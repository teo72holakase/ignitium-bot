# Ingnitium — Bot de Discord

Bot modular hecho con `discord.py` + Supabase, pensado para copiar a VS Code, subir a GitHub y alojar en WispByte.

## 📁 Estructura

```
discord-bot/
├── main.py                 # Punto de entrada, carga todos los cogs
├── keepalive.py             # Servidor Flask para mantener el proceso vivo en WispByte
├── requirements.txt
├── .env.example              # Copiar a .env y completar
├── .gitignore
├── supabase_schema.sql       # Pegar en el SQL Editor de Supabase
├── utils/
│   ├── db.py                 # Cliente Supabase
│   ├── permissions.py        # Chequeo de "es administrador"
│   └── i18n.py               # Traducciones (EN / ES / PT-BR) y traductor de comandos
└── cogs/
    ├── tickets.py             # Sistema de tickets
    ├── custom_triggers.py     # Triggers y comandos personalizados
    ├── embed_creator.py       # Embed creator interactivo
    ├── antispam.py            # Antispam
    ├── giveaways.py           # Sorteos
    ├── reaction_roles.py      # Reaction roles y join roles
    ├── admin.py               # Moderación y roles de admin
    └── general.py             # /ping, /help y /counter-setup
```

### 4. Probar en local
```bash
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 5. Subir a GitHub
```bash
git init
git add .
git commit -m "Bot inicial"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```
El `.gitignore` ya excluye tu `.env`, así que el token nunca se sube.

### 6. Desplegar en WispByte
1. Creá un servidor tipo **Generic/Python** (o el template que WispByte tenga para bots de Python).
2. Conectá el repo de GitHub o subí los archivos por SFTP.
3. Startup command: `python main.py` (o `python3 main.py`, según el panel).
4. En la sección de **Variables de entorno / Startup Variables** del panel, cargá las mismas variables del `.env` (DISCORD_TOKEN, SUPABASE_URL, SUPABASE_KEY, GUILD_ID, KEEPALIVE_PORT).
5. **Sobre el keepalive:** la mayoría de paneles tipo WispByte (basados en Pterodactyl) mantienen el proceso corriendo mientras el contenedor esté encendido — no "duermen" el proceso como un free-tier de Heroku/Replit. El archivo `keepalive.py` expone un endpoint HTTP (`/`) por si tu plan específico sí requiere un ping externo para no reciclar el proceso; en ese caso, configurá un monitor gratuito en **UptimeRobot** o **cron-job.org** que pegue a `http://TU-IP-O-DOMINIO:PUERTO/` cada 5 minutos. Revisá el panel/documentación de tu plan de WispByte para confirmar si esto es necesario en tu caso — varía según el tipo de plan contratado.

## 🌐 Idiomas

Los mensajes del bot están en **inglés por defecto** y se adaptan solos al idioma del cliente de Discord de quien usa el comando: **español** (es-ES / es-419) y **portugués de Brasil** (pt-BR). Cualquier otro idioma cae en inglés.

- Las respuestas a comandos, botones, modales y la lista de comandos (`/`) usan el idioma del usuario.
- Los mensajes públicos que no vienen de un usuario concreto (sorteos, honeypot, antispam, contador de miembros) usan el **idioma preferido del servidor** (Server Settings → Community → Primary Language).
- Para editar o agregar textos, todo está en `utils/i18n.py`: `MESSAGES` (mensajes) y `DESCRIPTIONS` (descripciones de comandos).

## 🧩 Uso rápido de cada función

- **Tickets**: `/ticket panel` en el canal donde querés el botón. Los usuarios abren tickets, el staff los reclama con el botón "Reclamar" y los cierra con "Cerrar Ticket".
- **Triggers**: `/trigger add word:hola response:"¡Bienvenido!"` — cada vez que alguien escriba "hola", el bot responde.
- **Comandos personalizados**: `/customcommand add name:reglas response:"..."` crea un `/reglas` al instante.
- **Embeds**: `/embed-create` abre un panel con botones para título, descripción, color, imágenes, footer, autor y campos, con vista previa en vivo.
- **Antispam**: activado por defecto. Detecta ráfagas de mensajes, contenido/imagen repetida y dominios de scam conocidos (ampliable con `/antispam blacklist-add`).
- **Sorteos**: `/giveaway prize:"Rango VIP" duration:1h winners:2` — la gente participa con el botón, el bot sortea automáticamente al terminar el tiempo.
- **Reaction roles**: `/reactionrole add message_id:... emoji:🔥 role:@Miembro`.
- **Join roles**: `/joinrole add role:@Nuevo` — se asigna automático a quien entre.
- **Roles de administración del bot**: `/adminrole add role:@Moderador` — ese rol podrá usar todos los comandos de admin del bot aunque no tenga el permiso nativo "Administrador" de Discord.

## ⚠️ Notas importantes

- Los comandos slash pueden tardar hasta 1 hora en aparecer si no configurás `GUILD_ID` (sincronización global). Con `GUILD_ID` configurado, aparecen al instante solo en ese servidor — ideal durante desarrollo.
- La `service_role key` de Supabase tiene acceso total a la base de datos sin restricciones de RLS. Nunca la subas a un repo público ni la compartas; siempre debe vivir solo en variables de entorno.
- Si en el futuro querés Row Level Security en Supabase, este bot no lo necesita porque accede con la service_role key directamente (es un backend confiable, no un cliente público).
