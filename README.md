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
            <th>Possible values</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>TG_BOT_TOKEN</code></td>
            <td>Telegram Bot API token (from <a href="https://t.me/BotFather" target="_blank">@BotFather</a>).</td>
            <td>—</td>
            <td>✅</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS</code><sup>*</sup></td>
            <td>Comma-separated list of chat-member statuses granting admin rights (creator, administrator).</td>
            <td><code>creator,administrator</code></td>
            <td>❌</td>
            <td><code>creator</code>, <code>administrator</code></td>
        </tr>
        <tr>
            <td><code>TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS</code><sup>*</sup></td>
            <td>Comma-separated list of user IDs granting admin rights.</td>
            <td>—</td>
            <td>❌</td>
            <td>Integers</td>
        </tr>
        <tr>
            <td><code>DB_URI</code></td>
            <td>PostgreSQL database connection URI <strong>without</strong> the driver URL scheme.</td>
            <td>—</td>
            <td>✅</td>
            <td><code>user:password@host:port/database</code></td>
        </tr>
        <tr>
            <td><code>MIN_WEIGHT</code></td>
            <td>Minimum allowed weight (must be ≥ 0).</td>
            <td><code>1</code></td>
            <td>❌</td>
            <td>Integer ≥ 0</td>
        </tr>
        <tr>
            <td><code>MAX_WEIGHT</code></td>
            <td>Maximum allowed weight (must be ≥ <code>MIN_WEIGHT</code>).</td>
            <td><code>5</code></td>
            <td>❌</td>
            <td>Integer ≥ <code>MIN_WEIGHT</code></td>
        </tr>
        <tr>
            <td><code>DEFAULT_WEIGHT</code></td>
            <td>Default weight (between <code>MIN_WEIGHT</code> and <code>MAX_WEIGHT</code>).</td>
            <td><code>3</code></td>
            <td>❌</td>
            <td>Integer ∈ [<code>MIN_WEIGHT</code>, <code>MAX_WEIGHT</code>]</td>
        </tr>
        <tr>
            <td><code>GROUPS_PER_PAGE</code></td>
            <td>
                Number of groups displayed per page.
                <em>(when an admin in a private chat lists groups to change a player’s weight)</em>.
            </td>
            <td><code>5</code></td>
            <td>❌</td>
            <td>Integer ≥ 0</td>
        </tr>
        <tr>
            <td>
                <code>PLAYERS_PER_PAGE</code>
            </td>
            <td>
                Number of players displayed per page.
                <em>(when an admin in a private chat lists groups to change a player’s weight)</em>.
            </td>
            <td><code>5</code></td>
            <td>❌</td>
            <td>Integer ≥ 0</td>
        </tr>
        <tr>
            <td><code>MIN_PLAYERS</code></td>
            <td>Minimum number of players required to start (must be ≥ 2).</td>
            <td><code>10</code></td>
            <td>❌</td>
            <td>Integer ≥ 2</td>
        </tr>
        <tr>
            <td><code>NON_APPROVED_GROUP_MESSAGE</code></td>
            <td>Message shown when the group isn’t approved yet.</td>
            <td>
                <code>🏰 Halt! This royal entertainment has not yet been sanctioned! The Court Jester Selector awaits approval from the kingdom's nobles before the foolery can commence.</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>NOT_ENOUGH_PLAYERS_MESSAGE</code></td>
            <td>Message shown when there are fewer than <code>MIN_PLAYERS</code> players; uses <code>{min_players}</code>.</td>
            <td>
                <code>⚜️ Insufficient subjects detected in the realm! The Court requires a minimum of {min_players} participants before any royal proceedings or records can be accessed. Expand thy circle of jesters!</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>PICK_PLAYER_COMMAND</code></td>
            <td>Command to crown today’s jester.</td>
            <td><code>crown_the_jester</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>PICK_PLAYER_COMMAND_DESCRIPTION</code></td>
            <td>Description of the jester-crown command.</td>
            <td><code>Crown today's jester.</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>PICK_PLAYER_PICKED_PLAYER_MESSAGE</code></td>
            <td>Message announcing the crowned jester; replaces <code>{username}</code>.</td>
            <td>
                <code>🎪 By royal decree, {username} is hereby appointed as today's Royal Entertainer! The throne awaits your foolery! 🎭</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>SHOW_LEADERBOARD_COMMAND</code></td>
            <td>Command to show the leaderboard.</td>
            <td><code>court_leaderboard</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>SHOW_LEADERBOARD_COMMAND_DESCRIPTION</code></td>
            <td>Description of the leaderboard command.</td>
            <td><code>View the court rankings.</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>LEADERBOARD_NOT_ENOUGH_PICKED_PLAYERS_MESSAGE</code></td>
            <td>Message when not enough selections to build a ranking.</td>
            <td>
                <code>📜 The royal court cannot establish a hierarchy of fools yet! More jesters must be selected before we can rank their foolery.</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>LEADERBOARD_INTRO_MESSAGE</code></td>
            <td>Introductory text for the leaderboard.</td>
            <td>
                <code>🏆 Behold the Royal Jester Rankings! From the most frequently summoned fools to the rarely seen tricksters:</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>LEADERBOARD_RANK_MESSAGE</code></td>
            <td>Format for each leaderboard entry; uses <code>{rank}</code>, <code>{username}</code>, <code>{draw_count}</code>.</td>
            <td><code>{rank}. {username} - {draw_count}</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>LEADERBOARD_OUTRO_MESSAGE</code></td>
            <td>Closing message for the leaderboard.</td>
            <td>
                <code>These are the top jesters of our noble court! May the odds forever favor the truly entertaining! 👑</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>SHOW_PERSONAL_STATS_COMMAND</code></td>
            <td>Command to view personal jester stats.</td>
            <td><code>my_jester_stats</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>SHOW_PERSONAL_STATS_COMMAND_DESCRIPTION</code></td>
            <td>Description of the personal stats command.</td>
            <td><code>Check your jester stats.</code></td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>PERSONAL_STATS_NO_PICKED_PLAYER_MESSAGE</code></td>
            <td>Message if the user has never been crowned; replaces <code>{username}</code>.</td>
            <td>
                <code>🎭 Hark, {username}! The jester's hat has never graced thy noble head. You remain untouched by the royal selection. A blessing or a curse? Only time will tell!</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
        <tr>
            <td><code>PERSONAL_STATS_MESSAGE</code></td>
            <td>Message showing user’s stats; uses <code>{username}</code>, <code>{draw_count}</code>, <code>{rank}</code>.</td>
            <td>
                <code>🃏 Hear this, {username}! You have entertained the court {draw_count} times as Jester, placing you at position {rank} among all court entertainers!</code>
            </td>
            <td>❌</td>
            <td>—</td>
        </tr>
    </tbody>
</table>

<small><sup>\*</sup> At least one of <code>TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS</code> or <code>TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS</code> must be defined.</small>

```bash
uv run alembic upgrade head # Upgrade the database schema to the latest version
```

```bash
uv run main.py # Run the main.py
```
