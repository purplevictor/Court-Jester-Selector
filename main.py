import os
import logging

import asyncpg

from telegram import Update
from telegram.ext import Application

DEBUG = os.environ.get("DEBUG", "0") == "1"

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_BOT_ADMINISTRATOR_IDS = [int(x) for x in os.environ["TG_BOT_ADMINISTRATOR_IDS"].split(",") if len(x) > 0 and x.isdigit()]

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO
)

logger = logging.getLogger(__name__)

db_pool = None

async def on_startup(application: Application):
    global db_pool
    db_pool = await asyncpg.create_pool(
        min_size=1,
        max_size=5,
        max_inactive_connection_lifetime=60,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    logger.info("Pool created")

async def on_shutdown(application: Application):
    await db_pool.close()
    logger.info("Pool closed")

def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()

    application.post_init = on_startup
    application.post_shutdown = on_shutdown

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()