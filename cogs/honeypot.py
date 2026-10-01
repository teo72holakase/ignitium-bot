"""
Honeypot: canal trampa anti-spam/scam.
Al detectar un mensaje de un no-admin:
  1. Borra TODOS los mensajes del miembro en TODOS los canales de texto del servidor (últimas 24h).
  2. Expulsa al miembro.
  3. Manda un aviso en el canal honeypot (se borra solo en 15s).
"""

import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import supabase, update_guild_config, run_query
from utils.permissions import admin_check
from utils.i18n import L, tr

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "honeypot.png")


def build_warning_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(
        title=tr(guild, "hp_title"),
        description=tr(guild, "hp_desc"),
        color=discord.Color.dark_gold(),
    )
    embed.set_thumbnail(url="attachment://honeypot.png")
    return embed


async def purge_member_messages(guild: discord.Guild, member: discord.Member, hours: int = 24):
    """
    Borra todos los mensajes del miembro en todos los canales de texto
    enviados en las últimas `hours` horas.
    Usa bulk_delete donde es posible (mensajes < 14 días) y delete() individual
    para los demás.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    for channel in guild.text_channels:
        try:
            # Recopilar mensajes del miembro en este canal
            to_delete: list[discord.Message] = []
            async for msg in channel.history(limit=500, after=cutoff):
                if msg.author.id == member.id:
                    to_delete.append(msg)

            if not to_delete:
                continue

            # bulk_delete solo acepta mensajes de menos de 14 días y en grupos de 2–100
            bulk_eligible   = [m for m in to_delete if (datetime.now(timezone.utc) - m.created_at).days < 14]
            single_eligible = [m for m in to_delete if m not in bulk_eligible]

            # Borrar en lotes de 100
            for i in range(0, len(bulk_eligible), 100):
                batch = bulk_eligible[i:i + 100]
                if len(batch) == 1:
                    single_eligible.append(batch[0])
                elif len(batch) > 1:
                    try:
                        await channel.delete_messages(batch)
                    except discord.HTTPException:
                        single_eligible.extend(batch)

            for msg in single_eligible:
                try:
                    await msg.delete()
                except discord.HTTPException:
                    pass

        except (discord.Forbidden, discord.HTTPException):
            continue


class Honeypot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="honeypot-setup", description=L("Creates (or reconfigures) the anti-scam trap channel"))
    @admin_check()
    @app_commands.describe(
        name=L("Tempting name for the channel (default: ・free-nitro)"),
        category=L("Category to create the channel in (optional)"),
    )
    async def honeypot_setup(
        self,
        interaction: discord.Interaction,
        name: str = "・free-nitro",
        category: discord.CategoryChannel = None,
    ):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            topic=tr(guild, "hp_topic"),
            reason=f"Honeypot set up by {interaction.user}",
        )

        embed = build_warning_embed(guild)
        if os.path.isfile(IMAGE_PATH):
            file = discord.File(IMAGE_PATH, filename="honeypot.png")
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(embed=embed)

        update_guild_config(guild.id, honeypot_channel_id=channel.id)

        await interaction.followup.send(tr(interaction, "hp_created", channel=channel.mention), ephemeral=True)

    @app_commands.command(name="honeypot-disable", description=L("Disables the honeypot (doesn't delete the channel)"))
    @admin_check()
    async def honeypot_disable(self, interaction: discord.Interaction):
        update_guild_config(interaction.guild.id, honeypot_channel_id=None)
        await interaction.response.send_message(tr(interaction, "hp_disabled"), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        result = await run_query(
            lambda: supabase.table("guild_config")
            .select("honeypot_channel_id")
            .eq("guild_id", message.guild.id)
            .execute()
        )
        if not result.data:
            return

        honeypot_id = result.data[0].get("honeypot_channel_id")
        if not honeypot_id or message.channel.id != honeypot_id:
            return

        member = message.author
        if not isinstance(member, discord.Member):
            return

        # Nunca tocar admins
        if member.guild_permissions.administrator:
            return

        guild = message.guild

        # 1. Borrar el mensaje del honeypot primero
        try:
            await message.delete()
        except discord.HTTPException:
            pass

        # 2. Borrar todos los mensajes recientes del miembro en todo el servidor (24h)
        await purge_member_messages(guild, member, hours=24)

        # 3. Expulsar
        try:
            await member.kick(reason="Wrote in the honeypot channel (bot/scam detected)")
        except discord.HTTPException:
            pass

        # 4. Aviso en el honeypot
        try:
            await message.channel.send(
                tr(guild, "hp_kicked", member=member),
                delete_after=15,
            )
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Honeypot(bot))