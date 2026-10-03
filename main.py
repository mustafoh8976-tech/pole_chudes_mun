from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from callbeck import router as callback_router
from connection_db import create_table
from dotenv import load_dotenv
from keybord import knop
from servises import add_user
from states import router as state_router
import asyncio
import os


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
dp = Dispatcher()


@dp.message(Command('start'))
async def starts(message: types.Message, state: FSMContext):
	await state.clear()
	await add_user(message.from_user.id, message.from_user.username)
	await message.answer(
		'Привет, я бот Поле чудес.\n'
		'Нажми /help, чтобы посмотреть команды.',
		reply_markup=knop
	)


@dp.message(Command('help'))
async def helps(message: types.Message):
	await message.answer('''Вот что я умею:
/start - начать работу со мной
/help - помощь по командам
/play - начать новую игру
/top - посмотреть топ игроков
/me - посмотреть свой счёт
Как играть:
1. Напиши /play, начнётся игра из 5 раундов, в каждом своё слово и вопрос
2. Нажми /spin и крути барабан
3. Если выпало число, введи букву. За каждую найденную букву получишь очки: число на барабане умножить на количество букв
4. Банкрот обнуляет очки раунда, приз даёт +500
5. Слово целиком можно назвать командой /word, за него +1000 очков
6. Команда /hint за 300 очков открывает одну случайную букву
7. После 5 ошибок раунд проигран, а /giveup пропускает слово
8. В конце игры бот покажет, какие слова ты разгадал и сколько очков набрал
Очки сохраняются только за разгаданные слова.
''', reply_markup=knop)


async def main():
	if not BOT_TOKEN:
		print('у вас не указан BOT_TOKEN в файле .env')
		return

	await create_table()
	bot = Bot(token=BOT_TOKEN)
	dp.include_router(state_router)
	dp.include_router(callback_router)
	print('Start bot')
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())