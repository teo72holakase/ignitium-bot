"""
Sistema de tickets estilo bots populares (Ticket Tool / Tickets++):
- /ticket-panel : crea un panel con botón para abrir tickets
- Botón "Abrir Ticket" -> crea canal privado, agrega roles de soporte
- Dentro del ticket: botones de Reclamar, Cerrar, y comando para agregar/quitar usuarios
- Guarda todo en Supabase (tabla ticket_panels y tickets)
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import supabase, get_guild_config
from utils.permissions import admin_check, is_admin
from utils.i18n import L, tr


def make_ticket_embed(panel: dict, ctx=None) -> discord.Embed:
    color = discord.Color.from_str(panel.get("embed_color") or "#2b2d31")
    embed = discord.Embed(
        title=panel.get("embed_title") or tr(ctx, "tk_default_title"),
        description=panel.get("embed_description") or tr(ctx, "tk_default_desc"),
        color=color
    )
    return embed


class TicketOpenView(discord.ui.View):
    """Vista persistente del botón para abrir tickets (vive en el panel)."""

    def __init__(self, panel_id: int, button_label: str):
        super().__init__(timeout=None)
        self.panel_id = panel_id
        button = discord.ui.Button(
            label=button_label,
            style=discord.ButtonStyle.primary,
            emoji="🎫",
            custom_id=f"ticket_open:{panel_id}"
        )
        button.callback = self.open_ticket
        self.add_item(button)

    async def open_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        panel_res = supabase.table("ticket_panels").select("*").eq("id", self.panel_id).execute()
        if not panel_res.data:
            await interaction.response.send_message(tr(interaction, "tk_gone"), ephemeral=True)
            return
        panel = panel_res.data[0]

        # Evitar tickets duplicados del mismo usuario en el mismo panel
        existing = supabase.table("tickets").select("*") \
            .eq("guild_id", guild.id).eq("user_id", interaction.user.id) \
            .eq("panel_id", self.panel_id).eq("status", "open").execute()
        if existing.data:
            channel = guild.get_channel(existing.data[0]["channel_id"])
            if channel:
                await interaction.response.send_message(
                    tr(interaction, "tk_exists", channel=channel.mention), ephemeral=True
                )
                return

        await interaction.response.defer(ephemeral=True)

        category = guild.get_channel(panel["category_id"]) if panel.get("category_id") else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        for role_id in (panel.get("support_role_ids") or []):
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-")[:90]
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket opened by {interaction.user}"
        )

        supabase.table("tickets").insert({
            "guild_id": guild.id,
            "channel_id": ticket_channel.id,
            "user_id": interaction.user.id,
            "panel_id": self.panel_id,
            "status": "open"
        }).execute()

        embed = discord.Embed(
            title=tr(interaction, "tk_open_title"),
            description=tr(interaction, "tk_open_desc", user=interaction.user.mention),
            color=discord.Color.blurple()
        )
        await ticket_channel.send(embed=embed, view=TicketManageView(interaction))
        await interaction.followup.send(tr(interaction, "tk_created", channel=ticket_channel.mention), ephemeral=True)


class TicketManageView(discord.ui.View):
    """Botones dentro del channel de ticket: Reclamar y Cerrar."""

    def __init__(self, ctx=None):
        super().__init__(timeout=None)
        # Las etiquetas se fijan al enviar el mensaje, en el idioma de quien abre el ticket
        self.claim.label = tr(ctx, "tk_btn_claim")
        self.close.label = tr(ctx, "tk_btn_close")

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.secondary, emoji="🙋", custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(tr(interaction, "tk_staff_only"), ephemeral=True)
            return
        supabase.table("tickets").update({"status": "claimed", "claimed_by": interaction.user.id}) \
            .eq("channel_id", interaction.channel.id).execute()
        await interaction.response.send_message(tr(interaction, "tk_claimed", user=interaction.user.mention))

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_res = supabase.table("tickets").select("*").eq("channel_id", interaction.channel.id).execute()
        if not ticket_res.data:
            await interaction.response.send_message(tr(interaction, "tk_not_ticket"), ephemeral=True)
            return

        ticket = ticket_res.data[0]
        is_owner = interaction.user.id == ticket["user_id"]
        if not is_owner and not (isinstance(interaction.user, discord.Member) and is_admin(interaction.user)):
            await interaction.response.send_message(tr(interaction, "tk_no_close"), ephemeral=True)
            return

        await interaction.response.send_message(tr(interaction, "tk_closing"))
        supabase.table("tickets").update({"status": "closed"}).eq("channel_id", interaction.channel.id).execute()

        config = get_guild_config(interaction.guild.id)
        log_channel_id = config.get("ticket_log_channel_id")
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title=tr(interaction.guild, "tk_log_title"),
                    description=tr(interaction.guild, "tk_log_desc", channel=interaction.channel.name, user=interaction.user.mention),
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket closed")


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Re-registra las vistas persistentes de paneles existentes al reiniciar el bot
        try:
            panels = supabase.table("ticket_panels").select("*").execute().data or []
            for panel in panels:
                self.bot.add_view(TicketOpenView(panel["id"], panel.get("button_label") or "Open Ticket"))
            self.bot.add_view(TicketManageView())
        except Exception:
            pass

    group = app_commands.Group(name="ticket", description=L("Manage the ticket system"))

    @group.command(name="panel", description=L("Creates a ticket panel in this channel"))
    @admin_check()
    @app_commands.describe(
        title=L("Title of the panel embed"),
        description=L("Embed description"),
        button=L("Text of the button that opens a ticket"),
        category=L("Category where ticket channels will be created"),
        color=L("Hex color, e.g. #5865F2"),
        support_role=L("Role that can see and answer tickets")
    )
    async def panel(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        button: str = None,
        category: discord.CategoryChannel = None,
        color: str = "#2b2d31",
        support_role: discord.Role = None
    ):
        button = button or tr(interaction.guild, "tk_default_button")
        support_role_ids = [support_role.id] if support_role else []

        insert_res = supabase.table("ticket_panels").insert({
            "guild_id": interaction.guild.id,
            "panel_name": title,
            "channel_id": interaction.channel.id,
            "embed_title": title,
            "embed_description": description,
            "embed_color": color,
            "button_label": button,
            "category_id": category.id if category else None,
            "support_role_ids": support_role_ids
        }).execute()

        panel = insert_res.data[0]
        embed = make_ticket_embed(panel, interaction.guild)
        view = TicketOpenView(panel["id"], button)

        await interaction.response.send_message(tr(interaction, "tk_panel_created"), ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=view)

        supabase.table("ticket_panels").update({"message_id": msg.id}).eq("id", panel["id"]).execute()

    @group.command(name="add", description=L("Adds a user to the current ticket"))
    @admin_check()
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True)
        await interaction.response.send_message(tr(interaction, "tk_user_added", user=user.mention))

    @group.command(name="remove", description=L("Removes a user from the current ticket"))
    @admin_check()
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(tr(interaction, "tk_user_removed", user=user.mention))

    @group.command(name="log-channel", description=L("Sets the channel where ticket closures are logged"))
    @admin_check()
    async def log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        supabase.table("guild_config").upsert({
            "guild_id": interaction.guild.id,
            "ticket_log_channel_id": channel.id
        }).execute()
        await interaction.response.send_message(tr(interaction, "tk_log_set", channel=channel.mention), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
