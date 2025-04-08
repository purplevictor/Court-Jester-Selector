import os
import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes
from telegram.error import Forbidden

from models import *

DEBUG = os.environ.get("DEBUG", "0") == "1"

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_BOT_ADMINISTRATOR_IDS = [int(x) for x in os.environ["TG_BOT_ADMINISTRATOR_IDS"].split(",") if len(x) > 0 and x.isdigit()]

DB_URI = os.environ["DB_URI"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO
)

logger = logging.getLogger(__name__)

engine = create_async_engine(DB_URI, echo=True, future=True)

async def chat_member_update_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    my_chat_member = update.my_chat_member
    new_chat_member_status = my_chat_member.new_chat_member.status
    my_chat_member_chat = my_chat_member.chat

    if my_chat_member_chat.type not in ("group", "supergroup"):
        return

    if my_chat_member.new_chat_member.user.id != context.bot.id:
        return

    logger.info(
        f"Group update {my_chat_member_chat.id} : Telegram status = {new_chat_member_status}"
    )

    async with AsyncSession(engine) as session:
        result = await session.exec(select(Group).where(Group.telegram_id == my_chat_member_chat.id))
        group = result.one_or_none()

        if not group:
            group = Group(telegram_id=my_chat_member_chat.id, status=new_chat_member_status)
            session.add(group)

            logger.info(f"Add group {my_chat_member_chat.id} with status {new_chat_member_status}")
        else:
            group.status = new_chat_member_status

            logger.info(f"Update group {my_chat_member_chat.id} with status {new_chat_member_status}")

        await session.commit()

async def check_bot_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    async with AsyncSession(engine) as session:
        result = await session.exec(select(Group).where(Group.status.in_(["member", "administrator"])))
        groups = result.all()

        for group in groups:
            try:
                chat_member_count = await context.bot.get_chat_member_count(chat_id=group.telegram_id)
            except Forbidden as e:
                status = e.message
                if group.status != status:
                    group.status = status
                    await session.commit()

                    logger.info(f"Update group {group.telegram_id} with status {status}")

def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()

    application.add_handler(ChatMemberHandler(chat_member_update_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    job_queue = application.job_queue
    job_queue.run_repeating(check_bot_status, interval=3600, first=10)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()