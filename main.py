import asyncio
import logging
import random
import threading
from typing import (
    Sequence,
    Union
)
 
from flask import Flask
from sqlmodel import (
    and_,
    distinct,
    func,
    or_,
    select,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload
from telegram import (
    Bot,
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeAllGroupChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram._chatmember import (
    ChatMemberAdministrator,
    ChatMemberOwner,
    ChatMemberMember,
    ChatMemberRestricted,
)
 
from config import (
    ALLOWED_UPDATES,
    DB_URI,
    GROUP_CHAT_TYPES,
    GROUPS_PER_PAGE,
    LEADERBOARD_INTRO_MESSAGE,
    LEADERBOARD_NOT_ENOUGH_PICKED_PLAYERS_MESSAGE,
    LEADERBOARD_OUTRO_MESSAGE,
    LEADERBOARD_RANK_MESSAGE,
    MAX_WEIGHT,
    MIN_PLAYERS,
    MIN_WEIGHT,
    NON_APPROVED_GROUP_MESSAGE,
    NON_MEMBER_USER_STATUS,
    NOT_ENOUGH_PLAYERS_MESSAGE,
    PERSONAL_STATS_MESSAGE,
    PERSONAL_STATS_NO_PICKED_PLAYER_MESSAGE,
    PICK_PLAYER_COMMAND,
    PICK_PLAYER_COMMAND_DESCRIPTION,
    PICK_PLAYER_PICKED_PLAYER_MESSAGE,
    PLAYERS_PER_PAGE,
    PRIVATE_CHAT_TYPES,
    SHOW_LEADERBOARD_COMMAND,
    SHOW_LEADERBOARD_COMMAND_DESCRIPTION,
    SHOW_PERSONAL_STATS_COMMAND,
    SHOW_PERSONAL_STATS_COMMAND_DESCRIPTION,
    TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS,
    TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS,
    TG_BOT_TOKEN,
    UPDATE_PLAYER_WEIGHT_COMMAND,
    UPDATE_PLAYER_WEIGHT_COMMAND_DESCRIPTION,
    USER_MEMBER_STATUS,
)
from models import (
    Draw,
    Group,
    Player,
)
 
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
 
logger = logging.getLogger(__name__)
 
engine = create_async_engine(DB_URI, echo=True)
 
async def set_admin_commands(bot: Bot, chat_members: Sequence[Union[ChatMemberOwner, ChatMemberAdministrator, int]]) -> None:
    admin_commands = [
        BotCommand(UPDATE_PLAYER_WEIGHT_COMMAND, UPDATE_PLAYER_WEIGHT_COMMAND_DESCRIPTION)
    ]
    set_admin_tasks = []
    if all(isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)) for chat_member in chat_members):
        set_admin_tasks = [
            bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=chat_member.user.id)
            )
            for chat_member in chat_members
            if chat_member.status in TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS
        ]
    elif all(isinstance(chat_member, int) for chat_member in chat_members):
        set_admin_tasks = [
            bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=chat_member)
            )
            for chat_member in chat_members
        ]
    if set_admin_tasks:
        await asyncio.gather(*set_admin_tasks)
    return
 
 
async def bot_chat_member_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_member = update.my_chat_member
    status = chat_member.new_chat_member.status
    chat = chat_member.chat
    telegram_id = chat.id
    telegram_title = chat.title
    message = update.message
    bot = context.bot
 
    if chat.type in GROUP_CHAT_TYPES and chat_member.new_chat_member.user.id == bot.id:
        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(Group)
                .where(Group.telegram_id == telegram_id)
            )
            group = result.one_or_none()
 
            added_group = False
 
            if not group:
                approved = True if TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS else False
                if status in USER_MEMBER_STATUS:
                    group = Group(status=status, telegram_id=telegram_id, telegram_title=telegram_title, approved=approved)
                    session.add(group)
                    added_group = True
            else:
                if message:
                    if message.migrate_to_chat_id:
                        group.telegram_id = message.migrate_to_chat_id
                    elif message.migrate_from_chat_id:
                        group.telegram_id = message.chat.id
                group.status = status
                group.telegram_title = telegram_title
 
 
            if group:
                await session.commit()
                await session.refresh(group)
                logger.info(group.added if added_group else group.updated)
 
            if added_group:
                if group.approved:
                    players = []
 
                    if TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS:
                        chat_administrators = await bot.get_chat_administrators(chat_id=group.telegram_id)
                        for chat_administrator in chat_administrators:
                            user = chat_administrator.user
                            if user.id not in TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS:
                                player = Player(
                                    status=chat_administrator.status,
                                    group_id=group.id,
                                    telegram_id=user.id,
                                    telegram_first_name=user.first_name,
                                    telegram_last_name=user.last_name,
                                    telegram_username=user.username
                                )
                                players.append(player)
 
                    get_chat_member_tasks = [
                        bot.get_chat_member(chat_id=group.telegram_id, user_id=chat_administrator_user_id)
                        for chat_administrator_user_id in TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS
                    ]
 
                    if get_chat_member_tasks:
                        chat_members = await asyncio.gather(*get_chat_member_tasks, return_exceptions=True)
                        for chat_member in chat_members:
                            if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember, ChatMemberRestricted)):
                                user = chat_member.user
                                player = Player(
                                    status=chat_member.status,
                                    group_id=group.id,
                                    telegram_id=user.id,
                                    telegram_first_name=user.first_name,
                                    telegram_last_name=user.last_name,
                                    telegram_username=user.username
                                )
                                players.append(player)
 
                    session.add_all(players)
                    await session.commit()
                    for player in players:
                        await session.refresh(player, attribute_names=["group"])
                        logger.info(player.added)
 
                    if TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS:
                        if chat_administrators:
                            await set_admin_commands(bot, chat_administrators)
                elif TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS:
                    text = f"🤖 Installed on {group.telegram_title} group (id: {group.id}, telegram_id: {group.telegram_id})."
 
                    inline_keyboard = [
                        [
                            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{group.id}"),
                            InlineKeyboardButton("❌ Reject",  callback_data=f"reject:{group.id}")
                        ]
                    ]
 
                    reply_markup = InlineKeyboardMarkup(inline_keyboard)
 
                    get_chat_member_tasks = [
                        bot.get_chat_member(chat_id=chat_administrator_user_id, user_id=chat_administrator_user_id)
                        for chat_administrator_user_id in TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS
                    ]
 
                    chat_members = await asyncio.gather(*get_chat_member_tasks, return_exceptions=True)
                    send_message_tasks = [
                        bot.send_message(
                            chat_id=chat_member.user.id,
                            text=text,
                            reply_markup=reply_markup
                        )
                        for chat_member in chat_members
                        if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember, ChatMemberRestricted))
                    ]
 
                    if send_message_tasks:
                        sended_messages = await asyncio.gather(*send_message_tasks)
                        approval_messages = {sended_message.chat.id: sended_message.message_id for sended_message in sended_messages}
                        group.approval_messages = approval_messages
                        await session.commit()
                        await session.refresh(group)
                        logger.info(f"Approval messages added to {telegram_title} group (id: {group.id}, telegram_id: {telegram_id}).")
                    else:
                        await session.delete(group)
                        await session.commit()
    return
 
async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type in GROUP_CHAT_TYPES:
        message = update.message
        user_id = message.from_user.id
        chat_id = message.chat.id
        bot = context.bot
        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(Group, Player)
                .join(Player, and_(
                    Group.id == Player.group_id,
                    Player.telegram_id == user_id
                ), isouter=True)
                .where(
                    Group.telegram_id == chat_id,
                    Group.approved == True
                )
            )
            row = result.one_or_none()
            if row:
                group, player = row
                chat_member = await bot.get_chat_member(chat_id, user_id)
                user = chat_member.user
                added_player = False
                updated_player = False
                if not player:
                    player = Player(
                        status=chat_member.status,
                        group_id=group.id,
                        telegram_id=user.id,
                        telegram_first_name=user.first_name,
                        telegram_last_name=user.last_name,
                        telegram_username=user.username
                    )
                    session.add(player)
                    added_player = True
                elif player.status != chat_member.status or player.telegram_first_name != user.first_name or player.telegram_last_name != user.last_name or player.telegram_username != user.username:
                    player.status = chat_member.status
                    player.telegram_first_name = user.first_name
                    player.telegram_last_name = user.last_name
                    player.telegram_username = user.username
                    updated_player = True
                if added_player or updated_player:
                    await session.commit()
                    await session.refresh(player, attribute_names=["group"])
                    logger.info(player.added if added_player else player.updated)
                await set_admin_commands(bot, [chat_member])
    return
 
def protect(func_):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        chat_id = update.effective_chat.id
        message = update.message
        user_id = message.from_user.id
        bot = context.bot
        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(
                    Group,
                    func.count(distinct(Player.id)).label("players_count"),
                    func.count(distinct(Draw.id)).label("draws_count")
                )
                .join(Player, Group.id == Player.group_id, isouter=True)
                .join(Draw, Group.id == Draw.group_id, isouter=True)
                .where(
                    Group.telegram_id == chat_id,
                    Group.approved == True
                )
                .group_by(Group.id)
            )
            row = result.one_or_none()
            if row:
                group, players_count, draws_count = row
                if players_count < MIN_PLAYERS and draws_count == 0:
                    await message.reply_text(NOT_ENOUGH_PLAYERS_MESSAGE.format(min_players=MIN_PLAYERS))
                    return
                else:
                    result = await session.exec(
                        select(Player)
                        .where(
                            Player.telegram_id == user_id,
                            Player.group_id == group.id
                        )
                    )
                    player = result.one_or_none()
                    chat_member = await bot.get_chat_member(chat_id, user_id)
                    user = chat_member.user
                    added_player = False
                    updated_player = False
                    if not player:
                        player = Player(
                            status=chat_member.status,
                            group_id=group.id,
                            telegram_id=user.id,
                            telegram_first_name=user.first_name,
                            telegram_last_name=user.last_name,
                            telegram_username=user.username
                        )
                        session.add(player)
                        added_player = True
                    elif player.status != chat_member.status or player.telegram_first_name != user.first_name or player.telegram_last_name != user.last_name or player.telegram_username != user.username:
                        player.status = chat_member.status
                        player.telegram_first_name = user.first_name
                        player.telegram_last_name = user.last_name
                        player.telegram_username = user.username
                        updated_player = True
                    if added_player or updated_player:
                        await session.commit()
                        await session.refresh(player, attribute_names=["group"])
                        logger.info(player.added if added_player else player.updated)
                    await set_admin_commands(bot, [chat_member])
 
                    return await func_(update, context, *args, **kwargs)
            else:
                await message.reply_text(NON_APPROVED_GROUP_MESSAGE)
                return
    return wrapper
 
async def approve_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
 
    data = query.data.split(":")
    action = data[0]
    group_id = int(data[1])
 
    user = query.from_user
 
    bot = context.bot
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Group)
            .where(Group.id == group_id)
        )
        group = result.one()
 
        group_id = group.id
        telegram_id = group.telegram_id
        telegram_title = group.telegram_title
        approval_messages = group.approval_messages
 
        approved = (action == "approve")
 
        group.approved = True if approved else await bot.leave_chat(chat_id=group.telegram_id)
 
        common_text = f"{'✅' if approved else '❌'} Group {telegram_title} (id: {group_id}, telegram_id: {telegram_id}) {'approved' if approved else 'rejected'}"
 
        await query.edit_message_text(f"{common_text}.")
 
        display_name = f"@{user.username}" if user.username else (f"{user.first_name} {user.last_name}" if user.last_name else user.first_name)
 
        edit_message_text_tasks = []
        get_chat_member_tasks = []
        players = []
 
        for chat_administrator_user_id, message_id in approval_messages.items():
            if query.message.message_id != message_id:
                edit_message_text_tasks.append(
                    bot.edit_message_text(
                        chat_id=chat_administrator_user_id,
                        message_id=message_id,
                        text=f"{common_text} by {display_name}."
                    )
                )
            if approved:
                get_chat_member_tasks.append(
                    bot.get_chat_member(chat_id=telegram_id, user_id=chat_administrator_user_id)
                )
 
        if edit_message_text_tasks:
            await asyncio.gather(*edit_message_text_tasks, return_exceptions=True)
 
        if approved and get_chat_member_tasks:
            chat_members = await asyncio.gather(*get_chat_member_tasks)
 
            for chat_member in chat_members:
                if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember, ChatMemberRestricted)):
                    user = chat_member.user
                    players.append(
                        Player(
                            status=chat_member.status,
                            group_id=group.id,
                            telegram_id=user.id,
                            telegram_first_name=user.first_name,
                            telegram_last_name=user.last_name,
                            telegram_username=user.username
                        )
                    )
 
        if approved:
            group.approval_messages = None
            if players:
                session.add_all(players)
        else:
            await session.delete(group)
 
        await session.commit()
 
        logger.info(f"Group {telegram_title} (id: {group_id}, telegram_id: {telegram_id}) {'approved' if approved else 'rejected'} by {display_name} (telegram_id: {user.id}).")
 
        for player in players:
            await session.refresh(player, attribute_names=["group"])
            logger.info(player.added)
 
async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type in PRIVATE_CHAT_TYPES:
        message = update.message
 
        query = update.callback_query
        page = int(query.data.split(":")[1]) if query else 0
        offset = page * GROUPS_PER_PAGE
 
        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(Group)
                .join(Player, Group.id == Player.group_id)
                .where(
                    and_(
                        Group.status.in_(USER_MEMBER_STATUS),
                        Group.approved == True,
                        Player.telegram_id == update.effective_user.id,
                        or_(
                            Player.status.in_(TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_STATUS),
                            Player.telegram_id.in_(TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS)
                        )
                    )
                )
                .order_by(Group.telegram_title.asc())
                .offset(offset)
                .limit(GROUPS_PER_PAGE)
            )
            groups = result.all()
 
            if not groups:
                await message.reply_text("❌ This bot is not installed or approved on any group.")
                return
 
            inline_keyboard = []
 
            for group in groups:
                inline_keyboard.append([InlineKeyboardButton(group.telegram_title, callback_data=f"show_players_in_group:{group.id}")])
 
            total_count_result = await session.exec(
                select(func.count())
                .select_from(Group)
                .where(
                    Group.status.in_(USER_MEMBER_STATUS),
                    Group.approved == True
                )
            )
            total_count = total_count_result.one()
 
            pagination_buttons = []
            if page > 0:
                pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"show_groups_page:{page - 1}"))
            if total_count > offset + GROUPS_PER_PAGE:
                pagination_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"show_groups_page:{page + 1}"))
 
            if pagination_buttons:
                inline_keyboard.append(pagination_buttons)
 
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            
            text = "👥 Select a group :"
            if query:
                await query.edit_message_text(text=text, reply_markup=reply_markup)
            else:
                await message.reply_text(text=text, reply_markup=reply_markup)
    return
 
async def show_players_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
 
    data = query.data.split(":")
    group_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0
    offset = page * PLAYERS_PER_PAGE
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.players))
        )
        group = result.one()
        context.user_data["group"] = group
 
        if not group.players:
            await query.edit_message_text("❌ No chat member is a player.")
            return
 
        inline_keyboard = []
 
        for player in group.players:
            inline_keyboard.append([InlineKeyboardButton(f"{player.display_name()}", callback_data=f"select_player:{player.id}")])
 
        total_count_result = await session.exec(
            select(func.count())
            .select_from(Player)
            .where(Player.group_id == group_id)
            .where(Player.status.in_(USER_MEMBER_STATUS))
        )
        total_count = total_count_result.one()
 
        pagination_buttons = []
        if page > 0:
            pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"show_players_in_group:{group_id}:{page - 1}"))
        if total_count > offset + PLAYERS_PER_PAGE:
            pagination_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"show_players_in_group:{group_id}:{page + 1}"))
 
        if pagination_buttons:
            inline_keyboard.append(pagination_buttons)
 
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await query.edit_message_text(text="👤 Select a player:", reply_markup=reply_markup)
    return
 
async def ask_player_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
 
    player_id = int(query.data.split(":")[1])
 
    group = context.user_data["group"]
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Player)
            .where(
                Player.id == player_id,
                Player.group_id == group.id
            )
            .options(selectinload(Player.group))
        )
        player = result.one()
 
        context.user_data["player"] = player
 
    inline_keyboard_buttons = [
        InlineKeyboardButton(text=str(weight), callback_data=f"weight:{weight}")
        for weight in range(MIN_WEIGHT, MAX_WEIGHT + 1)
    ]
 
    inline_keyboard = [
        inline_keyboard_buttons[i:i+3]
        for i in range(0, len(inline_keyboard_buttons), 3)
    ]
 
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
 
    await query.edit_message_text(text=f"ℹ️ {player.display_name()}'s current weight in the {group.telegram_title} group is {player.weight}.\r\n⚖️ Set a new weight between {MIN_WEIGHT} and {MAX_WEIGHT}:", reply_markup=reply_markup)
 
 
async def update_player_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
 
    weight = int(query.data.split(":")[1])
 
    group = context.user_data["group"]
    player = context.user_data["player"]
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Player)
            .where(
                Player.id == player.id,
                Player.group_id == group.id
            )
            .options(selectinload(Player.group))
        )
        player = result.one()
        if weight != player.weight:
            player.weight = weight
            await session.commit()
            await session.refresh(player, attribute_names=["group"])
            await query.edit_message_text(text=f"✅ {player.display_name()}'s current weight in the {group.telegram_title} group is now {weight}.")
        else:
            await query.edit_message_text(text=f"ℹ️ {player.display_name()}'s weight in the {group.telegram_title} group is already {weight}.")
    
    context.user_data.clear()
 
@protect
async def pick_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    bot = context.bot
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Group)
            .where(Group.telegram_id == chat_id)
        )
        group = result.one()
 
        result = await session.exec(
            select(Draw)
            .where(
                Draw.draw_date == func.current_date(),
                Draw.group_id == group.id
            )
            .options(
                selectinload(Draw.player)
                .selectinload(Player.group)
            )
        )
        draw = result.one_or_none()
 
        added_draw = False
 
        if not draw:
            result = await session.exec(
                select(Player)
                .where(
                    Player.status.in_(USER_MEMBER_STATUS),
                    Player.group_id == group.id
                )
            )
            players = result.all()
 
            while True:
                picked_player = random.choices(
                    population=players,
                    weights=[player.weight for player in players],
                    k=1
                )[0]
 
                chat_member = await bot.get_chat_member(group.telegram_id, picked_player.telegram_id)
                status = chat_member.status
                user = chat_member.user
                first_name = user.first_name
                last_name = user.last_name
                username = user.username
 
                if status != picked_player.status or picked_player.telegram_first_name != first_name or picked_player.telegram_last_name != last_name or picked_player.telegram_username != username:
                    picked_player.status = status
                    picked_player.telegram_first_name = first_name
                    picked_player.telegram_last_name = last_name
                    picked_player.telegram_username = username
                    await session.commit()
                    await session.refresh(picked_player, attribute_names=["group"])
                    logger.info(picked_player.updated)
                
                if status in USER_MEMBER_STATUS:
                    break
 
                players = [player for player in players if player.id != picked_player.id]
 
            draw = Draw(
                group_id=group.id,
                player_id=picked_player.id
            )
            session.add(draw)
            await session.commit()
            await session.refresh(draw, attribute_names=["group", "player"])
            await session.refresh(draw.player, attribute_names=["group"])
            logger.info(draw.added)
            added_draw = True
        else:
            chat_member = await bot.get_chat_member(chat_id, draw.player.telegram_id)
    
        text = PICK_PLAYER_PICKED_PLAYER_MESSAGE.format(username=draw.player.display_name(without_at=not added_draw))
        await update.message.reply_text(text)
 
@protect
async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(
                func.rank().over(order_by=func.count(Draw.id).desc()).label("rank"),
                Player,
                func.count(Draw.id).label("draw_count")
            )
            .join(Group, Player.group_id == Group.id)
            .join(Draw, Player.id == Draw.player_id)
            .where(
                Player.status.in_(USER_MEMBER_STATUS),
                Group.telegram_id == chat_id
            )
            .group_by(
                Player
            )
            .order_by(func.count(Draw.id).desc())
            .limit(10)
        )
        leaders = result.all()
        if len(leaders) > 1:
            text = LEADERBOARD_INTRO_MESSAGE
            if len(text):
                text += "\r\n"
 
            get_chat_member_tasks = [context.bot.get_chat_member(chat_id, leader.Player.telegram_id) for leader in leaders]
            chat_members = await asyncio.gather(*get_chat_member_tasks)
 
            players = []
 
            for leader, chat_member in zip(leaders, chat_members):
                status = chat_member.status
                user = chat_member.user
                first_name = user.first_name
                last_name = user.last_name
                username = user.username
                if leader.Player.status != status or leader.Player.telegram_first_name != first_name or leader.Player.telegram_last_name != last_name or leader.Player.telegram_username != username:
                    leader.Player.status = status
                    leader.Player.telegram_first_name = first_name
                    leader.Player.telegram_last_name = last_name
                    leader.Player.telegram_username = username
                    players.append(leader.Player)
                text += LEADERBOARD_RANK_MESSAGE.format(
                    rank=leader.rank,
                    username=leader.Player.display_name(without_at=True),
                    draw_count=leader.draw_count
                ) + "\r\n"
            text += LEADERBOARD_OUTRO_MESSAGE
 
            if players:
                session.add_all(players)
                await session.commit()
                for player in players:
                    await session.refresh(player, attribute_names=["group"])
                    logger.info(player.updated)
                for player in players:
                    if player.status in NON_MEMBER_USER_STATUS:
                        return await show_leaderboard(update, context)
 
            await update.message.reply_text(text)
        else:
            await update.message.reply_text(LEADERBOARD_NOT_ENOUGH_PICKED_PLAYERS_MESSAGE)
    return
 
@protect
async def show_personal_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    user_id = message.from_user.id
 
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(
                Player,
                func.count(Draw.id).label("draw_count")
            )
            .join(Group, Player.group_id == Group.id)
            .join(Draw, Player.id == Draw.player_id)
            .where(
                Player.status.in_(USER_MEMBER_STATUS),
                Group.telegram_id == chat_id
            )
            .group_by(
                Player
            )
            .order_by(func.count(Draw.id).desc())
        )
        ranking = result.all()
        if ranking:
            rank_number, rank = next(
                ((i, rank) for i, rank in enumerate(ranking, 1) if rank.Player.telegram_id == user_id),
                (None, None)
            )
            if rank_number and rank:
                await message.reply_text(
                    PERSONAL_STATS_MESSAGE
                    .format(
                        username=username,
                        rank=rank_number,
                        draw_count=rank.draw_count
                    )
                )
 
        if not ranking or (not rank_number and not rank):
            await message.reply_text(PERSONAL_STATS_NO_PICKED_PLAYER_MESSAGE.format(username=username))
    return
 
def set_handlers(application: Application) -> None:
    handlers = [
        ChatMemberHandler(bot_chat_member_status_handler, ChatMemberHandler.MY_CHAT_MEMBER),
        MessageHandler(filters=filters.ChatType.GROUPS & filters.UpdateType.MESSAGE & filters.TEXT & ~filters.COMMAND & ~filters.VIA_BOT, callback=chat_member_handler),
        CallbackQueryHandler(approve_group, pattern=r"^(approve|reject):-?\d+$"),
        CommandHandler(UPDATE_PLAYER_WEIGHT_COMMAND, show_groups),
        CallbackQueryHandler(show_groups, pattern=r"^show_groups_page:-?\d+$"),
        CallbackQueryHandler(show_players_in_group, pattern=r"^show_players_in_group:-?\d+$"),
        CallbackQueryHandler(ask_player_weight, pattern=r"^select_player:-?\d+$"),
        CallbackQueryHandler(update_player_weight, pattern=r"^weight:-?\d+$"),
        CommandHandler(PICK_PLAYER_COMMAND, pick_player),
        CommandHandler(SHOW_LEADERBOARD_COMMAND, show_leaderboard),
        CommandHandler(SHOW_PERSONAL_STATS_COMMAND, show_personal_stats),
    ]
    for handler in handlers:
        application.add_handler(handler)
    return
 
async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(PICK_PLAYER_COMMAND, PICK_PLAYER_COMMAND_DESCRIPTION),
        BotCommand(SHOW_LEADERBOARD_COMMAND, SHOW_LEADERBOARD_COMMAND_DESCRIPTION),
        BotCommand(SHOW_PERSONAL_STATS_COMMAND, SHOW_PERSONAL_STATS_COMMAND_DESCRIPTION),
    ], scope=BotCommandScopeAllGroupChats())
    return
 
async def post_init(application: Application) -> None:
    bot = application.bot
    set_handlers(application)
    await set_admin_commands(bot, TG_BOT_ADMIN_RIGHTS_CHAT_MEMBER_USER_IDS)
    await set_commands(bot)
    return
 
def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).post_init(post_init).build()
    application.run_polling(allowed_updates=ALLOWED_UPDATES)
 
app = Flask(__name__)
 
if __name__ == "__main__":
    threading.Thread(target=main).start()
    app.run(host='0.0.0.0', port=3000)
