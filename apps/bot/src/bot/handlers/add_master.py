from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from core_shared import AsyncSession
from core_shared.services.master import create_master

from bot.core.database import db
from bot.core.exceptions import InternalError
from bot.keyboards.admin_panel import get_master_profile_keyboard
from bot.keyboards.general import confirm_keyboard
from bot.middlewares import IsAdminCheckMiddleware
from bot.states import AdminPanelStates, MasterCreationStates

router = Router()
router.message.middleware(IsAdminCheckMiddleware(db))


@router.callback_query(AdminPanelStates.main_menu, F.data == "add_master")
async def create_master_dialog(callback: types.CallbackQuery, state: FSMContext):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    await callback.answer()
    await callback.message.answer("Введите имя мастера:")
    await state.set_state(MasterCreationStates.get_name)


@router.message(MasterCreationStates.get_name)
async def get_master_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(MasterCreationStates.select_profile)
    keyboard = get_master_profile_keyboard()
    await message.answer("Выберите профиль мастера:", reply_markup=keyboard)


@router.message(MasterCreationStates.select_profile, F.user_shared)
async def link_user(message: types.Message, state: FSMContext):
    if not message.user_shared:
        raise InternalError
    contact = message.user_shared
    if not contact.user_id:
        raise InternalError

    await state.update_data(tg_id=contact.user_id)
    await state.set_state(MasterCreationStates.confirm)
    keyboard = confirm_keyboard()
    await message.answer("Вы подтерждаете создание мастера?", reply_markup=keyboard)


@router.message(MasterCreationStates.select_profile, ~F.user_shared)
async def cancel_link_user(message: types.Message, state: FSMContext):
    await state.update_data(tg_id=-1)
    await state.set_state(MasterCreationStates.confirm)
    keyboard = confirm_keyboard()
    await message.answer("Вы подтерждаете создание мастера?", reply_markup=keyboard)


@router.callback_query(MasterCreationStates.confirm, F.data == "confirm")
async def create_master_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    data = await state.get_data()
    tg_id = data["tg_id"]
    if tg_id == -1:
        tg_id = None
    full_name = data["full_name"]
    master = await create_master(full_name=full_name, tg_id=tg_id, session=session)
    if not master:
        await callback.message.edit_text("Серверная ошибка")
        return
    await callback.message.edit_text(f"Профиль создан: #{master.id}")
    await callback.answer()


@router.callback_query(MasterCreationStates.confirm, F.data == "cancel")
async def cancel_master_creation(callback: types.CallbackQuery, state: FSMContext):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    await state.clear()
    await state.set_state(AdminPanelStates.main_menu)
    await callback.message.edit_text("Вы отменили операцию")
    await callback.answer()
