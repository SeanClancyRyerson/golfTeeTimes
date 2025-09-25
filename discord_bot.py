import private as pvt
import const as const

import discord
from discord import app_commands
from discord.ext import commands
import datetime

TOKEN = pvt.discord_bot_token
GUILD_ID = 1161391779845783782 #niccy's server

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix=None)

#Dropdown setup
class CourseSelect(discord.ui.Select):
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
            f"👥 Players: **{players}**",
            ephemeral=True # ephemeral so only the user who sent the command sees it
        )
    else:
        await interaction.followup.send(
            "⚠️ You didn’t select any categories in time.",
            ephemeral=True
        )

# --- Bot startup ---
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user} and synced commands to guild {GUILD_ID}")

bot.run(TOKEN)

