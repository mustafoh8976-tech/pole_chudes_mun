from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from states import start_game


router = Router()


@router.callback_query(F.data == 'again')
async def again_handler(callback: types.CallbackQuery, state: FSMContext):
	await callback.message.edit_reply_markup(reply_markup=None)
	await callback.answer()
	await start_game(callback.message, state, callback.from_user)