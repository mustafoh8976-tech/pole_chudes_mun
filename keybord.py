from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup


knop = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='/play'), KeyboardButton(text='/top')],
		[KeyboardButton(text='/me'), KeyboardButton(text='/help')]
	],
	resize_keyboard=True
)

knop_spin = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='/spin'), KeyboardButton(text='/word')],
		[KeyboardButton(text='/hint'), KeyboardButton(text='/giveup')]
	],
	resize_keyboard=True
)

knop_letter = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='/word'), KeyboardButton(text='/giveup')]
	],
	resize_keyboard=True
)

knop_word = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='/giveup')]
	],
	resize_keyboard=True
)


def again_keyboard():
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(
					text='Сыграть ещё',
					callback_data='again'
				)
			]
		]
	)
	return keyboard