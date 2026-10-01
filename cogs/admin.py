"""
Comandos clásicos de administración/moderación + gestión de qué roles
cuentan como "staff/administración" para todo el bot (tickets, embeds, etc).
"""

from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import supabase, get_guild_config, update_guild_config
from utils.permissions import admin_check
from utils.i18n import L, tr


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- Gestión de roles de administración del bot ----------

    adminrole_group = app_commands.Group(name="adminrole", description=L("Configure which roles count as administration for the bot"))

    @adminrole_group.command(name="add", description=L("Adds a role recognized as 'administration' by the bot"))
    @admin_check()
    async def adminrole_add(self, interaction: discord.Interaction, role: discord.Role):
        config = get_guild_config(interaction.guild.id)
        ids = set(config.get("admin_role_ids") or [])
        ids.add(role.id)
        update_guild_config(interaction.guild.id, admin_role_ids=list(ids))
        await interaction.response.send_message(tr(interaction, "adminrole_added", role=role.mention), ephemeral=True)

    @adminrole_group.command(name="remove", description=L("Removes a role from the bot's administration list"))
    @admin_check()
    async def adminrole_remove(self, interaction: discord.Interaction, role: discord.Role):
        config = get_guild_config(interaction.guild.id)
        ids = set(config.get("admin_role_ids") or [])
        ids.discard(role.id)
        update_guild_config(interaction.guild.id, admin_role_ids=list(ids))
        await interaction.response.send_message(tr(interaction, "adminrole_removed", role=role.mention), ephemeral=True)

    @adminrole_group.command(name="list", description=L("Shows the roles recognized as administration"))
    @admin_check()
    async def adminrole_list(self, interaction: discord.Interaction):
        config = get_guild_config(interaction.guild.id)
        ids = config.get("admin_role_ids") or []
        if not ids:
            await interaction.response.send_message(tr(interaction, "adminrole_empty"), ephemeral=True)
            return
        mentions = ", ".join(f"<@&{i}>" for i in ids)
        await interaction.response.send_message(tr(interaction, "adminrole_list", roles=mentions), ephemeral=True)

    # ---------- Moderación básica ----------

    @app_commands.command(name="kick", description=L("Kicks a member from the server"))
    @admin_check()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = reason or tr(interaction, "reason_default")
        await member.kick(reason=reason)
        await interaction.response.send_message(tr(interaction, "kicked", member=member.mention, reason=reason))

    @app_commands.command(name="ban", description=L("Bans a member from the server"))
    @admin_check()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = reason or tr(interaction, "reason_default")
        await member.ban(reason=reason)
        await interaction.response.send_message(tr(interaction, "banned", member=member.mention, reason=reason))

    @app_commands.command(name="unban", description=L("Unbans a user by ID"))
    @admin_check()
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = discord.Object(id=int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(tr(interaction, "unbanned", user_id=user_id))

    @app_commands.command(name="mute", description=L("Mutes (timeouts) a member for X minutes"))
    @admin_check()
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = None):
        reason = reason or tr(interaction, "reason_default")
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(tr(interaction, "muted", member=member.mention, minutes=minutes, reason=reason))

    @app_commands.command(name="unmute", description=L("Removes a member's timeout"))
    @admin_check()
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(tr(interaction, "unmuted", member=member.mention))

    @app_commands.command(name="clear", description=L("Deletes a number of messages from the channel"))
    @admin_check()
    async def clear(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=count)
        await interaction.followup.send(tr(interaction, "cleared", count=len(deleted)), ephemeral=True)

    @app_commands.command(name="warn", description=L("Records a warning for a user"))
    @admin_check()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        supabase.table("warns").insert({
            "guild_id": interaction.guild.id,
            "user_id": member.id,
            "moderator_id": interaction.user.id,
            "reason": reason
        }).execute()
        await interaction.response.send_message(tr(interaction, "warned", member=member.mention, reason=reason))

    @app_commands.command(name="warns", description=L("Shows a user's warnings"))
    @admin_check()
    async def warns(self, interaction: discord.Interaction, member: discord.Member):
        rows = supabase.table("warns").select("*").eq("guild_id", interaction.guild.id).eq("user_id", member.id).execute().data or []
        if not rows:
            await interaction.response.send_message(tr(interaction, "no_warns", member=member.mention), ephemeral=True)
            return
        text = "\n".join(tr(interaction, "warns_row", id=r['id'], reason=r['reason'], mod=r['moderator_id']) for r in rows)
        await interaction.response.send_message(tr(interaction, "warns_header", member=member.mention, text=text), ephemeral=True)

    @app_commands.command(name="slowmode", description=L("Sets slowmode for the current channel (seconds)"))
    @admin_check()
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(tr(interaction, "slowmode_set", seconds=seconds), ephemeral=True)

    @app_commands.command(name="announce", description=L("Sends a formatted announcement to a channel"))
    @admin_check()
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        embed = discord.Embed(description=message, color=discord.Color.blurple())
        embed.set_author(name=tr(interaction, "announce_author", guild=interaction.guild.name), icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        await channel.send(embed=embed)
        await interaction.response.send_message(tr(interaction, "announce_sent", channel=channel.mention), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
