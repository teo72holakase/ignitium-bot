"""
Traducciones del bot: inglés (por defecto), español y portugués de Brasil.

- tr(ctx, "clave", **datos): devuelve el texto en el idioma de `ctx`.
    * Interaction -> idioma del cliente de Discord del usuario (interaction.locale)
    * Guild / Message -> idioma preferido del servidor (guild.preferred_locale)
    * cualquier otro idioma -> inglés
- L("texto en inglés"): marca descripciones de comandos/parámetros para que
  IngnitiumTranslator las localice en la lista de comandos de Discord.
"""

import discord
from discord import app_commands
from discord.app_commands import locale_str as L  # noqa: F401  (se importa desde los cogs)

EN, ES, PT = 0, 1, 2


def lang_index(ctx) -> int:
    """Devuelve 0 (en), 1 (es) o 2 (pt) según el locale del contexto."""
    code = ""
    if isinstance(ctx, (str, discord.Locale)):
        code = str(getattr(ctx, "value", ctx))
    elif ctx is not None:
        for attr in ("locale", "preferred_locale"):
            value = getattr(ctx, attr, None)
            if value is not None:
                code = str(getattr(value, "value", value))
                break
        else:
            guild = getattr(ctx, "guild", None)
            if guild is not None:
                code = str(getattr(guild.preferred_locale, "value", guild.preferred_locale))
    code = code.lower()
    if code.startswith("es"):
        return ES
    if code.startswith("pt"):
        return PT
    return EN


# clave: (English, Español, Português-BR)
MESSAGES = {
    # ---- genéricos ----
    "no_admin": (
        "❌ You don't have admin permissions to use this.",
        "❌ No tenés permisos de administración para usar esto.",
        "❌ Você não tem permissões de administração para usar isso.",
    ),
    "no_manage_guild": (
        "❌ You need the 'Manage Server' permission to use this.",
        "❌ Necesitás el permiso 'Gestionar servidor' para usar esto.",
        "❌ Você precisa da permissão 'Gerenciar servidor' para usar isso.",
    ),
    "reason_default": ("Not specified", "No especificada", "Não especificado"),

    # ---- general ----
    "ping": ("🏓 Pong! {ms}ms", "🏓 Pong! {ms}ms", "🏓 Pong! {ms}ms"),
    "counter_created": (
        "✅ Counter channel created: {channel}\nIt updates automatically every {minutes} minutes (Discord's own limit for renaming channels).",
        "✅ Canal contador creado: {channel}\nSe actualiza solo cada {minutes} minutos (límite propio de Discord para renombrar canales).",
        "✅ Canal contador criado: {channel}\nEle é atualizado sozinho a cada {minutes} minutos (limite do próprio Discord para renomear canais).",
    ),
    "counter_name": ("👥 Members: {count}", "👥 Miembros: {count}", "👥 Membros: {count}"),
    "help_title": ("📖 Ingnitium Help", "📖 Ayuda de Ingnitium", "📖 Ajuda do Ingnitium"),
    "help_desc": (
        "Commands grouped by module. Type `/` in chat to see each one's description.",
        "Comandos organizados por módulo. Usá `/` en el chat para ver la descripción de cada uno.",
        "Comandos organizados por módulo. Digite `/` no chat para ver a descrição de cada um.",
    ),
    "help_triggers": ("💬 Triggers & commands", "💬 Triggers y comandos", "💬 Triggers e comandos"),
    "help_giveaways": ("🎉 Giveaways", "🎉 Sorteos", "🎉 Sorteios"),
    "help_roles": ("🎭 Roles", "🎭 Roles", "🎭 Cargos"),
    "help_admin": ("🔨 Administration", "🔨 Administración", "🔨 Administração"),
    "help_counter": ("👥 Counter", "👥 Contador", "👥 Contador"),

    # ---- admin ----
    "adminrole_added": (
        "✅ {role} is now recognized as administration.",
        "✅ {role} ahora es reconocido como administración.",
        "✅ {role} agora é reconhecido como administração.",
    ),
    "adminrole_removed": (
        "✅ {role} is no longer recognized as administration.",
        "✅ {role} ya no es reconocido como administración.",
        "✅ {role} não é mais reconhecido como administração.",
    ),
    "adminrole_empty": (
        "No admin roles configured (only Discord's native permission applies).",
        "No hay roles de administración configurados (solo el permiso nativo de Discord aplica).",
        "Nenhum cargo de administração configurado (só vale a permissão nativa do Discord).",
    ),
    "adminrole_list": ("Admin roles: {roles}", "Roles de administración: {roles}", "Cargos de administração: {roles}"),
    "kicked": (
        "👢 {member} was kicked. Reason: {reason}",
        "👢 {member} fue expulsado. Razón: {reason}",
        "👢 {member} foi expulso. Motivo: {reason}",
    ),
    "banned": (
        "🔨 {member} was banned. Reason: {reason}",
        "🔨 {member} fue baneado. Razón: {reason}",
        "🔨 {member} foi banido. Motivo: {reason}",
    ),
    "unbanned": (
        "✅ User with ID `{user_id}` was unbanned.",
        "✅ Usuario con ID `{user_id}` desbaneado.",
        "✅ Usuário com ID `{user_id}` desbanido.",
    ),
    "muted": (
        "🔇 {member} muted for {minutes} minutes. Reason: {reason}",
        "🔇 {member} silenciado por {minutes} minutos. Razón: {reason}",
        "🔇 {member} silenciado por {minutes} minutos. Motivo: {reason}",
    ),
    "unmuted": (
        "🔊 {member} is no longer muted.",
        "🔊 {member} ya no está silenciado.",
        "🔊 {member} não está mais silenciado.",
    ),
    "cleared": ("🧹 {count} messages deleted.", "🧹 {count} mensajes eliminados.", "🧹 {count} mensagens apagadas."),
    "warned": (
        "⚠️ {member} was warned. Reason: {reason}",
        "⚠️ {member} advertido. Razón: {reason}",
        "⚠️ {member} advertido. Motivo: {reason}",
    ),
    "no_warns": ("{member} has no warnings.", "{member} no tiene advertencias.", "{member} não tem advertências."),
    "warns_header": (
        "Warnings for {member}:\n{text}",
        "Advertencias de {member}:\n{text}",
        "Advertências de {member}:\n{text}",
    ),
    "warns_row": (
        "`{id}` — {reason} (by <@{mod}>)",
        "`{id}` — {reason} (por <@{mod}>)",
        "`{id}` — {reason} (por <@{mod}>)",
    ),
    "slowmode_set": (
        "🐢 Slowmode set to {seconds} seconds.",
        "🐢 Modo lento configurado a {seconds} segundos.",
        "🐢 Modo lento configurado para {seconds} segundos.",
    ),
    "announce_author": ("Announcement from {guild}", "Anuncio de {guild}", "Anúncio de {guild}"),
    "announce_sent": (
        "✅ Announcement sent to {channel}.",
        "✅ Anuncio enviado a {channel}.",
        "✅ Anúncio enviado para {channel}.",
    ),

    # ---- antispam ----
    "as_scam": ("Scam link detected", "Enlace de scam detectado", "Link de golpe (scam) detectado"),
    "as_rate": (
        "Sending messages too fast (possible spam)",
        "Enviar mensajes demasiado rápido (posible spam)",
        "Enviar mensagens rápido demais (possível spam)",
    ),
    "as_dupe": (
        "Same message/image repeated several times (spam)",
        "Mensaje/imagen repetido varias veces (spam)",
        "Mensagem/imagem repetida várias vezes (spam)",
    ),
    "as_punished": (
        "🚫 Message from {member} deleted and user muted for 10 minutes. Reason: {reason}",
        "🚫 Mensaje de {member} eliminado y usuario silenciado 10 minutos. Motivo: {reason}",
        "🚫 Mensagem de {member} apagada e usuário silenciado por 10 minutos. Motivo: {reason}",
    ),
    "as_on": ("enabled ✅", "activado ✅", "ativado ✅"),
    "as_off": ("disabled ❌", "desactivado ❌", "desativado ❌"),
    "as_state": ("Antispam {state}.", "Antispam {state}.", "Antispam {state}."),
    "as_added": (
        "✅ `{domain}` added to the blacklist.",
        "✅ `{domain}` agregado a la lista negra.",
        "✅ `{domain}` adicionado à lista negra.",
    ),
    "as_list": ("Blocked domains: {text}", "Dominios bloqueados: {text}", "Domínios bloqueados: {text}"),
    "as_empty": ("empty", "vacía", "vazia"),

    # ---- triggers / comandos personalizados ----
    "trg_created": (
        "✅ Trigger created for: `{word}`",
        "✅ Trigger creado para: `{word}`",
        "✅ Trigger criado para: `{word}`",
    ),
    "trg_none": ("No triggers configured.", "No hay triggers configurados.", "Nenhum trigger configurado."),
    "trg_removed": ("✅ Trigger deleted.", "✅ Trigger eliminado.", "✅ Trigger removido."),
    "cmd_error": (
        "⚠️ Couldn't create it (does that name already exist?): {error}",
        "⚠️ No se pudo crear (¿ya existe ese nombre?): {error}",
        "⚠️ Não foi possível criar (esse nome já existe?): {error}",
    ),
    "cmd_created": (
        "✅ Command `/{name}` created and available right now.",
        "✅ Comando `/{name}` creado y disponible ya mismo.",
        "✅ Comando `/{name}` criado e disponível agora mesmo.",
    ),
    "cmd_removed": (
        "✅ Command `/{name}` deleted.",
        "✅ Comando `/{name}` eliminado.",
        "✅ Comando `/{name}` removido.",
    ),

    # ---- embed creator ----
    "em_modal_basic": ("Title & description", "Título y descripción", "Título e descrição"),
    "em_modal_images": ("Images", "Imágenes", "Imagens"),
    "em_modal_footer": ("Footer & Author", "Footer y Autor", "Rodapé e Autor"),
    "em_modal_field": ("Add field", "Agregar campo", "Adicionar campo"),
    "em_title": ("Title", "Título", "Título"),
    "em_desc": ("Description", "Descripción", "Descrição"),
    "em_color": ("Color (hex, e.g. #5865F2)", "Color (hex, ej: #5865F2)", "Cor (hex, ex: #5865F2)"),
    "em_image": ("Large image URL", "URL de imagen grande", "URL da imagem grande"),
    "em_thumb": ("Thumbnail URL (small image)", "URL de thumbnail (imagen chica)", "URL da miniatura (imagem pequena)"),
    "em_footer_text": ("Footer text", "Texto del footer", "Texto do rodapé"),
    "em_footer_icon": ("Footer icon URL", "URL ícono del footer", "URL do ícone do rodapé"),
    "em_author_name": ("Author name", "Nombre del autor", "Nome do autor"),
    "em_author_icon": ("Author icon URL", "URL ícono del autor", "URL do ícone do autor"),
    "em_field_name": ("Field name", "Nombre del campo", "Nome do campo"),
    "em_field_value": ("Field value", "Valor del campo", "Valor do campo"),
    "em_field_inline": ("Inline? (yes/no)", "¿En línea? (si/no)", "Em linha? (sim/não)"),
    "em_inline_default": ("yes", "si", "sim"),
    "em_max_fields": (
        "Maximum 25 fields per embed (Discord limit).",
        "Máximo 25 campos por embed (límite de Discord).",
        "Máximo de 25 campos por embed (limite do Discord).",
    ),
    "em_pick_channel": (
        "Pick the channel to send the embed to",
        "Elegí el canal donde enviar el embed",
        "Escolha o canal para enviar o embed",
    ),
    "em_no_access": (
        "⚠️ I couldn't access that channel (the bot may lack permissions there).",
        "⚠️ No pude acceder a ese canal (puede que el bot no tenga permisos ahí).",
        "⚠️ Não consegui acessar esse canal (o bot pode não ter permissões lá).",
    ),
    "em_sent": ("✅ Embed sent to {channel}", "✅ Embed enviado a {channel}", "✅ Embed enviado para {channel}"),
    "em_empty_preview": (
        "*(empty preview, start by adding some text)*",
        "*(vista previa vacía, empezá agregando texto)*",
        "*(prévia vazia, comece adicionando texto)*",
    ),
    "em_btn_basic": (
        "Title / Description / Color",
        "Título / Descripción / Color",
        "Título / Descrição / Cor",
    ),
    "em_btn_images": ("Images", "Imágenes", "Imagens"),
    "em_btn_footer": ("Footer / Author", "Footer / Autor", "Rodapé / Autor"),
    "em_btn_addfield": ("➕ Add field", "➕ Agregar campo", "➕ Adicionar campo"),
    "em_btn_rmfield": ("🗑️ Remove last field", "🗑️ Quitar último campo", "🗑️ Remover último campo"),
    "em_btn_send": ("📤 Send embed", "📤 Enviar embed", "📤 Enviar embed"),
    "em_btn_cancel": ("❌ Cancel", "❌ Cancelar", "❌ Cancelar"),
    "em_ask_channel": (
        "Which channel should I send it to?",
        "¿A qué canal lo envío?",
        "Para qual canal devo enviar?",
    ),
    "em_cancelled": ("Embed creation cancelled.", "Creación de embed cancelada.", "Criação do embed cancelada."),

    # ---- sorteos ----
    "gw_bad_duration": (
        "Invalid duration format. Use something like 10m, 1h, 2d.",
        "Formato de duración inválido. Usá algo como 10m, 1h, 2d.",
        "Formato de duração inválido. Use algo como 10m, 1h, 2d.",
    ),
    "gw_btn": ("Join", "Participar", "Participar"),
    "gw_joined": (
        "🎉 You're in the giveaway!",
        "🎉 ¡Estás participando en el sorteo!",
        "🎉 Você está participando do sorteio!",
    ),
    "gw_already": (
        "You were already in this giveaway.",
        "Ya estabas participando en este sorteo.",
        "Você já estava participando deste sorteio.",
    ),
    "gw_title": ("🎉 GIVEAWAY 🎉", "🎉 SORTEO 🎉", "🎉 SORTEIO 🎉"),
    "gw_body": (
        "**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** {ends}",
        "**Premio:** {prize}\n**Ganadores:** {winners}\n**Termina:** {ends}",
        "**Prêmio:** {prize}\n**Vencedores:** {winners}\n**Termina:** {ends}",
    ),
    "gw_footer": ("Hosted by {host}", "Organizado por {host}", "Organizado por {host}"),
    "gw_created": ("✅ Giveaway created.", "✅ Sorteo creado.", "✅ Sorteio criado."),
    "gw_not_found": (
        "No active giveaway found with that ID.",
        "No se encontró un sorteo activo con ese ID.",
        "Nenhum sorteio ativo encontrado com esse ID.",
    ),
    "gw_ended_manual": (
        "Giveaway ended manually.",
        "Sorteo finalizado manualmente.",
        "Sorteio encerrado manualmente.",
    ),
    "gw_no_entries": (
        "😔 The giveaway for **{prize}** ended with no valid participants.",
        "😔 El sorteo de **{prize}** terminó sin participantes válidos.",
        "😔 O sorteio de **{prize}** terminou sem participantes válidos.",
    ),
    "gw_end_title": ("🎉 Giveaway ended!", "🎉 ¡Sorteo finalizado!", "🎉 Sorteio encerrado!"),
    "gw_end_body": (
        "**Prize:** {prize}\n**Winner(s):** {winners}",
        "**Premio:** {prize}\n**Ganador(es):** {winners}",
        "**Prêmio:** {prize}\n**Vencedor(es):** {winners}",
    ),

    # ---- honeypot ----
    "hp_title": ("⚠️ Trap channel", "⚠️ Canal trampa", "⚠️ Canal armadilha"),
    "hp_desc": (
        "This channel is an **anti-spam honeypot**.\n"
        "No legitimate member has any reason to write here.\n\n"
        "Any message sent in this channel results in an **immediate kick** and "
        "**deletion of recent messages** across the server.",
        "Este canal es un **honeypot anti-spam**.\n"
        "Ningún miembro legítimo tiene motivo para escribir acá.\n\n"
        "Cualquier mensaje enviado en este canal resulta en "
        "**expulsión inmediata** y **borrado de mensajes recientes** del servidor.",
        "Este canal é um **honeypot anti-spam**.\n"
        "Nenhum membro legítimo tem motivo para escrever aqui.\n\n"
        "Qualquer mensagem enviada neste canal resulta em "
        "**expulsão imediata** e **exclusão das mensagens recentes** em todo o servidor.",
    ),
    "hp_topic": (
        "⚠️ Do not write here — anti-spam trap channel",
        "⚠️ No escribir acá — canal trampa anti-spam",
        "⚠️ Não escreva aqui — canal armadilha anti-spam",
    ),
    "hp_created": (
        "✅ Trap channel created: {channel}\nIt's hidden from @everyone. Anyone who writes there will be kicked and their messages from the last 24 hours will be deleted in all channels.",
        "✅ Canal trampa creado: {channel}\nEstá oculto para @everyone. Cualquiera que escriba ahí será expulsado y se borrarán sus mensajes de las últimas 24 horas en todos los canales.",
        "✅ Canal armadilha criado: {channel}\nEle está oculto para @everyone. Quem escrever lá será expulso e suas mensagens das últimas 24 horas serão apagadas em todos os canais.",
    ),
    "hp_disabled": (
        "✅ Honeypot disabled. The channel still exists but no longer kicks anyone who writes in it.",
        "✅ Honeypot desactivado. El canal sigue existiendo pero ya no expulsa a quien escriba.",
        "✅ Honeypot desativado. O canal continua existindo, mas não expulsa mais quem escrever nele.",
    ),
    "hp_kicked": (
        "🍯 **{member}** was kicked for writing in the trap channel. Their messages from the last 24h were deleted.",
        "🍯 **{member}** fue expulsado por escribir en el canal trampa. Sus mensajes de las últimas 24h fueron borrados.",
        "🍯 **{member}** foi expulso por escrever no canal armadilha. Suas mensagens das últimas 24h foram apagadas.",
    ),

    # ---- reaction roles / join roles ----
    "jr_added": (
        "✅ {role} will be given automatically to new members.",
        "✅ {role} se asignará automáticamente a nuevos miembros.",
        "✅ {role} será atribuído automaticamente aos novos membros.",
    ),
    "jr_removed": (
        "✅ {role} will no longer be assigned automatically.",
        "✅ {role} ya no se asignará automáticamente.",
        "✅ {role} não será mais atribuído automaticamente.",
    ),
    "rr_bad_id": (
        "That message ID isn't valid.",
        "El ID de mensaje no es válido.",
        "O ID da mensagem não é válido.",
    ),
    "rr_not_found": (
        "I couldn't find that message in any visible text channel.",
        "No encontré ese mensaje en ningún canal de texto visible.",
        "Não encontrei essa mensagem em nenhum canal de texto visível.",
    ),
    "rr_bad_emoji": (
        "I couldn't react with that emoji, check that it's valid.",
        "No pude reaccionar con ese emoji, revisá que sea válido.",
        "Não consegui reagir com esse emoji, verifique se ele é válido.",
    ),
    "rr_added": (
        "✅ Reaction {emoji} on that message now grants the role {role}.",
        "✅ Reacción {emoji} en ese mensaje ahora da el rol {role}.",
        "✅ A reação {emoji} nessa mensagem agora dá o cargo {role}.",
    ),

    # ---- tickets ----
    "tk_default_title": ("🎫 Support", "🎫 Soporte", "🎫 Suporte"),
    "tk_default_desc": (
        "Click the button to open a ticket.",
        "Hacé clic en el botón para abrir un ticket.",
        "Clique no botão para abrir um ticket.",
    ),
    "tk_default_button": ("Open Ticket", "Abrir Ticket", "Abrir Ticket"),
    "tk_gone": ("This panel no longer exists.", "Este panel ya no existe.", "Este painel não existe mais."),
    "tk_exists": (
        "You already have an open ticket: {channel}",
        "Ya tenés un ticket abierto: {channel}",
        "Você já tem um ticket aberto: {channel}",
    ),
    "tk_open_title": ("🎫 Ticket opened", "🎫 Ticket abierto", "🎫 Ticket aberto"),
    "tk_open_desc": (
        "Hi {user}, thanks for reaching out.\nTell us what you need and the support team will be with you shortly.",
        "Hola {user}, gracias por contactarte.\nContanos tu consulta y el equipo de soporte te va a atender pronto.",
        "Olá {user}, obrigado por entrar em contato.\nConte sua dúvida e a equipe de suporte vai atender você em breve.",
    ),
    "tk_created": ("Ticket created: {channel}", "Ticket creado: {channel}", "Ticket criado: {channel}"),
    "tk_btn_claim": ("Claim", "Reclamar", "Assumir"),
    "tk_btn_close": ("Close Ticket", "Cerrar Ticket", "Fechar Ticket"),
    "tk_staff_only": (
        "Only staff can claim tickets.",
        "Solo el staff puede reclamar tickets.",
        "Apenas a equipe pode assumir tickets.",
    ),
    "tk_claimed": (
        "🙋 Ticket claimed by {user}",
        "🙋 Ticket reclamado por {user}",
        "🙋 Ticket assumido por {user}",
    ),
    "tk_not_ticket": (
        "This doesn't look like a registered ticket.",
        "Esto no parece ser un ticket registrado.",
        "Isto não parece ser um ticket registrado.",
    ),
    "tk_no_close": (
        "You don't have permission to close this ticket.",
        "No tenés permiso para cerrar este ticket.",
        "Você não tem permissão para fechar este ticket.",
    ),
    "tk_closing": (
        "🔒 Closing ticket in 5 seconds...",
        "🔒 Cerrando ticket en 5 segundos...",
        "🔒 Fechando o ticket em 5 segundos...",
    ),
    "tk_log_title": ("Ticket closed", "Ticket cerrado", "Ticket fechado"),
    "tk_log_desc": (
        "Channel: `{channel}`\nClosed by: {user}",
        "Canal: `{channel}`\nCerrado por: {user}",
        "Canal: `{channel}`\nFechado por: {user}",
    ),
    "tk_panel_created": ("✅ Panel created.", "✅ Panel creado.", "✅ Painel criado."),
    "tk_user_added": (
        "✅ {user} added to the ticket.",
        "✅ {user} agregado al ticket.",
        "✅ {user} adicionado ao ticket.",
    ),
    "tk_user_removed": (
        "✅ {user} removed from the ticket.",
        "✅ {user} quitado del ticket.",
        "✅ {user} removido do ticket.",
    ),
    "tk_log_set": (
        "✅ Ticket log channel: {channel}",
        "✅ Canal de logs de tickets: {channel}",
        "✅ Canal de logs de tickets: {channel}",
    ),
}


def tr(ctx, key: str, **kwargs) -> str:
    """Texto traducido según el idioma de `ctx` (Interaction, Guild o Message)."""
    text = MESSAGES[key][lang_index(ctx)]
    return text.format(**kwargs) if kwargs else text


# Descripciones de comandos / parámetros / opciones: clave = texto en inglés, valor = (español, portugués)
DESCRIPTIONS = {
    # general
    "Shows the bot's latency": ("Muestra la latencia del bot", "Mostra a latência do bot"),
    "Creates a voice channel that shows the member count in its name": (
        "Crea un canal de voz que muestra la cantidad de miembros en su nombre",
        "Cria um canal de voz que mostra a quantidade de membros no nome",
    ),
    "Category to create the channel in (optional)": (
        "Categoría donde crear el canal (opcional)",
        "Categoria onde criar o canal (opcional)",
    ),
    "Shows info about the bot and its modules": (
        "Muestra información sobre el bot y sus módulos",
        "Mostra informações sobre o bot e seus módulos",
    ),
    # admin
    "Configure which roles count as administration for the bot": (
        "Configura qué roles cuentan como administración para el bot",
        "Configura quais cargos contam como administração para o bot",
    ),
    "Adds a role recognized as 'administration' by the bot": (
        "Agrega un rol como 'administración' reconocido por el bot",
        "Adiciona um cargo reconhecido como 'administração' pelo bot",
    ),
    "Removes a role from the bot's administration list": (
        "Quita un rol de la lista de administración del bot",
        "Remove um cargo da lista de administração do bot",
    ),
    "Shows the roles recognized as administration": (
        "Muestra los roles reconocidos como administración",
        "Mostra os cargos reconhecidos como administração",
    ),
    "Kicks a member from the server": ("Expulsa a un miembro del servidor", "Expulsa um membro do servidor"),
    "Bans a member from the server": ("Banea a un miembro del servidor", "Bane um membro do servidor"),
    "Unbans a user by ID": ("Desbanea a un usuario por su ID", "Desbane um usuário pelo ID"),
    "Mutes (timeouts) a member for X minutes": (
        "Silencia (timeout) a un miembro por X minutos",
        "Silencia (timeout) um membro por X minutos",
    ),
    "Removes a member's timeout": ("Quita el timeout a un miembro", "Remove o timeout de um membro"),
    "Deletes a number of messages from the channel": (
        "Borra una cantidad de mensajes del canal",
        "Apaga uma quantidade de mensagens do canal",
    ),
    "Records a warning for a user": ("Registra una advertencia a un usuario", "Registra uma advertência para um usuário"),
    "Shows a user's warnings": ("Muestra las advertencias de un usuario", "Mostra as advertências de um usuário"),
    "Sets slowmode for the current channel (seconds)": (
        "Configura el modo lento del canal actual (segundos)",
        "Configura o modo lento do canal atual (segundos)",
    ),
    "Sends a formatted announcement to a channel": (
        "Envía un anuncio con formato a un canal",
        "Envia um anúncio formatado para um canal",
    ),
    # antispam
    "Antispam system settings": ("Configuración del sistema antispam", "Configurações do sistema antispam"),
    "Enables or disables antispam on this server": (
        "Activa o desactiva el antispam en este servidor",
        "Ativa ou desativa o antispam neste servidor",
    ),
    "Adds a domain to the antispam blacklist": (
        "Agrega un dominio a la lista negra de antispam",
        "Adiciona um domínio à lista negra do antispam",
    ),
    "Shows the blacklisted domains": ("Muestra los dominios en la lista negra", "Mostra os domínios na lista negra"),
    # triggers
    "Manage automatic messages (triggers)": (
        "Gestión de mensajes automáticos (triggers)",
        "Gerenciar mensagens automáticas (triggers)",
    ),
    "Creates a trigger: when a word is detected, the bot replies": (
        "Crea un trigger: al detectar una palabra, el bot responde",
        "Cria um trigger: ao detectar uma palavra, o bot responde",
    ),
    "Word or phrase that activates the trigger": (
        "Palabra o frase que activa el trigger",
        "Palavra ou frase que ativa o trigger",
    ),
    "What the bot will reply": ("Lo que el bot va a responder", "O que o bot vai responder"),
    "Whether it must match exactly or just contain the word": (
        "Si debe coincidir exacto o solo contener la palabra",
        "Se deve ser exato ou apenas conter a palavra",
    ),
    "Contains the word": ("Contiene la palabra", "Contém a palavra"),
    "Exact message": ("Mensaje exacto", "Mensagem exata"),
    "Lists the configured triggers": ("Lista los triggers configurados", "Lista os triggers configurados"),
    "Deletes a trigger by ID (see /trigger list)": (
        "Elimina un trigger por su ID (ver /trigger list)",
        "Remove um trigger pelo ID (veja /trigger list)",
    ),
    "Manage custom slash commands": (
        "Gestión de comandos slash personalizados",
        "Gerenciar comandos slash personalizados",
    ),
    "Creates a custom slash command (e.g. /rules)": (
        "Crea un comando slash personalizado (ej: /reglas)",
        "Cria um comando slash personalizado (ex: /regras)",
    ),
    "Command name, no spaces or capitals (e.g. rules)": (
        "Nombre del comando, sin espacios ni mayúsculas (ej: reglas)",
        "Nome do comando, sem espaços nem maiúsculas (ex: regras)",
    ),
    "Text the bot will send when the command is used": (
        "Texto que el bot enviará al usar el comando",
        "Texto que o bot enviará ao usar o comando",
    ),
    "Description shown in Discord when typing /": (
        "Descripción que se muestra en Discord al escribir /",
        "Descrição exibida no Discord ao digitar /",
    ),
    "Deletes a custom slash command": (
        "Elimina un comando slash personalizado",
        "Remove um comando slash personalizado",
    ),
    # embed
    "Opens the interactive embed creator": (
        "Abre el creador interactivo de embeds",
        "Abre o criador interativo de embeds",
    ),
    # giveaways
    "Creates a giveaway with a join button": (
        "Crea un sorteo con botón de participación",
        "Cria um sorteio com botão de participação",
    ),
    "What is being given away": ("Qué se sortea", "O que está sendo sorteado"),
    "Duration: e.g. 10m, 1h, 2d": ("Duración: ej 10m, 1h, 2d", "Duração: ex 10m, 1h, 2d"),
    "Number of winners (default 1)": ("Cantidad de ganadores (default 1)", "Quantidade de vencedores (padrão 1)"),
    "Ends a giveaway manually ahead of time": (
        "Termina un sorteo manualmente antes de tiempo",
        "Encerra um sorteio manualmente antes do tempo",
    ),
    # honeypot
    "Creates (or reconfigures) the anti-scam trap channel": (
        "Crea (o reconfigura) el canal trampa anti-scam",
        "Cria (ou reconfigura) o canal armadilha anti-scam",
    ),
    "Tempting name for the channel (default: ・free-nitro)": (
        "Nombre tentador para el canal (default: ・free-nitro)",
        "Nome tentador para o canal (padrão: ・free-nitro)",
    ),
    "Disables the honeypot (doesn't delete the channel)": (
        "Desactiva el honeypot (no borra el canal)",
        "Desativa o honeypot (não apaga o canal)",
    ),
    # join roles / reaction roles
    "Automatic roles when joining the server": (
        "Roles automáticos al entrar al servidor",
        "Cargos automáticos ao entrar no servidor",
    ),
    "Adds a role given automatically to new members": (
        "Agrega un rol que se dará automáticamente a nuevos miembros",
        "Adiciona um cargo dado automaticamente a novos membros",
    ),
    "Removes a role from the join-roles list": (
        "Quita un rol de la lista de join-roles",
        "Remove um cargo da lista de join-roles",
    ),
    "Reaction roles": ("Roles por reacción", "Cargos por reação"),
    "Links a message emoji to a role": (
        "Vincula un emoji de un mensaje a un rol",
        "Vincula um emoji de uma mensagem a um cargo",
    ),
    "Message ID (right click -> Copy ID, needs developer mode)": (
        "ID del mensaje (clic derecho -> Copiar ID, necesitás modo desarrollador activado)",
        "ID da mensagem (botão direito -> Copiar ID, requer modo desenvolvedor ativado)",
    ),
    "The emoji to use (must exist on the server or be a standard Discord one)": (
        "El emoji a usar (tiene que existir en el server o ser uno estándar de Discord)",
        "O emoji a usar (precisa existir no servidor ou ser um padrão do Discord)",
    ),
    "Role granted when reacting": ("Rol que se dará al reaccionar", "Cargo concedido ao reagir"),
    # tickets
    "Manage the ticket system": ("Gestión del sistema de tickets", "Gerenciar o sistema de tickets"),
    "Creates a ticket panel in this channel": (
        "Crea un panel de tickets en este canal",
        "Cria um painel de tickets neste canal",
    ),
    "Title of the panel embed": ("Título del embed del panel", "Título do embed do painel"),
    "Embed description": ("Descripción del embed", "Descrição do embed"),
    "Text of the button that opens a ticket": (
        "Texto del botón para abrir ticket",
        "Texto do botão para abrir ticket",
    ),
    "Category where ticket channels will be created": (
        "Categoría donde se crearán los canales de ticket",
        "Categoria onde os canais de ticket serão criados",
    ),
    "Hex color, e.g. #5865F2": ("Color en hex, ej: #5865F2", "Cor em hex, ex: #5865F2"),
    "Role that can see and answer tickets": (
        "Rol que podrá ver y responder los tickets",
        "Cargo que poderá ver e responder os tickets",
    ),
    "Adds a user to the current ticket": ("Agrega un usuario al ticket actual", "Adiciona um usuário ao ticket atual"),
    "Removes a user from the current ticket": (
        "Quita un usuario del ticket actual",
        "Remove um usuário do ticket atual",
    ),
    "Sets the channel where ticket closures are logged": (
        "Define el canal donde se registran los cierres de tickets",
        "Define o canal onde os fechamentos de tickets são registrados",
    ),
}


class IngnitiumTranslator(app_commands.Translator):
    """Localiza descripciones de comandos para clientes en español (es-ES / es-419) y portugués (pt-BR)."""

    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context):
        idx = lang_index(locale)
        if idx == EN:
            return None
        entry = DESCRIPTIONS.get(string.message)
        return entry[idx - 1] if entry else None
