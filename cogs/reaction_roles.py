"""
- Reaction roles: reaccionar con un emoji en un mensaje da/quita un rol.
- Join roles: rol(es) que se asignan automáticamente al entrar al server.
"""

import discord
import asyncio
from discord import app_commands
from discord.ext import commands

from utils.db import supabase, get_guild_config, update_guild_config, run_query
from utils.permissions import admin_check
from utils.i18n import L, tr


class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- Join roles ----------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        config = await asyncio.to_thread(get_guild_config, member.guild.id)
        role_ids = config.get("join_role_ids") or []
        for role_id in role_ids:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Automatic join role")
                except discord.HTTPException:
                    pass

    joinrole_group = app_commands.Group(name="joinrole", description=L("Automatic roles when joining the server"))

    @joinrole_group.command(name="add", description=L("Adds a role given automatically to new members"))
    @admin_check()
    async def joinrole_add(self, interaction: discord.Interaction, role: discord.Role):
        config = get_guild_config(interaction.guild.id)
        role_ids = set(config.get("join_role_ids") or [])
        role_ids.add(role.id)
        update_guild_config(interaction.guild.id, join_role_ids=list(role_ids))
        await interaction.response.send_message(tr(interaction, "jr_added", role=role.mention), ephemeral=True)

    @joinrole_group.command(name="remove", description=L("Removes a role from the join-roles list"))
    @admin_check()
    async def joinrole_remove(self, interaction: discord.Interaction, role: discord.Role):
        config = get_guild_config(interaction.guild.id)
        role_ids = set(config.get("join_role_ids") or [])
        role_ids.discard(role.id)
        update_guild_config(interaction.guild.id, join_role_ids=list(role_ids))
        await interaction.response.send_message(tr(interaction, "jr_removed", role=role.mention), ephemeral=True)

    # ---------- Reaction roles ----------

    reactionrole_group = app_commands.Group(name="reactionrole", description=L("Reaction roles"))

    @reactionrole_group.command(name="add", description=L("Links a message emoji to a role"))
    @admin_check()
    @app_commands.describe(
        message_id=L("Message ID (right click -> Copy ID, needs developer mode)"),
        emoji=L("The emoji to use (must exist on the server or be a standard Discord one)"),
        role=L("Role granted when reacting")
    )
    async def reactionrole_add(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        try:
            message_id = int(message_id)
        except ValueError:
            await interaction.response.send_message(tr(interaction, "rr_bad_id"), ephemeral=True)
            return

        message = None
        for channel in interaction.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id)
                break
            except (discord.NotFound, discord.Forbidden):
                continue

        if not message:
            await interaction.response.send_message(tr(interaction, "rr_not_found"), ephemeral=True)
            return

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            await interaction.response.send_message(tr(interaction, "rr_bad_emoji"), ephemeral=True)
            return

        supabase.table("reaction_roles").insert({
            "guild_id": interaction.guild.id,
            "channel_id": message.channel.id,
            "message_id": message.id,
            "emoji": emoji,
            "role_id": role.id
        }).execute()

        await interaction.response.send_message(tr(interaction, "rr_added", emoji=emoji, role=role.mention), ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member and payload.member.bot:
            return
        await self._handle_reaction(payload, add=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self._handle_reaction(payload, add=False)

    async def _handle_reaction(self, payload: discord.RawReactionActionEvent, add: bool):
        emoji_str = str(payload.emoji)
        result = await run_query(
            lambda: supabase.table("reaction_roles").select("*")
                .eq("message_id", payload.message_id).eq("emoji", emoji_str).execute()
        )
        rows = result.data
        if not rows:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        role = guild.get_role(rows[0]["role_id"])
        member = guild.get_member(payload.user_id)
        if not role or not member or member.bot:
            return

        try:
            if add:
                await member.add_roles(role, reason="Reaction role")
            else:
                await member.remove_roles(role, reason="Reaction role removed")
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))