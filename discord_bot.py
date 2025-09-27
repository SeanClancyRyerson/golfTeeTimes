import private as pvt
import const as const
import tee_times as tee
import helpers as hlpr

import discord
from discord import app_commands
from discord.ext import commands
import datetime
import time
import asyncio

#Bot setup stuff
TOKEN = pvt.discord_bot_token
GUILD_ID = 1161391779845783782 #niccy's server

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix=None)

#setup job tracking
active_jobs = {}

#Loop for finding tee times and calling the tee_times functions
async def finder_loop(job, date, start_time, end_time, players, courses, user, loop_end):
    #slightly hacky use of try-finally, but prevents repeated code, or creating a function just for removing the job
    try:
        while True:
            all_times = []
            for course in courses:
                course_key = getattr(const, const.COURSES_DICT[course])
                all_times += tee.get_tee_times(course_key, date)
            filtered_tee_times = tee.get_filtered_tee_times(all_times, start_time, end_time, players)
            if len(filtered_tee_times) == 0:
                if datetime.datetime.now() > loop_end:
                    await user.send("No tee times found before end time. Stopping search.")
                    hlpr.console_log(f"No tee times found before end time for {str(user.name)}. Stopping search.")

                    break
                sleep_time_seconds = hlpr.get_wait_time(1,5)
                hlpr.console_log(f"No good tee times found for {str(user.name)}. Sleeping for {(sleep_time_seconds/60):.1f} minutes")
                await asyncio.sleep(sleep_time_seconds)
            else:
                '''
                Limited this to top 10 because discord has a 2000 char limit per message
                This isn't great because if you're searching for times across all courses
                you might not see the best times for each course. Maybe create a way to break
                it up by course and send multiple messages?
                '''
                if len(filtered_tee_times) > 10:
                    filtered_tee_times = filtered_tee_times[:10] #limit to 10 results to avoid spam
                await user.send(
                    f"Found {len(filtered_tee_times)} available tee times. Showing first 10 available:\n"
                    f"{tee.tee_times_to_string(filtered_tee_times)}")
                break
    finally:
        # cleanup job when loop finishes
        if user.id in active_jobs and job in active_jobs[user.id]:
            active_jobs[user.id].remove(job)
            hlpr.console_log(f"Removed job for {str(user.name)}.")
            # remove user entry if no jobs left
            if not active_jobs[user.id]:
                del active_jobs[user.id]
                hlpr.console_log(f"No active jobs left for {str(user.name)}. Removed user from active_jobs.")


#Dropdown setup
class CourseSelect(discord.ui.Select):#
    def __init__(self, date, start_dt, end_dt):
        options = []
        for course in const.foreUp_mappings.keys():
            options.append(discord.SelectOption(label=course, value=course))

        super().__init__(
            placeholder="Select one or more courses...",
            min_values=1,
            max_values=len(options),
            options=options
        )
        self.date = date
        self.start_dt = start_dt
        self.end_dt = end_dt

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_courses = self.values
        await interaction.response.send_message("Received.")
        self.view.stop()

class CourseView(discord.ui.View):
    def __init__(self, date, start_dt, end_dt):
        super().__init__(timeout=60)
        self.add_item(CourseSelect(date, start_dt, end_dt))
        self.selected_courses: list[str] = []

# --- Slash command ---
@bot.tree.command(
    name="find",
    description="Find golf tee times",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    date="Enter a date (YYYY-MM-DD)",
    start_time="Enter start time (HH:MM, 24h)",
    end_time="Enter end time (HH:MM, 24h)"
)
async def find(
    interaction: discord.Interaction,
    date: str,
    start_time: str,
    end_time: str,
    players: int
):
    #Initial Command inputs
    try:
        picked_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()

        start_dt = datetime.datetime.combine(picked_date, start)
        end_dt = datetime.datetime.combine(picked_date, end)
    except ValueError:
        await interaction.response.send_message("⚠️ Use YYYY-MM-DD for date and HH:MM for times.")

    #data quality checks, you'd hope the user was smart enough :D
    if start_dt <= datetime.datetime.now() or end_dt <= datetime.datetime.now():
        await interaction.response.send_message("⚠️ Start and end time must be in the future.")
        return
    
    if end_dt <= start_dt:
        await interaction.response.send_message("⚠️ End time must be after start time.")
        return
    
    if players < 1 or players > 4:
        await interaction.response.send_message("⚠️ Players must be between 1 and 4.")
        return
    
    #Creating a drop down view for course selection
    view = CourseView(picked_date, start_dt, end_dt)
    await interaction.response.send_message(
        "⛳️ Please choose one or more courses:",
        view=view,
        ephemeral=True
        )
    
    #Make sure user chooses courses or 60s timeout
    timeout = await view.wait()

    #get courses selected
    courses = view.selected_courses
    if courses:
        await interaction.followup.send(
            f"📅 Date: **{picked_date.strftime('%B %d, %Y')}**\n"
            f"🕒 Start: **{start_dt.strftime('%H:%M')}**\n"
            f"🕒 End: **{end_dt.strftime('%H:%M')}**\n"
            f"⛳️ Courses: **{', '.join(courses)}**\n"
            f"👥 Players: **{players}**\n"
            f"🔎 Searching for available tee times...",
            ephemeral=True # ephemeral so only the user who sent the command sees it
        )

        #Format date for compatibility with tee_times functions
        find_date = [picked_date.strftime('%m-%d-%Y')]

        #Store jobs by user id
        if interaction.user.id not in active_jobs:
            active_jobs[interaction.user.id] = []

        job = {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "courses": courses,
            "task": None  # will be set below
        }
        job["task"] = bot.loop.create_task(
            #pass the job object to the loop so the loop can track itself and remove itself when done
            finder_loop(job, find_date, start, end, players, courses, interaction.user, end_dt)
        )

        active_jobs[interaction.user.id].append(job)
        
    else:
        await interaction.followup.send(
            "⚠️ You didn't select any categories in time.",
            ephemeral=True
        ) 

@bot.tree.command(
    name="report",
    description="Show all currently running tee time search jobs",
    guild=discord.Object(id=GUILD_ID)
)
async def report(interaction: discord.Interaction):
    if not active_jobs:
        await interaction.response.send_message("✅ No active jobs running.", ephemeral=True)
        return

    lines = []
    for user_id, jobs in active_jobs.items():
        user = await bot.fetch_user(user_id)  # fetch full user object
        lines.append(f"👤 **{user.name}#{user.discriminator}** ({user_id})")

        for i, job in enumerate(jobs, start=1):
            lines.append(
                f"   └─ Job {i}: "
                f"📅 {job['date']} | "
                f"🕒 {job['start_time']} - {job['end_time']} | "
                f"⛳️ {', '.join(job['courses'])}"
            )

    report_text = "\n".join(lines)

    # Discord messages are limited to 2000 chars, so chunk if necessary
    if len(report_text) > 2000:
        chunks = [report_text[i:i+1900] for i in range(0, len(report_text), 1900)]
        await interaction.response.send_message(chunks[0], ephemeral=True)
        for chunk in chunks[1:]:
            await interaction.followup.send(chunk, ephemeral=True)
    else:
        await interaction.response.send_message(report_text, ephemeral=True)

@bot.tree.command(
    name="cancel",
    description="Cancel a running tee time search job",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    user_id="(Admins only) The user whose job you want to cancel. Leave blank to cancel your own.",
    job_id="The job number to cancel (see /report for IDs)"
)
async def cancel(
    interaction: discord.Interaction,
    job_id: int,
    user_id: int = None  # optional, only usable by OWNER_ID
):
    target_user_id = user_id or interaction.user.id
    admin_ids = ['188108217677643785'] #niccy
    # Permission check: only OWNER_ID can cancel other users' jobs
    if target_user_id != interaction.user.id and interaction.user.id not in admin_ids:
        await interaction.response.send_message(
            "⚠️ You can only cancel your own jobs.", ephemeral=True
        )
        return

    user_jobs = active_jobs.get(target_user_id, [])

    if not user_jobs:
        await interaction.response.send_message("⚠️ No active jobs found for this user.", ephemeral=True)
        return

    if job_id < 1 or job_id > len(user_jobs):
        await interaction.response.send_message(
            f"⚠️ Invalid job ID. This user has {len(user_jobs)} active jobs.", ephemeral=True
        )
        return

    job_to_cancel = user_jobs[job_id - 1]

    # Cancel the asyncio task
    if job_to_cancel["task"]:
        job_to_cancel["task"].cancel()

    # Remove job from active_jobs
    user_jobs.pop(job_id - 1)
    if not user_jobs:
        del active_jobs[target_user_id]

    await interaction.response.send_message(
        f"✅ Cancelled job {job_id} for user {target_user_id}.", ephemeral=True
    )

# --- Bot startup ---
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user} and synced commands to guild {GUILD_ID}")

bot.run(TOKEN)

