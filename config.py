import os

DEBUG = os.environ.get("DEBUG", "0") == "1"

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_BOT_ADMINISTRATOR_IDS = [int(x) for x in os.environ["TG_BOT_ADMINISTRATOR_IDS"].split(",") if len(x) > 0 and x.isdigit()]

DB_URI = os.environ["DB_URI"]

MAX_WEIGHT = int(os.environ.get("MAX_WEIGHT", 5))
DEFAULT_WEIGHT = int(os.environ.get("DEFAULT_WEIGHT", 3))

if MAX_WEIGHT < 1:
    raise ValueError("MAX_WEIGHT must be greater than or equal to 1.")
if DEFAULT_WEIGHT < 1:
    raise ValueError("DEFAULT_WEIGHT must be greater than or equal to 1.")
if DEFAULT_WEIGHT > MAX_WEIGHT:
    raise ValueError("DEFAULT_WEIGHT must be less than or equal to MAX_WEIGHT.")

PRIVATE_CHAT_TYPES = ["private"]
GROUP_CHAT_TYPES = ["group", "supergroup"]
CHANNEL_CHAT_TYPES = ["channel"]

USER_MEMBER_STATUS = ["creator", "administrator", "member", "restricted"]
NON_MEMBER_USER_STATUS = ["left", "kicked"]