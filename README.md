# Ingnitium — Bot de Discord

Bot modular de moderación y comunidad hecho con `discord.py` y Supabase. Incluye tickets, triggers, comandos personalizados, creador de embeds, antispam, honeypot, sorteos, roles automáticos y por reacción, y herramientas de moderación.

## Índice

- [Idiomas](#-idiomas)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Quién puede usar qué (permisos)](#-quién-puede-usar-qué-permisos)
- [Lista rápida de comandos](#-lista-rápida-de-comandos)
- [Wiki de comandos](#-wiki-de-comandos)
  - [General](#general)
  - [Administración y moderación](#administración-y-moderación)
  - [Tickets](#tickets)
  - [Triggers y comandos personalizados](#triggers-y-comandos-personalizados)
  - [Embeds](#embeds)
  - [Antispam](#antispam)
  - [Honeypot (canal trampa)](#honeypot-canal-trampa)
  - [Sorteos](#sorteos)
  - [Roles automáticos y por reacción](#roles-automáticos-y-por-reacción)
- [Funciones automáticas (sin comando)](#-funciones-automáticas-sin-comando)
- [Base de datos](#-base-de-datos)
- [Precauciones generales](#-precauciones-generales)
- [Problemas frecuentes](#-problemas-frecuentes)

---

## 🌐 Idiomas

Los mensajes del bot están en **inglés por defecto** y se adaptan solos al idioma del cliente de Discord de quien usa el comando: **español** (es-ES / es-419) y **portugués de Brasil** (pt-BR). Cualquier otro idioma cae en inglés.

- **Respuestas a comandos, botones, ventanas (modales) y la descripción de cada comando** en la lista de `/`: usan el idioma del usuario que los ejecuta.
- **Mensajes públicos sin un usuario de referencia** (sorteos, honeypot, avisos del antispam, nombre del contador de miembros, logs de tickets): usan el **idioma principal del servidor** (Ajustes del servidor → Comunidad → Idioma principal).
- **Los nombres de los comandos y de sus parámetros están siempre en inglés**, sin importar el idioma.
- Para editar o agregar textos: `utils/i18n.py` (`MESSAGES` para mensajes, `DESCRIPTIONS` para las descripciones de comandos).

## 📁 Estructura del proyecto

```
├── main.py                  # Punto de entrada, carga todos los cogs
├── keepalive.py             # Servidor web mínimo (endpoint "/")
├── requirements.txt
├── supabase_schema.sql      # Esquema de la base de datos
├── reset_data.sql           # Borra todos los datos del bot (conserva las tablas)
├── utils/
│   ├── db.py                # Cliente Supabase
│   ├── permissions.py       # Chequeo de "es administrador"
│   └── i18n.py              # Traducciones EN / ES / PT-BR
└── cogs/
    ├── general.py           # /ping, /help, /counter-setup y contador de miembros
    ├── admin.py             # Moderación y roles de administración
    ├── tickets.py           # Sistema de tickets
    ├── custom_triggers.py   # Triggers y comandos personalizados
    ├── embed_creator.py     # Creador interactivo de embeds
    ├── antispam.py          # Antispam
    ├── honeypot.py          # Canal trampa anti-scam
    ├── giveaways.py         # Sorteos
    └── reaction_roles.py    # Roles por reacción y roles al entrar
```

---

## 🔐 Quién puede usar qué (permisos)

Casi todos los comandos están protegidos por el chequeo **"es administrador del bot"**. Se considera administrador a quien cumpla **al menos una** de estas condiciones:

1. Tiene el permiso nativo de Discord **Administrador**.
2. Tiene un rol agregado con `/adminrole add`.
3. Tiene el rol cuyo ID está en la variable `ADMIN_ROLE_ID` (opcional, configurada por quien aloja el bot).

Quien no cumpla ninguna recibe un mensaje de "no tenés permisos de administración".

Excepciones:

| Comando | Quién puede usarlo |
|---|---|
| `/ping`, `/help` | Cualquier miembro |
| `/counter-setup` | Quien tenga el permiso **Gestionar servidor** |
| Botón **Join** de un sorteo | Cualquier miembro |
| Botón **Close Ticket** | El dueño del ticket **o** un administrador del bot |
| Botón **Claim** | Solo administradores del bot |

> ⚠️ **Primer uso:** `/adminrole add` también exige ser administrador. La primera vez tiene que hacerlo alguien con el permiso nativo de Discord **Administrador** (normalmente el dueño del servidor).

> ⚠️ **Los roles de `/adminrole` son poderosos.** Quien los tenga puede usar `/kick`, `/ban`, `/clear`, etc. a través del bot **aunque no tenga esos permisos en Discord**. Asignalos solo a gente de confianza.

---

## ⚡ Lista rápida de comandos

| Módulo | Comandos |
|---|---|
| General | `/ping` · `/help` · `/counter-setup` |
| Administración | `/adminrole add\|remove\|list` · `/kick` · `/ban` · `/unban` · `/mute` · `/unmute` · `/clear` · `/warn` · `/warns` · `/slowmode` · `/announce` |
| Tickets | `/ticket panel` · `/ticket add` · `/ticket remove` · `/ticket log-channel` |
| Triggers | `/trigger add\|list\|remove` |
| Comandos personalizados | `/customcommand add\|remove` |
| Embeds | `/embed-create` |
| Antispam | `/antispam toggle` · `/antispam blacklist-add` · `/antispam blacklist-list` |
| Honeypot | `/honeypot-setup` · `/honeypot-disable` |
| Sorteos | `/giveaway` · `/giveaway-end` |
| Roles | `/joinrole add\|remove` · `/reactionrole add` |

---

# 📚 Wiki de comandos

> **Cómo leer esta wiki:** los parámetros marcados como *(obligatorio)* hay que completarlos; los demás son opcionales. Las respuestas **efímeras** solo las ve quien ejecutó el comando; las **públicas** las ve todo el canal.

## General

### `/ping`
Muestra la latencia del bot en milisegundos.
- **Permiso:** cualquiera.
- **Respuesta:** pública.
- **Uso:** `/ping` → `🏓 Pong! 87ms`

### `/help`
Muestra un resumen de los módulos del bot y qué comandos tiene cada uno.
- **Permiso:** cualquiera.
- **Uso:** `/help`. Para ver la descripción de cada comando, escribí `/` en el chat.

### `/counter-setup`
Crea un **canal de voz** cuyo nombre muestra la cantidad de miembros (por ejemplo `👥 Members: 120`). El bot lo renombra solo cada 10 minutos.

| Parámetro | Descripción |
|---|---|
| `category` | Categoría donde crear el canal (opcional) |

- **Permiso:** Gestionar servidor.
- **Respuesta:** efímera.
- **Uso:** `/counter-setup category:#Estadísticas`

**Precauciones:**
- El contador **no cuenta a todos los miembros**: cuenta a quienes tienen un rol concreto, definido en el código (`MIEMBRO_ROLE_ID` en `cogs/general.py`). Si el rol no existe en tu servidor, el contador mostrará `0`. Hay que cambiar ese ID por el de tu rol de miembro.
- El canal se crea con `Connect` desactivado para `@everyone`: se ve, pero nadie puede entrar.
- Solo se recuerda **un** contador por servidor. Si ejecutás el comando otra vez se crea un canal nuevo y el anterior queda sin actualizarse (hay que borrarlo a mano).
- Discord limita cuántas veces se puede renombrar un canal, por eso el intervalo no se puede bajar de unos 10 minutos.
- Requiere la columna `member_counter_channel_id` en la tabla `guild_config` (ya incluida en `supabase_schema.sql`).

---

## Administración y moderación

Todos requieren ser administrador del bot (ver [permisos](#-quién-puede-usar-qué-permisos)).

**Precauciones válidas para todo este módulo:**
- El **rol del bot tiene que estar por encima** del rol del usuario al que querés sancionar, y tener el permiso de Discord correspondiente (Expulsar, Banear, Moderar miembros, Gestionar mensajes, Gestionar canales). Si no, Discord rechaza la acción.
- **El bot no puede sancionar al dueño del servidor ni a quien tenga un rol superior al suyo.**
- El bot **no verifica la jerarquía de quien ejecuta el comando**: un administrador del bot puede sancionar a otro miembro del staff mientras esté por debajo del rol del bot. Usalo con criterio.

### `/adminrole add` · `/adminrole remove` · `/adminrole list`
Define qué roles cuentan como "administración" para el bot.

| Comando | Parámetro | Descripción |
|---|---|---|
| `add` | `role` *(obligatorio)* | Rol que pasa a tener permisos de administración del bot |
| `remove` | `role` *(obligatorio)* | Rol al que se le quitan |
| `list` | — | Muestra los roles configurados |

- **Respuesta:** efímera.
- **Ejemplo:** `/adminrole add role:@Moderador`
- **Precaución:** ver el aviso de arriba sobre lo poderoso que es este permiso. Quitar un rol solo afecta al bot; el rol sigue existiendo en Discord.

### `/kick`
Expulsa a un miembro del servidor (puede volver a entrar con una invitación).

| Parámetro | Descripción |
|---|---|
| `member` *(obligatorio)* | Miembro a expulsar |
| `reason` | Motivo (si lo omitís, se guarda "Not specified") |

- **Respuesta:** pública. **Ejemplo:** `/kick member:@Usuario reason:Spam`

### `/ban`
Banea a un miembro del servidor.

| Parámetro | Descripción |
|---|---|
| `member` *(obligatorio)* | Miembro a banear |
| `reason` | Motivo |

- **Respuesta:** pública. **Ejemplo:** `/ban member:@Usuario reason:Scam`
- **Precaución:** el ban **no borra los mensajes anteriores** del usuario. Si querés limpiarlos, usá `/clear` antes o la moderación manual de Discord.

### `/unban`
Quita el ban de un usuario usando su **ID**.

| Parámetro | Descripción |
|---|---|
| `user_id` *(obligatorio)* | ID numérico del usuario (con el Modo desarrollador activado: clic derecho → Copiar ID) |

- **Ejemplo:** `/unban user_id:123456789012345678`
- **Precaución:** si el ID es incorrecto o el usuario no está baneado, el comando falla sin hacer nada.

### `/mute`
Silencia a un miembro con un *timeout* de Discord (no puede escribir, hablar ni reaccionar).

| Parámetro | Descripción |
|---|---|
| `member` *(obligatorio)* | Miembro a silenciar |
| `minutes` *(obligatorio)* | Duración en minutos |
| `reason` | Motivo |

- **Respuesta:** pública. **Ejemplo:** `/mute member:@Usuario minutes:30 reason:Insultos`
- **Precaución:** Discord permite como máximo **28 días** (`40320` minutos). Un valor mayor da error. No se puede silenciar a administradores.

### `/unmute`
Quita el *timeout* a un miembro antes de tiempo.
- **Parámetro:** `member` *(obligatorio)*. **Ejemplo:** `/unmute member:@Usuario`

### `/clear`
Borra mensajes recientes del canal donde lo ejecutás.

| Parámetro | Descripción |
|---|---|
| `count` *(obligatorio)* | Cantidad de mensajes, de 1 a 100 |

- **Respuesta:** efímera (informa cuántos borró). **Ejemplo:** `/clear count:50`
- **Precauciones:** **no se puede deshacer.** Discord no permite el borrado masivo de mensajes de más de 14 días, así que puede borrar menos de lo pedido. Borra también mensajes fijados (pineados).

### `/warn`
Registra una advertencia a un usuario en la base de datos.

| Parámetro | Descripción |
|---|---|
| `member` *(obligatorio)* | Miembro a advertir |
| `reason` *(obligatorio)* | Motivo |

- **Respuesta:** pública. **Ejemplo:** `/warn member:@Usuario reason:Lenguaje inapropiado`
- **Precauciones:** la advertencia **solo se registra**: no envía mensaje privado al usuario ni aplica sanciones automáticas al acumularlas. Actualmente **no hay un comando para borrar advertencias**; solo se pueden eliminar desde la tabla `warns` de Supabase.

### `/warns`
Lista las advertencias de un usuario, con el ID de cada una, el motivo y quién la puso.
- **Parámetro:** `member` *(obligatorio)*. **Respuesta:** efímera. **Ejemplo:** `/warns member:@Usuario`

### `/slowmode`
Configura el modo lento del **canal actual**.

| Parámetro | Descripción |
|---|---|
| `seconds` *(obligatorio)* | De 0 a 21600 (6 horas). `0` lo desactiva |

- **Respuesta:** efímera. **Ejemplo:** `/slowmode seconds:10`

### `/announce`
Envía un anuncio en formato embed (con tu nombre de servidor como autor) a un canal.

| Parámetro | Descripción |
|---|---|
| `channel` *(obligatorio)* | Canal de texto de destino |
| `message` *(obligatorio)* | Texto del anuncio |

- **Respuesta:** efímera (confirmación); el anuncio se publica en el canal elegido.
- **Ejemplo:** `/announce channel:#anuncios message:Mañana hay mantenimiento a las 18:00`
- **Precauciones:** el bot necesita permiso para escribir y enviar embeds en ese canal. Los campos de comandos slash **no admiten saltos de línea** cómodamente; para anuncios largos o con formato usá `/embed-create`.

---

## Tickets

Sistema de soporte con botón. Cada ticket es un **canal privado** visible solo para quien lo abre, el bot y el rol de soporte configurado.

### `/ticket panel`
Publica en el canal actual un mensaje con un botón para abrir tickets.

| Parámetro | Descripción |
|---|---|
| `title` *(obligatorio)* | Título del embed del panel |
| `description` *(obligatorio)* | Texto del embed |
| `button` | Texto del botón (por defecto "Open Ticket" / "Abrir Ticket" / "Abrir Ticket" según el idioma del servidor) |
| `category` | Categoría donde se crearán los canales de ticket |
| `color` | Color en hex, por defecto `#2b2d31` |
| `support_role` | Rol que podrá ver y responder los tickets |

- **Respuesta:** efímera (el panel se publica en el canal).
- **Ejemplo:** `/ticket panel title:Soporte description:Presioná el botón para abrir un ticket. button:Abrir ticket category:Tickets color:#5865F2 support_role:@Staff`

**Cómo funciona el flujo:**
1. Un usuario presiona el botón → se crea un canal privado dentro de la categoría elegida.
2. Un administrador del bot puede presionar **Claim** para marcar que atiende el ticket.
3. El dueño del ticket o un administrador presiona **Close Ticket** → el bot avisa, espera **5 segundos** y **elimina el canal**.

**Precauciones:**
- Cada usuario puede tener **un solo ticket abierto por panel**.
- ⚠️ **Al cerrar, el canal se elimina y no se guarda transcripción.** Si necesitás conservar la conversación, copiala antes de cerrar.
- Si no indicás `support_role`, **solo** el dueño, el bot y los administradores de Discord verán el ticket. Indicá siempre el rol del staff.
- El botón **Claim** lo puede usar solo un administrador del bot, aunque otro rol esté configurado como `support_role`.
- Podés crear varios paneles (por ejemplo "Soporte" y "Reportes") con distintos roles y categorías.
- Los botones siguen funcionando tras reiniciar el bot.

### `/ticket add`
Da acceso a un usuario al ticket donde ejecutás el comando.
- **Parámetro:** `user` *(obligatorio)*. **Respuesta:** pública. **Ejemplo:** `/ticket add user:@Usuario`

### `/ticket remove`
Quita el acceso de un usuario al ticket actual.
- **Parámetro:** `user` *(obligatorio)*. **Respuesta:** pública. **Ejemplo:** `/ticket remove user:@Usuario`

> ⚠️ **`/ticket add` y `/ticket remove` modifican los permisos del canal donde los ejecutás sin comprobar que sea un ticket.** Usalos únicamente dentro de canales de ticket.

### `/ticket log-channel`
Define el canal donde el bot registra cada ticket cerrado (nombre del canal y quién lo cerró).
- **Parámetro:** `channel` *(obligatorio)*. **Respuesta:** efímera. **Ejemplo:** `/ticket log-channel channel:#logs-tickets`
- **Precaución:** conviene que sea un canal privado del staff. Si no se configura, no se registra nada.

---

## Triggers y comandos personalizados

### `/trigger add`
Crea una respuesta automática: cuando alguien escribe cierta palabra o frase, el bot responde en el mismo canal.

| Parámetro | Descripción |
|---|---|
| `word` *(obligatorio)* | Palabra o frase que activa el trigger |
| `response` *(obligatorio)* | Lo que responderá el bot |
| `match_type` | `Contains the word` (por defecto) o `Exact message` |

- **Respuesta:** efímera.
- **Ejemplos:**
  - `/trigger add word:ip response:La IP del servidor es play.ejemplo.com match_type:Exact message`
  - `/trigger add word:reglas response:Leé el canal #reglas`

**Cómo se compara el texto:**
- No distingue mayúsculas de minúsculas.
- **Contains:** se activa si el mensaje *contiene* el texto en cualquier parte. Con la palabra `ip`, se activaría también con "t**ip**s" o "esc**ip**". Para palabras cortas usá **Exact message**.
- **Exact:** se activa solo si el mensaje completo es igual al texto.
- Solo se dispara **el primer trigger** que coincida, y responde también a administradores.

### `/trigger list`
Muestra los triggers del servidor con su **ID**, el texto, el tipo y los primeros 50 caracteres de la respuesta.
- **Respuesta:** efímera.

### `/trigger remove`
Elimina un trigger.

| Parámetro | Descripción |
|---|---|
| `id` *(obligatorio)* | ID que aparece en `/trigger list` |

- **Ejemplo:** `/trigger remove id:3`

### `/customcommand add`
Crea un comando slash propio que responde con un texto fijo, disponible al instante.

| Parámetro | Descripción |
|---|---|
| `name` *(obligatorio)* | Nombre del comando, sin espacios ni mayúsculas (los espacios se convierten en `-`) |
| `response` *(obligatorio)* | Texto que enviará el bot |
| `description` | Descripción que se ve en Discord al escribir `/` (por defecto "Custom command") |

- **Respuesta:** efímera (confirmación); al usarse, el comando responde de forma pública.
- **Ejemplo:** `/customcommand add name:rules response:1. Respeto 2. Sin spam description:Reglas del servidor` → crea `/rules`.

**Precauciones:**
- **No uses el nombre de un comando que ya existe** (`help`, `ping`, `kick`, `giveaway`, etc.). El bot guarda el registro pero no puede crear el comando duplicado, y igual responde "creado".
- Nombres válidos en Discord: letras minúsculas, números y guiones, hasta 32 caracteres.
- El comando responde siempre el mismo texto; no admite parámetros.
- Puede tardar unos segundos en aparecer en tu cliente de Discord; si no aparece, reiniciá Discord (`Ctrl+R`).

### `/customcommand remove`
Elimina un comando personalizado.
- **Parámetro:** `name` *(obligatorio)*, sin la barra. **Ejemplo:** `/customcommand remove name:rules`

---

## Embeds

### `/embed-create`
Abre un **panel interactivo** (solo visible para vos) para armar un embed con vista previa en vivo y enviarlo a un canal.

**Botones del panel:**

| Botón | Qué edita |
|---|---|
| **Title / Description / Color** | Título, descripción y color (hex, ej. `#5865F2`) |
| **Images** | URL de imagen grande y de miniatura |
| **Footer / Author** | Texto e ícono del pie, nombre e ícono del autor |
| **➕ Add field** | Agrega un campo (nombre, valor y si va en línea: `yes`/`no`, `sí`/`no` o `sim`/`não`) |
| **🗑️ Remove last field** | Quita el último campo agregado |
| **📤 Send embed** | Te pide elegir el canal y lo publica |
| **❌ Cancel** | Cierra el creador sin enviar nada |

**Uso paso a paso:**
1. Ejecutá `/embed-create`.
2. Completá los botones que necesites; la vista previa se actualiza sola.
3. Presioná **Send embed**, elegí el canal y listo.

**Precauciones:**
- Las imágenes se cargan por **URL pública** (terminada en `.png`, `.jpg`, `.gif`…). No se pueden subir archivos desde el creador.
- Límites de Discord: título 256 caracteres, descripción 4096, hasta **25 campos**.
- Si cerrás el panel o pasan **10 minutos** sin usarlo, expira y hay que empezar de nuevo; el trabajo no se guarda.
- Si el color es inválido se ignora y se mantiene el color anterior (azul de Discord por defecto).
- El bot necesita permiso para enviar mensajes y embeds en el canal de destino.

---

## Antispam

Protección automática contra bots comprometidos y spam. **Viene activada** en todos los servidores.

**Qué detecta:**

| Detección | Condición |
|---|---|
| Enlaces de scam | Mensaje con un dominio de la lista negra |
| Mensajes demasiado rápidos | **5 mensajes en 8 segundos** |
| Mensajes repetidos | El **mismo texto o archivo repetido 3 veces en 30 segundos** (aunque sea en distintos canales) |

**Qué hace al detectar:** borra el mensaje, **silencia al usuario 10 minutos** y avisa en el canal con un mensaje que se borra solo a los 10 segundos.

### `/antispam toggle`
Activa o desactiva el antispam en el servidor.
- **Parámetro:** `enabled` *(obligatorio)*: `True` o `False`. **Ejemplo:** `/antispam toggle enabled:False`

### `/antispam blacklist-add`
Agrega un dominio a la lista negra.
- **Parámetro:** `domain` *(obligatorio)*, solo el dominio, sin `https://` ni rutas. **Ejemplo:** `/antispam blacklist-add domain:free-nitro.xyz`

### `/antispam blacklist-list`
Muestra los dominios bloqueados. **Respuesta:** efímera.

**Precauciones:**
- ⚠️ **Los dominios agregados con `blacklist-add` viven en la memoria del bot y se pierden al reiniciarlo.** Solo permanecen los dominios que vienen por defecto en `cogs/antispam.py` (`DEFAULT_BAD_DOMAINS`). Para que sean permanentes hay que agregarlos en ese archivo.
- La coincidencia es por **dominio exacto**: bloquear `ejemplo.com` no bloquea `www.ejemplo.com` ni `login.ejemplo.com`; agregá cada variante.
- **Los usuarios con el permiso nativo Administrador nunca son sancionados.** Quienes solo tienen un rol de `/adminrole` **sí pueden ser sancionados** por el antispam.
- Un usuario que pega el mismo mensaje 3 veces legítimamente en 30 s (por ejemplo, copiando un código) será silenciado. Si el servidor necesita eso, ajustá los valores en `cogs/antispam.py`.
- Los archivos repetidos se detectan por **nombre de archivo**, no por contenido.
- El bot necesita los permisos **Gestionar mensajes** y **Moderar miembros**, y su rol debe estar por encima del de los usuarios.

---

## Honeypot (canal trampa)

Un canal oculto con un nombre tentador (por ejemplo `・free-nitro`) pensado para atrapar cuentas hackeadas y bots que escriben en todos los canales. **Quien escribe ahí es expulsado automáticamente** y se le borran los mensajes de las últimas 24 horas en todos los canales de texto.

### `/honeypot-setup`
Crea el canal trampa y lo deja activo.

| Parámetro | Descripción |
|---|---|
| `name` | Nombre del canal (por defecto `・free-nitro`) |
| `category` | Categoría donde crearlo (opcional) |

- **Respuesta:** efímera. **Ejemplo:** `/honeypot-setup name:・free-gift category:#Info`
- Dentro del canal, el bot deja un aviso explicando que es una trampa.

### `/honeypot-disable`
Desactiva el honeypot. **El canal no se borra**, pero deja de expulsar a quien escriba. Para eliminarlo, borrá el canal a mano.

**Precauciones:**
- ⚠️ **Es una expulsión inmediata y sin advertencia.** El canal debe estar **oculto para `@everyone`** (el comando ya lo configura así) y no debe darse acceso a ningún miembro real.
- Si alguien con un rol que *sí ve* el canal escribe ahí por error, será expulsado. No asignes permisos de lectura sobre ese canal a roles de miembros.
- **Los administradores (permiso nativo) nunca son expulsados.**
- Solo hay **un honeypot activo** por servidor. Si ejecutás `/honeypot-setup` otra vez se crea un canal nuevo y el anterior deja de funcionar como trampa, pero **sigue existiendo**: hay que borrarlo.
- El bot necesita los permisos **Expulsar miembros**, **Gestionar mensajes**, **Gestionar canales** y **Leer el historial** en todos los canales.
- Solo se borran los mensajes de las **últimas 24 horas**, y hasta 500 por canal. Lo anterior no se toca.

---

## Sorteos

### `/giveaway`
Publica un sorteo con un botón **🎉 Join**. Al terminar el tiempo, el bot elige ganadores al azar y los menciona.

| Parámetro | Descripción |
|---|---|
| `prize` *(obligatorio)* | Qué se sortea |
| `duration` *(obligatorio)* | Duración con unidades `s`, `m`, `h`, `d`; se pueden combinar: `30m`, `2h`, `1d`, `1h30m` |
| `winners` | Cantidad de ganadores (por defecto 1) |

- **Respuesta:** efímera (confirmación); el sorteo se publica en el canal actual.
- **Ejemplo:** `/giveaway prize:Rango VIP duration:2d winners:2`

**Cómo funciona:**
- Cada usuario participa **una sola vez** (si vuelve a presionar el botón, el bot se lo indica).
- Un proceso revisa cada **30 segundos** si algún sorteo terminó, así que el resultado puede demorar hasta medio minuto.
- Al finalizar se anuncia el resultado en el mismo canal. Si no hay participantes válidos, lo informa.
- Los participantes que **ya no están en el servidor** al terminar se descartan; si quedan menos candidatos que ganadores, se sortea entre los disponibles.
- Los botones siguen funcionando tras reiniciar el bot.

### `/giveaway-end`
Termina un sorteo ahora mismo y sortea a los ganadores.

| Parámetro | Descripción |
|---|---|
| `giveaway_id` *(obligatorio)* | ID numérico del sorteo (columna `id` de la tabla `giveaways`) |

- **Ejemplo:** `/giveaway-end giveaway_id:4`
- **Precaución:** actualmente el bot **no muestra el ID** del sorteo al crearlo. Se consulta en Supabase → Table Editor → `giveaways` → columna `id`.

**Precauciones generales de sorteos:**
- Una duración inválida (por ejemplo `diez minutos`) da error y no crea el sorteo.
- No hay comando para cancelar ni repetir (*reroll*) un sorteo.
- No se verifican requisitos para participar (roles, nivel, etc.): puede entrar cualquiera que vea el canal.

---

## Roles automáticos y por reacción

### `/joinrole add` · `/joinrole remove`
Roles que se asignan solos a cada persona que entra al servidor.

| Comando | Parámetro | Descripción |
|---|---|---|
| `add` | `role` *(obligatorio)* | Rol a asignar a los nuevos miembros |
| `remove` | `role` *(obligatorio)* | Rol a dejar de asignar |

- **Respuesta:** efímera. **Ejemplo:** `/joinrole add role:@Nuevo`
- **Precauciones:** el **rol del bot debe estar por encima** del rol a asignar y el bot necesita el permiso **Gestionar roles**. Nunca uses un rol con permisos de moderación. Afecta solo a quienes entren **después** de configurarlo, no a los miembros actuales. Requiere el *Server Members Intent* activado.

### `/reactionrole add`
Vincula un emoji de un mensaje existente con un rol. Al reaccionar se entrega el rol y **al quitar la reacción se retira**.

| Parámetro | Descripción |
|---|---|
| `message_id` *(obligatorio)* | ID del mensaje (Modo desarrollador activado → clic derecho en el mensaje → Copiar ID) |
| `emoji` *(obligatorio)* | Emoji estándar o uno que exista en el servidor |
| `role` *(obligatorio)* | Rol que se entrega |

- **Respuesta:** efímera. **Ejemplo:** `/reactionrole add message_id:123456789012345678 emoji:🔥 role:@Gamer`

**Cómo usarlo bien:**
1. Publicá un mensaje (por ejemplo, con `/embed-create`) explicando qué emoji da qué rol.
2. Copiá el ID del mensaje.
3. Ejecutá `/reactionrole add` una vez por cada emoji/rol. El bot reacciona al mensaje con el emoji por vos.

**Precauciones:**
- El bot busca el mensaje en los canales de texto que puede ver; si no lo encuentra, avisa.
- Con emojis personalizados, usá uno del **mismo servidor**.
- El **rol del bot debe estar por encima** del rol entregado y debe tener **Gestionar roles**.
- No hay comando para eliminar un reaction role: se borra la fila en la tabla `reaction_roles` de Supabase.
- Si borrás el mensaje original, el vínculo queda inactivo en la base de datos.

---

# 🤖 Funciones automáticas (sin comando)

| Función | Qué hace |
|---|---|
| **Antispam** | Revisa cada mensaje (ver [Antispam](#antispam)) |
| **Honeypot** | Expulsa a quien escriba en el canal trampa |
| **Triggers** | Responde a las palabras configuradas con `/trigger add` |
| **Join roles** | Asigna roles al entrar un miembro |
| **Reaction roles** | Da y quita roles según reacciones |
| **Sorteos** | Cierra los sorteos cuando se cumple el tiempo |
| **Contador de miembros** | Actualiza el nombre del canal cada 10 minutos |
| **Presencia** | Muestra el estado "viendo el mapa del servidor 🗺️" |

---

# 🗄️ Base de datos

El bot guarda su información en Supabase. Tablas principales:

| Tabla | Qué guarda |
|---|---|
| `guild_config` | Roles de administración, join roles, antispam, honeypot, canal de logs de tickets y canal del contador |
| `ticket_panels` / `tickets` | Paneles y tickets abiertos/cerrados |
| `custom_triggers` / `custom_commands` | Triggers y comandos personalizados |
| `reaction_roles` | Vínculos emoji → rol |
| `giveaways` / `giveaway_entries` | Sorteos y participantes |
| `warns` | Advertencias |

- `supabase_schema.sql` crea todas las tablas (se puede volver a ejecutar sin perder datos).
- `reset_data.sql` **borra todos los datos** del bot y conserva las tablas. **Es irreversible**: elimina también la configuración de roles de administración, honeypot, contador y tickets.

---

# ⚠️ Precauciones generales

- **Permisos del bot:** para que todo funcione necesita, como mínimo, Gestionar roles, Gestionar canales, Expulsar miembros, Banear miembros, Moderar miembros, Gestionar mensajes, Enviar mensajes, Insertar enlaces, Leer el historial y Ver canales. Lo más simple es darle **Administrador**.
- **Jerarquía de roles:** mové el rol del bot **lo más arriba posible** (pero por debajo del rol del dueño). Si está por debajo de otros roles, no podrá sancionarlos ni entregarles roles.
- **Intents:** en el Portal de Desarrolladores de Discord deben estar activados *Server Members Intent* y *Message Content Intent*; sin ellos fallan los triggers, el antispam y los join roles.
- **Claves secretas:** el token del bot y la `service_role key` de Supabase dan control total. No las compartas ni las subas a un repositorio público. Si se filtran, regeneralas.
- **Acciones irreversibles:** `/ban`, `/clear`, cierre de tickets, el honeypot y `reset_data.sql` no se pueden deshacer.
- **Comandos nuevos:** si agregás o renombrás comandos, pueden tardar en aparecer. Con `GUILD_ID` configurado aparecen al instante en ese servidor; sin él, la sincronización global puede tardar hasta 1 hora.
- **Datos de otros servidores:** el bot está pensado para un solo servidor. Los comandos personalizados se registran de forma global, así que se compartirían entre servidores si lo invitás a más de uno.

---

# 🛠️ Problemas frecuentes

| Problema | Causa probable y solución |
|---|---|
| "No tenés permisos de administración" | No tenés el permiso Administrador ni un rol de `/adminrole`. Pedile al dueño que ejecute `/adminrole add`. |
| El bot no sanciona / "Missing Permissions" | El rol del bot está por debajo del usuario, o le falta el permiso de Discord correspondiente. |
| Un comando nuevo no aparece | Esperá unos segundos, reiniciá Discord (`Ctrl+R`) o revisá `GUILD_ID`. |
| Los triggers y el antispam no hacen nada | Falta el *Message Content Intent* en el Portal de Desarrolladores. |
| El contador de miembros muestra `0` | El ID de rol en `MIEMBRO_ROLE_ID` (`cogs/general.py`) no es el de tu servidor. |
| `/counter-setup` da error de base de datos | Falta la columna `member_counter_channel_id`; ejecutá `supabase_schema.sql` de nuevo. |
| Un `/customcommand` no responde | Su nombre coincide con un comando existente; borrá el registro con `/customcommand remove` y elegí otro nombre. |
| El sorteo terminó pero no anunció ganador | El canal fue borrado o el bot ya no lo ve. |
| Un dominio del antispam "se olvidó" | `blacklist-add` es temporal; agregalo a `DEFAULT_BAD_DOMAINS` en el código. |