from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from src.bot.common.texts import WELCOME_MESSAGE, HELP_MESSAGE
from src.settings import settings


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    formatted_message = settings.JINGA2_ENV.from_string(WELCOME_MESSAGE).render(
        {"user_id": message.from_user.id} # type: ignore
    )
    await message.answer(formatted_message)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_MESSAGE)

@router.message()
async def echo(message: Message):
    await message.answer("😊 Не знаю такой команды, попробуйте /help") 
