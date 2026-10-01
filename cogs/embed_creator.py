"""
Embed Creator interactivo: /embed-create abre un panel con botones para
configurar título, descripción, color, imagen, thumbnail, footer, autor
y hasta 3 campos (name/value/inline). Al final se envía al canal elegido.
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.permissions import admin_check
from utils.i18n import L, tr


class EmbedState:
    """Guarda el estado del embed que se está armando en memoria mientras el usuario lo edita."""
    def __init__(self):
        self.title = None
        self.description = None
        self.color = discord.Color.blurple()
        self.image_url = None
        self.thumbnail_url = None
        self.footer_text = None
        self.footer_icon = None
        self.author_name = None
        self.author_icon = None
        self.fields = []  # lista de dicts: {name, value, inline}

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )
        if self.image_url:
            embed.set_image(url=self.image_url)
        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)
        if self.footer_text:
            embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        if self.author_name:
            embed.set_author(name=self.author_name, icon_url=self.author_icon)
        for f in self.fields:
            embed.add_field(name=f["name"], value=f["value"], inline=f["inline"])
        return embed


class BasicInfoModal(discord.ui.Modal):
    def __init__(self, state: EmbedState, parent_view: "EmbedBuilderView", ctx=None):
        super().__init__(title=tr(ctx, "em_modal_basic"))
        self.state = state
        self.parent_view = parent_view
        self.titulo = discord.ui.TextInput(label=tr(ctx, "em_title"), required=False, max_length=256, default=state.title or "")
        self.descripcion = discord.ui.TextInput(
            label=tr(ctx, "em_desc"), style=discord.TextStyle.paragraph, required=False, max_length=4000,
            default=state.description or ""
        )
        self.color_hex = discord.ui.TextInput(label=tr(ctx, "em_color"), required=False, max_length=7)
        self.add_item(self.titulo)
        self.add_item(self.descripcion)
        self.add_item(self.color_hex)

    async def on_submit(self, interaction: discord.Interaction):
        self.state.title = self.titulo.value or None
        self.state.description = self.descripcion.value or None
        if self.color_hex.value:
            try:
                self.state.color = discord.Color.from_str(self.color_hex.value)
            except ValueError:
                pass
        await self.parent_view.refresh(interaction)


class ImagesModal(discord.ui.Modal):
    def __init__(self, state: EmbedState, parent_view: "EmbedBuilderView", ctx=None):
        super().__init__(title=tr(ctx, "em_modal_images"))
        self.state = state
        self.parent_view = parent_view
        self.imagen = discord.ui.TextInput(label=tr(ctx, "em_image"), required=False, default=state.image_url or "")
        self.thumb = discord.ui.TextInput(label=tr(ctx, "em_thumb"), required=False, default=state.thumbnail_url or "")
        self.add_item(self.imagen)
        self.add_item(self.thumb)

    async def on_submit(self, interaction: discord.Interaction):
        self.state.image_url = self.imagen.value or None
        self.state.thumbnail_url = self.thumb.value or None
        await self.parent_view.refresh(interaction)


class FooterAuthorModal(discord.ui.Modal):
    def __init__(self, state: EmbedState, parent_view: "EmbedBuilderView", ctx=None):
        super().__init__(title=tr(ctx, "em_modal_footer"))
        self.state = state
        self.parent_view = parent_view
        self.footer_text = discord.ui.TextInput(label=tr(ctx, "em_footer_text"), required=False, default=state.footer_text or "")
        self.footer_icon = discord.ui.TextInput(label=tr(ctx, "em_footer_icon"), required=False, default=state.footer_icon or "")
        self.author_name = discord.ui.TextInput(label=tr(ctx, "em_author_name"), required=False, default=state.author_name or "")
        self.author_icon = discord.ui.TextInput(label=tr(ctx, "em_author_icon"), required=False, default=state.author_icon or "")
        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)
        self.add_item(self.author_name)
        self.add_item(self.author_icon)

    async def on_submit(self, interaction: discord.Interaction):
        self.state.footer_text = self.footer_text.value or None
        self.state.footer_icon = self.footer_icon.value or None
        self.state.author_name = self.author_name.value or None
        self.state.author_icon = self.author_icon.value or None
        await self.parent_view.refresh(interaction)


class AddFieldModal(discord.ui.Modal):
    def __init__(self, state: EmbedState, parent_view: "EmbedBuilderView", ctx=None):
        super().__init__(title=tr(ctx, "em_modal_field"))
        self.state = state
        self.parent_view = parent_view
        self.name = discord.ui.TextInput(label=tr(ctx, "em_field_name"), max_length=256)
        self.value = discord.ui.TextInput(label=tr(ctx, "em_field_value"), style=discord.TextStyle.paragraph, max_length=1024)
        self.inline = discord.ui.TextInput(label=tr(ctx, "em_field_inline"), default=tr(ctx, "em_inline_default"), max_length=3)
        self.add_item(self.name)
        self.add_item(self.value)
        self.add_item(self.inline)

    async def on_submit(self, interaction: discord.Interaction):
        if len(self.state.fields) >= 25:
            await interaction.response.send_message(tr(interaction, "em_max_fields"), ephemeral=True)
            return
        self.state.fields.append({
            "name": self.name.value,
            "value": self.value.value,
            "inline": self.inline.value.strip().lower() in ("si", "sí", "sim", "s", "yes", "y", "true")
        })
        await self.parent_view.refresh(interaction)


class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent_view: "EmbedBuilderView", ctx=None):
        super().__init__(placeholder=tr(ctx, "em_pick_channel"), channel_types=[discord.ChannelType.text])
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.values[0].id)
        if channel is None:
            await interaction.response.edit_message(
                content=tr(interaction, "em_no_access"),
                embed=None, view=None
            )
            return
        embed = self.parent_view.state.build()
        await channel.send(embed=embed)
        await interaction.response.edit_message(content=tr(interaction, "em_sent", channel=channel.mention), embed=None, view=None)


class EmbedBuilderView(discord.ui.View):
    def __init__(self, state: EmbedState, ctx=None):
        super().__init__(timeout=600)
        self.state = state
        # Etiquetas de los botones en el idioma del usuario que abrió el creador
        self.basic_info.label = tr(ctx, "em_btn_basic")
        self.images.label = tr(ctx, "em_btn_images")
        self.footer_author.label = tr(ctx, "em_btn_footer")
        self.add_field.label = tr(ctx, "em_btn_addfield")
        self.remove_field.label = tr(ctx, "em_btn_rmfield")
        self.send_embed.label = tr(ctx, "em_btn_send")
        self.cancel.label = tr(ctx, "em_btn_cancel")

    async def refresh(self, interaction: discord.Interaction):
        embed = self.state.build()
        if not embed.title and not embed.description and not self.state.fields:
            embed.description = tr(interaction, "em_empty_preview")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Title / Description / Color", style=discord.ButtonStyle.primary, row=0)
    async def basic_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BasicInfoModal(self.state, self, interaction))

    @discord.ui.button(label="Images", style=discord.ButtonStyle.primary, row=0)
    async def images(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ImagesModal(self.state, self, interaction))

    @discord.ui.button(label="Footer / Author", style=discord.ButtonStyle.primary, row=0)
    async def footer_author(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FooterAuthorModal(self.state, self, interaction))

    @discord.ui.button(label="➕ Add field", style=discord.ButtonStyle.secondary, row=1)
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddFieldModal(self.state, self, interaction))

    @discord.ui.button(label="🗑️ Remove last field", style=discord.ButtonStyle.secondary, row=1)
    async def remove_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.state.fields:
            self.state.fields.pop()
        await self.refresh(interaction)

    @discord.ui.button(label="📤 Send embed", style=discord.ButtonStyle.success, row=2)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=120)
        view.add_item(ChannelSelect(self, interaction))
        await interaction.response.send_message(tr(interaction, "em_ask_channel"), view=view, ephemeral=True)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger, row=2)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=tr(interaction, "em_cancelled"), embed=None, view=None)


class EmbedCreator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="embed-create", description=L("Opens the interactive embed creator"))
    @admin_check()
    async def embed_create(self, interaction: discord.Interaction):
        state = EmbedState()
        view = EmbedBuilderView(state, interaction)
        preview = discord.Embed(description=tr(interaction, "em_empty_preview"), color=discord.Color.blurple())
        await interaction.response.send_message(embed=preview, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedCreator(bot))