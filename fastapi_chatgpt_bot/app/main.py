import logging
import asyncio
import uuid

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import BotCommand

from config import TELEGRAM_MAIN_BOT_TOKEN, TELEGRAM_ADMIN_BOT_TOKEN, OPENAI_API_KEY, TELEGRAM_ADMIN_USER_ID
from crud import add_message, check_user_password, create_user, get_user_by_telegram_id
from openai_agent import OpenAIAgent
from audio_to_text import audio_to_text
from database import session_scope, engine
from models import Base

logging.basicConfig(level=logging.INFO)

# main bot
bot = Bot(token=TELEGRAM_MAIN_BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# admin bot
admin_bot = Bot(token=TELEGRAM_ADMIN_BOT_TOKEN)
admin_dp = Dispatcher(admin_bot)
admin_dp.middleware.setup(LoggingMiddleware())

# create OpenAI agent
openai_agent = OpenAIAgent(api_key=OPENAI_API_KEY)
# create db tables
Base.metadata.create_all(bind=engine)

# add available bot commands
commands = [
    BotCommand(command="/start", description="Start the bot"),
    BotCommand(command="/help", description="Show the bot's help message"),
]

# ===========================================
# ========== Handlers for Main Bot ==========
# ===========================================


@dp.message_handler(commands=["start", "help"])
async def handle_start_help(message: types.Message):
    # set commands
    await bot.set_my_commands(commands)
    # send welcome message
    await bot.send_message(
        message.chat.id,
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/password <password> - Check if the user has access to the bot\n"
        "/reset_context - Reset the conversation context with the ChatGPT",
    )


@dp.message_handler(lambda message: message.text.startswith("/password"))
async def check_password(message: types.Message):

    message_list = message.text.split(" ")
    if len(message_list) == 1:
        await message.reply("Not found password.")
        return False

    password = message_list[1].strip()
    with session_scope() as db_session:
        user = get_user_by_telegram_id(db_session, str(message.from_user.id))
        if not user:
            await message.reply(
                "You don't have access. Check the instructions on how to activate the bot with the /help command.",
            )
            return False

        # check user password
        if check_user_password(user, password):
            await message.reply("Correct password entered, now you can communicate with the bot!")
        else:
            await message.reply("Wrong password entered, please try again.")


# reset context
@dp.message_handler(lambda message: message.text == "/reset_context")
async def reset_context(message: types.Message):
    with session_scope() as db_session:
        user = get_user_by_telegram_id(db_session, str(message.from_user.id))

        if not user or not user.active:
            await message.reply(
                "You don't have access. Check the instructions on how to activate the bot with the /help command.",
            )
            return False

        openai_agent.reset_context(user.telegram_id)
        await message.reply("The context has been successfully reset. You can start a new dialog with the bot.")


# handler for text messages
@dp.message_handler(lambda message: not message.text.startswith("/"))
async def handle_text_message(message: types.Message):
    text = message.text
    with session_scope() as db_session:
        user = get_user_by_telegram_id(db_session, str(message.from_user.id))

        if not user or not user.active:
            await message.reply(
                "You don't have access. Check the instructions on how to activate the bot with the /help command.",
            )
            return False

        user_id = user.id
        # save user message to database
        add_message(db_session, user_id=user_id, text=text, is_bot=False)

    # bot typing
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    # send message to ChatGPT
    chatgpt_response = openai_agent.process_message(user_id, message.text)

    # save bot message to database
    with session_scope() as db_session:
        add_message(db_session, user_id=user_id, text=chatgpt_response, is_bot=True)

    # send response to user
    await message.reply(chatgpt_response)


# handler for audio messages
@dp.message_handler(content_types=["voice"])
async def handle_voice_message(message: types.Message):
    with session_scope() as db_session:
        user = get_user_by_telegram_id(db_session, str(message.from_user.id))

        if not user or not user.active:
            await message.reply(
                "You don't have access. Check the instructions on how to activate the bot with the /help command.",
            )
            return False

        add_message(db_session, user_id=user.id, text="[Audio message]", is_bot=False)

        # get file id
        file_id = message.voice.file_id
        # get bytes of audio message
        voice_bytes = await bot.get_file(file_id)
        # convert audio message to text
        text = await audio_to_text(voice_bytes)

        # save bot message to database
        add_message(db_session, user_id=user.id, text=text, is_bot=True)

    # return the decoded message
    await message.reply(text)

# ============================================
# ========== Handlers for Admin Bot ==========
# ============================================


@admin_dp.message_handler(commands=["create_user"])
async def handle_create_user(message: types.Message):
    if str(message.from_user.id) != TELEGRAM_ADMIN_USER_ID:
        await message.reply("No access to register new user.")
        return False

    message_list = message.text.split(" ")
    if len(message_list) == 1:
        await message.reply("Not found telegram user ID to register new user.")
        return False

    telegram_id = message_list[1].strip()

    with session_scope() as db_session:
        user = get_user_by_telegram_id(db_session, telegram_id)
    if user:
        await message.reply("The user is already registered.")
        return False

    password = str(uuid.uuid4())
    with session_scope() as db_session:
        user = create_user(db_session, telegram_id, password)

    if user:
        await message.reply(f"The user was successfully created: Telegram ID {telegram_id}, Password {password}.")
    else:
        await message.reply("User creation error.")


@admin_dp.message_handler(lambda message: message.text.startswith("/"))
async def handle_unknown_command(message: types.Message):
    await message.reply("Unknown command.")


# ==========================
# ========== Main ==========
# ==========================

# TODO
# async def on_startup(dp):
#     import wdb
#     wdb.set_trace()
#     await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="The bot is running")
#
#
# async def on_shutdown(dp):
#     await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="The bot is stopped")

# TODO: lang (use english also)

async def start_bot():
    try:
        await dp.start_polling()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()


async def start_admin_bot():
    try:
        await admin_dp.start_polling()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await admin_dp.storage.close()
        await admin_dp.storage.wait_closed()


async def main():
    await asyncio.gather(start_bot(), start_admin_bot())


if __name__ == "__main__":
    asyncio.run(main())
