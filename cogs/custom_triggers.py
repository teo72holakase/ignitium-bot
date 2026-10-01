"""
- Triggers: cuando alguien escribe cierta palabra/frase, el bot responde automáticamente.
- Comandos personalizados: /nombre -> devuelve una respuesta configurada, con descripción propia.
  (Nota técnica: los slash commands de Discord requieren registrarse al iniciar el bot.
   Este cog registra los comandos custom guardados en Supabase como slash commands dinámicos
   al arrancar. Si agregás uno nuevo con /customcommand-add, se sincroniza al instante para ese server.)
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import supabase, run_query
from utils.permissions import admin_check
from utils.i18n import L, tr


class CustomTriggers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        await self.register_dynamic_commands()

    async def register_dynamic_commands(self):
        """Registra en el árbol de comandos todos los comandos custom guardados."""
        rows = supabase.table("custom_commands").select("*").execute().data or []
        for row in rows:
            self._add_dynamic_command(row)

    def _add_dynamic_command(self, row: dict):
        name = row["command_name"]
        response = row["response_text"]
        description = row.get("description") or "Custom command"

        if self.bot.tree.get_command(name):
            return  # ya existe, evitamos duplicados

        async def callback(interaction: discord.Interaction, _response=response):
            await interaction.response.send_message(_response)

        command = app_commands.Command(name=name, description=description, callback=callback)
        self.bot.tree.add_command(command)

    # ---------- Triggers de texto ----------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        rows = await run_query(
            lambda: supabase.table("custom_triggers").select("*").eq("guild_id", message.guild.id).execute()
        )
        rows = rows.data or []
        content_lower = message.content.lower()

        for row in rows:
            trigger = row["trigger_text"].lower()
            match_type = row.get("match_type", "contains")
            matched = (content_lower == trigger) if match_type == "exact" else (trigger in content_lower)
            if matched:
                await message.channel.send(row["response_text"])
                break  # solo dispara el primer trigger que coincida

    trigger_group = app_commands.Group(name="trigger", description=L("Manage automatic messages (triggers)"))

    @trigger_group.command(name="add", description=L("Creates a trigger: when a word is detected, the bot replies"))
    @admin_check()
    @app_commands.describe(
        word=L("Word or phrase that activates the trigger"),
        response=L("What the bot will reply"),
        match_type=L("Whether it must match exactly or just contain the word")
    )
    @app_commands.choices(match_type=[
        app_commands.Choice(name=L("Contains the word"), value="contains"),
        app_commands.Choice(name=L("Exact message"), value="exact"),
    ])
    async def trigger_add(self, interaction: discord.Interaction, word: str, response: str, match_type: app_commands.Choice[str] = None):
        supabase.table("custom_triggers").insert({
            "guild_id": interaction.guild.id,
            "trigger_text": word,
            "response_text": response,
            "match_type": match_type.value if match_type else "contains",
            "created_by": interaction.user.id
        }).execute()
        await interaction.response.send_message(tr(interaction, "trg_created", word=word), ephemeral=True)

    @trigger_group.command(name="list", description=L("Lists the configured triggers"))
    @admin_check()
    async def trigger_list(self, interaction: discord.Interaction):
        rows = supabase.table("custom_triggers").select("*").eq("guild_id", interaction.guild.id).execute().data or []
        if not rows:
            await interaction.response.send_message(tr(interaction, "trg_none"), ephemeral=True)
            return
        text = "\n".join(f"`{r['id']}` — **{r['trigger_text']}** ({r['match_type']}) → {r['response_text'][:50]}" for r in rows)
        await interaction.response.send_message(text, ephemeral=True)

    @trigger_group.command(name="remove", description=L("Deletes a trigger by ID (see /trigger list)"))
    @admin_check()
    async def trigger_remove(self, interaction: discord.Interaction, id: int):
        supabase.table("custom_triggers").delete().eq("id", id).eq("guild_id", interaction.guild.id).execute()
        await interaction.response.send_message(tr(interaction, "trg_removed"), ephemeral=True)

    # ---------- Comandos slash personalizados ----------

    command_group = app_commands.Group(name="customcommand", description=L("Manage custom slash commands"))

    @command_group.command(name="add", description=L("Creates a custom slash command (e.g. /rules)"))
    @admin_check()
    @app_commands.describe(
        name=L("Command name, no spaces or capitals (e.g. rules)"),
        response=L("Text the bot will send when the command is used"),
        description=L("Description shown in Discord when typing /")
    )
    async def command_add(self, interaction: discord.Interaction, name: str, response: str, description: str = "Custom command"):
        name = name.lower().replace(" ", "-")
        try:
            supabase.table("custom_commands").insert({
                "guild_id": interaction.guild.id,
                "command_name": name,
                "response_text": response,
                "description": description,
                "created_by": interaction.user.id
            }).execute()
        except Exception as e:
            await interaction.response.send_message(tr(interaction, "cmd_error", error=e), ephemeral=True)
            return

        self._add_dynamic_command({
            "command_name": name,
            "response_text": response,
            "description": description
        })
        await self.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(tr(interaction, "cmd_created", name=name), ephemeral=True)

    @command_group.command(name="remove", description=L("Deletes a custom slash command"))
    @admin_check()
    async def command_remove(self, interaction: discord.Interaction, name: str):
        name = name.lower().replace(" ", "-")
        supabase.table("custom_commands").delete().eq("guild_id", interaction.guild.id).eq("command_name", name).execute()
        self.bot.tree.remove_command(name)
        await self.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(tr(interaction, "cmd_removed", name=name), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CustomTriggers(bot))