# The Isle: Evrima Discord RCON Bot

A Discord bot for **The Isle: Evrima** game server management. Features RCON control, SFTP log parsing, Pterodactyl panel integration, player account linking, and kill feed/chat logging.

## How to Run

The workflow **"Start application"** runs `python main.py`. Start or restart it from the Replit interface.

The bot also starts a Flask keep-alive server on port 8080.

## Required Secrets

| Secret | Description |
|--------|-------------|
| `BOT_TOKEN` | Discord bot token from discord.com/developers |
| `RCON_PASS` | Password for RCON access to the game server |

## Environment Variables (currently set)

| Variable | Value |
|----------|-------|
| `DEFAULT_GUILDS` | 1506398572348965045 |
| `RCON_HOST` | 45.88.230.110 |
| `RCON_PORT` | 8888 |
| `BOT_PREFIX` | ! |

## Optional Features (disabled by default)

Configure these by adding environment variables / secrets:

- **FTP Log Parsing** — set `ENABLE_LOGGING=true` + `FTP_HOST`, `FTP_PORT`, `FTP_USER`, `FTP_PASS`, `FILE_PATH`, `CHATLOG_CHANNEL`, `KILLFEED_CHANNEL`, `ADMINLOG_CHANNEL`
- **Admin Injections** — set `ENABLE_INJECTIONS=true` + `ADMIN_FILE_PATH`
- **Pterodactyl Panel** — set `PTERO_ENABLE=true` + `PTERO_URL`, `PTERO_API`, `PTERO_SERVER`, `PTERO_WHITELIST`
- **Auto Restart** — set `ENABLE_RESTART=true` + `RESTART_CHANNEL`
- **Account Linking** — set `LINK_CHANNEL`

## Project Structure

```
main.py           — Bot entry point
keep_alive.py     — Flask server to keep the repl alive
util/
  config.py       — Loads all env vars / secrets
  coghandler.py   — Auto-loads cogs at startup
cogs/
  help.py         — Help command
  utility.py      — General utility commands
  ptero.py        — Pterodactyl panel cog
  pterocommand.py — Pterodactyl commands
  server/         — Server management (RCON, restart, whitelist, toggle, monitor)
  logging/        — Log parsers (chat, kills, players, admin)
  link/           — Player account linking
```

## User Preferences

- Keep existing project structure and stack.
