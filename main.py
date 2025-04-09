import os
import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from telegram import (
    Update,
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeAllGroupChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.error import Forbidden

from config import (
    DEBUG,
    TG_BOT_TOKEN,
    TG_BOT_ADMINISTRATOR_IDS,
    DB_URI,
    MAX_WEIGHT,
    DEFAULT_WEIGHT,
    PRIVATE_CHAT_TYPES,
    GROUP_CHAT_TYPES,
    CHANNEL_CHAT_TYPES,
    USER_MEMBER_STATUS,
    NON_MEMBER_USER_STATUS
)
from models import *

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

    if my_chat_member_chat.type not in GROUP_CHAT_TYPES:
        return

    if my_chat_member.new_chat_member.user.id != context.bot.id:
        return

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

async def check_bot_and_player_statuses(context: ContextTypes.DEFAULT_TYPE) -> None:
    async with AsyncSession(engine) as session:
        result = await session.exec(select(Group).where(Group.status.in_(USER_MEMBER_STATUS)))
        groups = result.all()

        for group in groups:
            try:
                await context.bot.get_chat_member_count(chat_id=group.telegram_id)
                result = await session.exec(select(Player).where(Player.group_id == group.id))
                players = result.all()
                for player in players:
                    chat_member = await context.bot.get_chat_member(group.telegram_id, player.telegram_id)
                    status = chat_member.status
                    username = chat_member.user.username
                    if status != player.status:
                        player.status = status
                        player_telegram_id = player.telegram_id
                        await session.commit()
                        logger.info(f"Update player {player_telegram_id} with status {status}")
                        if status in USER_MEMBER_STATUS:
                            await context.bot.send_message(group.telegram_id, f"@{username} you are back in the game.")
            except Forbidden as e:
                status = e.message
                if group.status != status:
                    group.status = status
                    group_telegram_id = group.telegram_id
                    await session.commit()
                    logger.info(f"Update group {group_telegram_id} with status {status}")

async def join_the_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(update.effective_chat.type)
    if update.effective_chat.type in GROUP_CHAT_TYPES:
        async with AsyncSession(engine) as session:
            result = await session.exec(select(Group).where(Group.telegram_id == update.message.chat.id))
            group = result.one_or_none()
            result = await session.exec(select(Player).where(
                Player.telegram_id == update.message.from_user.id,
                Player.group_id == group.id
            ))
            player = result.one_or_none()
            chat_member = await context.bot.get_chat_member(update.message.chat.id, update.message.from_user.id)
            status = chat_member.status
            user = chat_member.user
            telegram_id = user.id
            username = user.username
            if not player:
                player = Player(status=status, group_id=group.id, telegram_id=telegram_id)
                session.add(player)
                await session.commit()
                logger.info(f"Add user {telegram_id} with status {status}")
                await update.message.reply_text(f"@{username} you have joined the game.")
            else:
                if status != player.status:
                    player.status = status
                    player_telegram_id = player.telegram_id
                    await session.commit()
                    logger.info(f"Update player {player_telegram_id} with status {status}")
                    await update.message.reply_text(f"@{username} you are back in the game.")
                else:
                    logger.info(f"User {telegram_id} already exists")
                    await update.message.reply_text(f"@{username} you have already joined the game.")

def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()

    application.add_handler(ChatMemberHandler(chat_member_update_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    job_queue = application.job_queue
    job_queue.run_repeating(check_bot_and_player_statuses, interval=3600, first=10)

    application.add_handler(CommandHandler("join_the_game", join_the_game))

    application.bot.set_my_commands([
        BotCommand("join_the_game", "Commandes pour les groupes")
    ], scope=BotCommandScopeAllGroupChats())

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()