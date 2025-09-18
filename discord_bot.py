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

# --- Dropdown setup ---
class CategorySelect(discord.ui.Select):
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
        courses = ", ".join(self.values)
        await interaction.response.send_message(
            f"📅 Date: **{self.date.strftime('%B %d, %Y')}**\n"
            f"🕒 Start: **{self.start_dt.strftime('%H:%M')}**\n"
            f"🕒 End: **{self.end_dt.strftime('%H:%M')}**\n"
            f"⛳️ Courses: **{courses}**",
            ephemeral=True
        )

class CategoryView(discord.ui.View):
    def __init__(self, date, start_dt, end_dt):
        super().__init__(timeout=60)
        self.add_item(CategorySelect(date, start_dt, end_dt))

# --- Slash command ---
@bot.tree.command(
    name="find",
    description="Find something by date, time range, and categories",
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
    end_time: str
):
    try:
        picked_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()

        start_dt = datetime.datetime.combine(picked_date, start)
        end_dt = datetime.datetime.combine(picked_date, end)

        view = CategoryView(picked_date, start_dt, end_dt)
        await interaction.response.send_message(
            "⛳️ Please choose one or more courses:",
            view=view,
            ephemeral=True
        )
    except ValueError:
        await interaction.response.send_message("⚠️ Use YYYY-MM-DD for date and HH:MM for times.")

# --- Bot startup ---
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user} and synced commands to guild {GUILD_ID}")

bot.run(TOKEN)

