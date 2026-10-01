import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.db import supabase, get_guild_config, update_guild_config, run_query
from utils.i18n import L, tr

MIEMBRO_ROLE_ID = 1521700111518924881
COUNTER_UPDATE_MINUTES = 10  # Discord limita renombrar canales ~2 veces cada 10 min


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_member_counter.start()

    def cog_unload(self):
        self.update_member_counter.cancel()

    @app_commands.command(name="ping", description=L("Shows the bot's latency"))
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(tr(interaction, "ping", ms=round(self.bot.latency * 1000)))

    @app_commands.command(name="counter-setup", description=L("Creates a voice channel that shows the member count in its name"))
    @app_commands.describe(category=L("Category to create the channel in (optional)"))
    async def contador_setup(self, interaction: discord.Interaction, category: discord.CategoryChannel = None):
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(tr(interaction, "no_manage_guild"), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        role = guild.get_role(MIEMBRO_ROLE_ID)
        count = len(role.members) if role else 0

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
        }
        channel = await guild.create_voice_channel(
            name=tr(guild, "counter_name", count=count),
            category=category,
            overwrites=overwrites,
            reason=f"Member counter channel created by {interaction.user}"
        )

        update_guild_config(guild.id, member_counter_channel_id=channel.id)

        await interaction.followup.send(
            tr(interaction, "counter_created", channel=channel.mention, minutes=COUNTER_UPDATE_MINUTES),
            ephemeral=True
        )

    @tasks.loop(minutes=COUNTER_UPDATE_MINUTES)
    async def update_member_counter(self):
        for guild in self.bot.guilds:
            try:
                config = await run_query(
                    lambda: supabase.table("guild_config").select("member_counter_channel_id").eq("guild_id", guild.id).execute()
                )
            except Exception:
                continue

            if not config.data:
                continue

            channel_id = config.data[0].get("member_counter_channel_id")
            if not channel_id:
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            role = guild.get_role(MIEMBRO_ROLE_ID)
            count = len(role.members) if role else 0
            nuevo_nombre = tr(guild, "counter_name", count=count)

            if channel.name != nuevo_nombre:
                try:
                    await channel.edit(name=nuevo_nombre, reason="Automatic member counter update")
                except discord.HTTPException:
                    pass  # rate limit de Discord u otro error transitorio; se reintenta en el próximo ciclo

    @update_member_counter.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="help", description=L("Shows info about the bot and its modules"))
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=tr(interaction, "help_title"),
            description=tr(interaction, "help_desc"),
            color=discord.Color.blurple()
        )
        embed.add_field(name="🎫 Tickets", value="`/ticket panel`, `/ticket add`, `/ticket remove`, `/ticket log-channel`", inline=False)
        embed.add_field(name=tr(interaction, "help_triggers"), value="`/trigger add`, `/trigger list`, `/trigger remove`, `/customcommand add`, `/customcommand remove`", inline=False)
        embed.add_field(name="🖼️ Embeds", value="`/embed-create`", inline=False)
        embed.add_field(name="🛡️ Antispam", value="`/antispam toggle`, `/antispam blacklist-add`, `/antispam blacklist-list`", inline=False)
        embed.add_field(name="🍯 Honeypot", value="`/honeypot-setup`, `/honeypot-disable`", inline=False)
        embed.add_field(name=tr(interaction, "help_giveaways"), value="`/giveaway`, `/giveaway-end`", inline=False)
        embed.add_field(name=tr(interaction, "help_roles"), value="`/reactionrole add`, `/joinrole add`, `/joinrole remove`", inline=False)
        embed.add_field(name=tr(interaction, "help_admin"), value="`/kick`, `/ban`, `/unban`, `/mute`, `/unmute`, `/clear`, `/warn`, `/warns`, `/slowmode`, `/announce`, `/adminrole add`", inline=False)
        embed.add_field(name=tr(interaction, "help_counter"), value="`/counter-setup`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))