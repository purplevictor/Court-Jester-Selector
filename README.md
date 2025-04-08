# Court-Jester-Selector

🃏 A fun Telegram bot that crowns a random friend as the day's entertainer based on weighted randomization. All hail the royal jester! 🎪

## Environment

### [uv](https://github.com/astral-sh/uv) - An extremely fast Python package and project manager, written in Rust.

## Dependencies

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Version</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>asyncpg</td>
            <td>0.30</td>
        </tr>
        <tr>
            <td>sqlmodel</td>
            <td>0.0.24</td>
        </tr>
        <tr>
            <td>alembic</td>
            <td>1.15.2</td>
        </tr>
        <tr>
            <td>python-telegram-bot[all]</td>
            <td>22.0</td>
        </tr>
    </tbody>
</table>

## How To Use It

```bash
gh repo clone j-about/Court-Jester-Selector # Clone the Court-Jester-Selector repository
```

```bash
cd Court-Jester-Selector # Move to the 'Court-Jester-Selector' directory
```

```bash
uv sync # Install all project dependencies
```

### Define environment variables

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Default value</th>
            <th>Required</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>DEBUG</td>
            <td>Set to <strong>1</strong> to enable debug mode with verbose logging</td>
            <td>0</td>
            <td>❌</td>
        </tr>
        <tr>
            <td>TG_BOT_TOKEN</td>
            <td>Telegram Bot API token obtained from BotFather</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>TG_BOT_ADMINISTRATOR_IDS</td>
            <td>Comma-separated list of Telegram user IDs with admin privileges</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>DB_USER</td>
            <td>PostgreSQL database username</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>DB_PASSWORD</td>
            <td>PostgreSQL database password</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>DB_HOST</td>
            <td>PostgreSQL server hostname</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>DB_PORT</td>
            <td>PostgreSQL server port</td>
            <td></td>
            <td>✅</td>
        </tr>
        <tr>
            <td>DB_NAME</td>
            <td>PostgreSQL database name</td>
            <td></td>
            <td>✅</td>
        </tr>
    </tbody>
</table>

```bash
uv run alembic upgrade head # Upgrade the database schema to the latest version
```

```bash
uv run main.py # Run the main.py
```
