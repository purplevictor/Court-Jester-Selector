import os

PRIVATE_CHAT_TYPES = ("private",)
GROUP_CHAT_TYPES = (
    "group",
    "supergroup"
)

USER_MEMBER_STATUS = (
    "creator",
    "administrator",
    "member",
    "restricted",
)
NON_MEMBER_USER_STATUS = (
    "left", 
    "kicked",
)

UPDATE_PLAYER_WEIGHT_COMMAND = "update_player_weight"
UPDATE_PLAYER_WEIGHT_COMMAND_DESCRIPTION = "Update the weight of a player."

ALLOWED_UPDATES = (
    "message",
    "callback_query",
    "my_chat_member",
)

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]

TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS = tuple(
    status.strip()
    for status in os.environ.get("TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS", "creator,administrator").split(",")
    if status in ("creator", "administrator")
)

TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS = tuple(
    int(id)
    for id in os.environ.get("TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS", "").split(",")
    if len(id) > 0 and id.isdigit()
)

if not TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS and not TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS:
    raise ValueError("TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS and/or TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS must be defined.")

DB_URI = f"postgresql+asyncpg://{os.environ["DB_URI"]}"

MIN_WEIGHT = int(os.environ.get("MIN_WEIGHT", 1))

if MIN_WEIGHT < 0:
    raise ValueError(f"MIN_WEIGHT ({MIN_WEIGHT}) must be greater than or equal to 0.")

MAX_WEIGHT = int(os.environ.get("MAX_WEIGHT", 5))

if MAX_WEIGHT < MIN_WEIGHT:
    raise ValueError(f"MAX_WEIGHT ({MAX_WEIGHT}) must be greater than or equal to MIN_WEIGHT ({MIN_WEIGHT}).")

DEFAULT_WEIGHT = int(os.environ.get("DEFAULT_WEIGHT", 3))

if DEFAULT_WEIGHT < MIN_WEIGHT:
    raise ValueError(f"DEFAULT_WEIGHT ({DEFAULT_WEIGHT}) must be greater than or equal to MIN_WEIGHT ({MIN_WEIGHT}).")
if DEFAULT_WEIGHT > MAX_WEIGHT:
    raise ValueError(f"DEFAULT_WEIGHT ({DEFAULT_WEIGHT}) must be less than or equal to MAX_WEIGHT ({MAX_WEIGHT}).")

GROUPS_PER_PAGE = int(os.environ.get("GROUPS_PER_PAGE", 5))

if GROUPS_PER_PAGE < 0:
    raise ValueError(f"GROUPS_PER_PAGE ({GROUPS_PER_PAGE}) must be greater than or equal to 0.")

PLAYERS_PER_PAGE = int(os.environ.get("PLAYERS_PER_PAGE", 5))

if PLAYERS_PER_PAGE < 0:
    raise ValueError(f"PLAYERS_PER_PAGE ({PLAYERS_PER_PAGE}) must be greater than or equal to 0.")

MIN_PLAYERS = int(os.environ.get("MIN_PLAYERS", 10))

if MIN_PLAYERS < 2:
    raise ValueError(f"MIN_PLAYERS ({MIN_PLAYERS}) must be greater than or equal to 2.")

NON_APPROVED_GROUP_MESSAGE = os.environ.get("NON_APPROVED_GROUP_MESSAGE", "🏰 Halt! This royal entertainment has not yet been sanctioned! The Court Jester Selector awaits approval from the kingdom's nobles before the foolery can commence.")
NOT_ENOUGH_PLAYERS_MESSAGE = os.environ.get("NOT_ENOUGH_PLAYERS_MESSAGE", "⚜️ Insufficient subjects detected in the realm! The Court requires a minimum of {min_players} participants before any royal proceedings or records can be accessed. Expand thy circle of jesters!")

PICK_PLAYER_COMMAND = os.environ.get("PICK_PLAYER_COMMAND", "crown_the_jester")
PICK_PLAYER_COMMAND_DESCRIPTION = os.environ.get("PICK_PLAYER_COMMAND_DESCRIPTION", "Crown today's jester.")
PICK_PLAYER_PICKED_PLAYER_MESSAGE = os.environ.get("PICK_PLAYER_PICKED_PLAYER_MESSAGE", "🎪 By royal decree, {username} is hereby appointed as today's Royal Entertainer! The throne awaits your foolery! 🎭")
SHOW_LEADERBOARD_COMMAND = os.environ.get("SHOW_LEADERBOARD_COMMAND", "court_leaderboard")
SHOW_LEADERBOARD_COMMAND_DESCRIPTION = os.environ.get("SHOW_LEADERBOARD_COMMAND_DESCRIPTION", "View the court rankings.")
LEADERBOARD_NOT_ENOUGH_PICKED_PLAYERS_MESSAGE = os.environ.get("LEADERBOARD_NOT_ENOUGH_PICKED_PLAYERS_MESSAGE", "📜 The royal court cannot establish a hierarchy of fools yet! More jesters must be selected before we can rank their foolery.")
LEADERBOARD_INTRO_MESSAGE = os.environ.get("LEADERBOARD_INTRO_MESSAGE", "🏆 Behold the Royal Jester Rankings! From the most frequently summoned fools to the rarely seen tricksters:")
LEADERBOARD_RANK_MESSAGE = os.environ.get("LEADERBOARD_RANK_MESSAGE", "{rank}. {username} - {draw_count}")
LEADERBOARD_OUTRO_MESSAGE = os.environ.get("LEADERBOARD_OUTRO_MESSAGE", "These are the top jesters of our noble court! May the odds forever favor the truly entertaining! 👑")
SHOW_PERSONAL_STATS_COMMAND = os.environ.get("SHOW_PERSONAL_STATS_COMMAND", "my_jester_stats")
SHOW_PERSONAL_STATS_COMMAND_DESCRIPTION = os.environ.get("SHOW_PERSONAL_STATS_COMMAND_DESCRIPTION", "Check your jester stats.")
PERSONAL_STATS_NO_PICKED_PLAYER_MESSAGE = os.environ.get("PERSONAL_STATS_NO_PICKED_PLAYER_MESSAGE", "🎭 Hark, {username}! The jester's hat has never graced thy noble head. You remain untouched by the royal selection. A blessing or a curse? Only time will tell!")
PERSONAL_STATS_MESSAGE = os.environ.get("PERSONAL_STATS_MESSAGE", "🃏 Hear this, {username}! You have entertained the court {draw_count} times as Jester, placing you at position {rank} among all court entertainers!")