from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keybord import again_keyboard, knop, knop_letter, knop_spin, knop_word
from servises import add_game, add_user, get_stats, get_words, show_top
import random


SECTORS = [100, 200, 300, 400, 500, 700, 1000, 'bankrot', 'prize']
MAX_MISTAKES = 5
HINT_PRICE = 300
ROUNDS = 5


class Game(StatesGroup):
	spin = State()
	letter = State()
	word = State()


router = Router()


def clean_text(text):
	return (text or '').strip().upper().replace('Ё', 'Е')


def mask_word(word, opened):
	return ' '.join(ch if ch in opened else '_' for ch in word)


def game_text(data):
	return (
		f'Раунд {data["round"] + 1} из {ROUNDS}\n\n'
		f'Вопрос: {data["question"]}\n\n'
		f'Слово: {mask_word(data["word"], data["opened"])}\n\n'
		f'Очки: {data["score"]}\n'
		f'Ошибки: {data["mistakes"]}/{MAX_MISTAKES}'
	)


def results_text(results):
	text = ''
	number = 1
	for result in results:
		if result['is_win']:
			text = text + f'{number} - разгадано (+{result["score"]} очков)\n'
		else:
			text = text + f'{number} - не разгадано\n'
		number += 1
	return text


async def start_game(message, state, user):
	await add_user(user.id, user.username)
	words = await get_words(ROUNDS)
	if words is None or len(words) < ROUNDS:
		await message.answer(
			f'Не удалось получить слова. Проверьте подключение к БД и что в базе есть хотя бы {ROUNDS} слов.',
			reply_markup=knop
		)
		return

	await state.clear()
	await state.update_data(
		words=[{'id': w['id'], 'word': w['word'], 'question': w['question']} for w in words],
		round=0,
		results=[]
	)
	await message.answer(f'Поле чудес! Вам нужно отгадать слов: {ROUNDS}. Начинаем игру.')
	await start_round(message, state)


async def start_round(message, state):
	data = await state.get_data()
	word = data['words'][data['round']]

	await state.set_state(Game.spin)
	await state.update_data(
		word_id=word['id'],
		word=word['word'],
		question=word['question'],
		opened=[],
		score=0,
		mistakes=0,
		sector=0
	)
	data = await state.get_data()
	await message.answer(game_text(data), reply_markup=knop_spin)


async def finish_round(message, state, user, is_win):
	data = await state.get_data()
	score = data['score'] if is_win else 0
	number = data['round'] + 1

	results = data['results']
	results.append({'word_id': data['word_id'], 'score': score, 'is_win': is_win})
	await state.update_data(results=results)

	if is_win:
		text = f'Раунд {number} пройден! Слово: {data["word"]}\nВы заработали: {score}'
	else:
		text = f'Раунд {number} не пройден. Слово было: {data["word"]}'

	if number >= ROUNDS:
		await finish_game(message, state, user, text)
		return

	await state.update_data(round=data['round'] + 1)
	await message.answer(text + '\n\nРезультаты:\n' + results_text(results))
	await start_round(message, state)


async def finish_game(message, state, user, text):
	data = await state.get_data()
	results = data['results']
	total = sum(result['score'] for result in results)
	solved = len([result for result in results if result['is_win']])

	saved = await add_game(user.id, user.username, results)
	await state.clear()

	text = (
		text + '\n\nИгра окончена!\n\n'
		+ results_text(results)
		+ f'\nРазгадано слов: {solved} из {ROUNDS}\n'
		+ f'Всего очков: {total}'
	)
	if not saved:
		text += '\nНе удалось сохранить результат. Проверьте подключение к БД.'

	await message.answer(text, reply_markup=knop)
	await message.answer('Сыграем ещё?', reply_markup=again_keyboard())


@router.message(Command('play'))
async def play_handler(message: types.Message, state: FSMContext):
	await start_game(message, state, message.from_user)


@router.message(Command('top'))
async def top_handler(message: types.Message):
	users = await show_top()
	if users is None:
		await message.answer('Не удалось получить топ. Проверьте подключение к БД.', reply_markup=knop)
		return
	if not users:
		await message.answer('Пока никто не играл. Напиши /play, чтобы стать первым.', reply_markup=knop)
		return

	text = 'Топ игроков:\n\n'
	number = 1
	for user in users:
		name = '@' + user['username'] if user['username'] else 'без имени'
		text = text + f'{number}. {name} - {user["score"]} очков (слов: {user["wins"]})\n'
		number += 1
	await message.answer(text, reply_markup=knop)


@router.message(Command('me'))
async def me_handler(message: types.Message):
	stats = await get_stats(message.from_user.id)
	if stats is None:
		await message.answer('Ты ещё не играл. Напиши /play, чтобы начать.', reply_markup=knop)
		return

	await message.answer(
		f'Всего очков: {stats["score"]}\n'
		f'Разгадано слов: {stats["wins"]}\n'
		f'Игр: {stats["games"]}',
		reply_markup=knop
	)


@router.message(Command('giveup'), StateFilter(Game.spin, Game.letter, Game.word))
async def giveup_handler(message: types.Message, state: FSMContext):
	await finish_round(message, state, message.from_user, False)


@router.message(Command('spin'), Game.spin)
async def spin_handler(message: types.Message, state: FSMContext):
	sector = random.choice(SECTORS)
	data = await state.get_data()

	if sector == 'bankrot':
		await state.update_data(score=0)
		data = await state.get_data()
		await message.answer(
			'Банкрот! Все очки раунда сгорели. Крутите барабан ещё раз.\n\n' + game_text(data),
			reply_markup=knop_spin
		)
	elif sector == 'prize':
		await state.update_data(score=data['score'] + 500)
		data = await state.get_data()
		await message.answer(
			'Приз! +500 очков. Крутите барабан ещё раз.\n\n' + game_text(data),
			reply_markup=knop_spin
		)
	else:
		await state.update_data(sector=sector)
		await state.set_state(Game.letter)
		await message.answer(f'Выпало: {sector}\nВведите букву:', reply_markup=knop_letter)


@router.message(Command('hint'), Game.spin)
async def hint_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	if data['score'] < HINT_PRICE:
		await message.answer(
			f'Не хватает очков. Подсказка стоит {HINT_PRICE} очков.\n\n' + game_text(data),
			reply_markup=knop_spin
		)
		return

	opened = data['opened']
	hidden = [ch for ch in set(data['word']) if ch not in opened]
	if len(hidden) <= 1:
		await message.answer(
			'Осталась одна буква, подсказка не нужна. Назовите слово: /word\n\n' + game_text(data),
			reply_markup=knop_spin
		)
		return

	letter = random.choice(hidden)
	opened.append(letter)
	await state.update_data(opened=opened, score=data['score'] - HINT_PRICE)
	data = await state.get_data()
	await message.answer(
		f'Подсказка: открыта буква «{letter}». -{HINT_PRICE} очков.\n\n' + game_text(data),
		reply_markup=knop_spin
	)


@router.message(Command('word'), StateFilter(Game.spin, Game.letter))
async def word_handler(message: types.Message, state: FSMContext):
	await state.set_state(Game.word)
	await message.answer('Введите слово целиком:', reply_markup=knop_word)


@router.message(Game.letter)
async def letter_handler(message: types.Message, state: FSMContext):
	letter = clean_text(message.text)
	if len(letter) != 1 or not letter.isalpha():
		await message.answer('Нужна одна буква. Введите букву:')
		return

	data = await state.get_data()
	opened = data['opened']
	if letter in opened:
		await message.answer('Эта буква уже была. Введите другую:')
		return

	opened.append(letter)
	count = data['word'].count(letter)

	if count:
		plus = data['sector'] * count
		await state.update_data(opened=opened, score=data['score'] + plus)
		data = await state.get_data()

		if all(ch in opened for ch in data['word']):
			await finish_round(message, state, message.from_user, True)
			return

		await state.set_state(Game.spin)
		await message.answer(
			f'Есть буква «{letter}»! Букв: {count}, +{plus} очков.\n\n' + game_text(data),
			reply_markup=knop_spin
		)
	else:
		mistakes = data['mistakes'] + 1
		await state.update_data(opened=opened, mistakes=mistakes)
		if mistakes >= MAX_MISTAKES:
			await finish_round(message, state, message.from_user, False)
			return

		data = await state.get_data()
		await state.set_state(Game.spin)
		await message.answer(
			f'Буквы «{letter}» нет.\n\n' + game_text(data),
			reply_markup=knop_spin
		)


@router.message(Game.word)
async def get_word_handler(message: types.Message, state: FSMContext):
	answer = clean_text(message.text)
	if not answer:
		await message.answer('Слово не должно быть пустым. Введите слово:')
		return

	data = await state.get_data()
	if answer == data['word']:
		await state.update_data(score=data['score'] + 1000)
		await finish_round(message, state, message.from_user, True)
	else:
		mistakes = data['mistakes'] + 1
		await state.update_data(mistakes=mistakes)
		if mistakes >= MAX_MISTAKES:
			await finish_round(message, state, message.from_user, False)
			return

		data = await state.get_data()
		await state.set_state(Game.spin)
		await message.answer(
			'Неверное слово.\n\n' + game_text(data),
			reply_markup=knop_spin
		)