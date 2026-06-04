from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from bot.core.database import db
from bot.core.exceptions import InternalError
from bot.keyboards.admin_panel import (
    admin_panel_keyboard,
    cancel_master_name_entering_keyboard,
    get_master_profile_keyboard,
)
from bot.keyboards.general import cancel_keyboard, confirm_keyboard
from bot.middlewares import IsAdminCheckMiddleware
from bot.states import AdminPanelStates, MasterCreationStates
from core_shared import AsyncSession
from core_shared.services.master import create_master

router = Router()
router.message.middleware(IsAdminCheckMiddleware(db))


@router.callback_query(AdminPanelStates.main_menu, F.data == "add_master")
async def create_master_dialog(callback: types.CallbackQuery, state: FSMContext):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    await callback.answer()
    await callback.message.answer(
        "Введите имя мастера:", reply_markup=cancel_master_name_entering_keyboard()
    )
    await state.set_state(MasterCreationStates.get_name)


@router.message(MasterCreationStates.get_name, F.text != "Отменить")
async def get_master_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(MasterCreationStates.select_profile)
    keyboard = get_master_profile_keyboard()
    await message.reply("Выберите профиль мастера:", reply_markup=keyboard)


@router.message(MasterCreationStates.select_profile, F.user_shared)
async def link_user(message: types.Message, state: FSMContext):
    if not message.user_shared:
        raise InternalError
    contact = message.user_shared
    if not contact.user_id:
        raise InternalError

    await state.set_state(MasterCreationStates.waiting_for_password)
    message = await message.reply(
        "Введите пароль для мастера:", reply_markup=cancel_keyboard()
    )
    await state.update_data(tg_id=contact.user_id, to_remove=message.message_id)


@router.message(MasterCreationStates.waiting_for_password, F.text != "Отменить")
async def get_password(message: types.Message, state: FSMContext):
    password = message.text
    await message.delete()
    to_remove = await state.get_value("to_remove", -1)
    await message.chat.delete_message(to_remove)
    await state.update_data(password=password)
    keyboard = confirm_keyboard()
    await state.set_state(MasterCreationStates.confirm)
    await message.answer("Вы подтерждаете создание мастера?", reply_markup=keyboard)


@router.callback_query(MasterCreationStates.confirm, F.data == "confirm")
async def create_master_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    data = await state.get_data()
    tg_id = data["tg_id"]
    full_name = data["full_name"]
    password = data["password"]
    master = await create_master(
        full_name=full_name,
        tg_id=tg_id,
        session=session,
        username=full_name,
        password=password,
    )
    if not master:
        raise InternalError

    await state.clear()
    await state.set_state(AdminPanelStates.main_menu)
    await callback.message.delete()
    await callback.message.answer(
        f"Профиль создан: #{master.id}", reply_markup=admin_panel_keyboard()
    )
    await callback.answer()


async def cancel_master_creation_by_callback(
    callback: types.CallbackQuery, state: FSMContext
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    await state.clear()
    await state.set_state(AdminPanelStates.main_menu)
    await callback.message.edit_text("Вы отменили операцию")
    await callback.answer()


router.callback_query.register(
    cancel_master_creation_by_callback, MasterCreationStates.confirm, F.data == "cancel"
)


async def cancel_master_creation_by_message(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(AdminPanelStates.main_menu)
    await message.reply("Вы отменили операцию", reply_markup=admin_panel_keyboard())


router.message.register(
    cancel_master_creation_by_message,
    MasterCreationStates.get_name,
    F.text == "Отменить",
)
router.message.register(
    cancel_master_creation_by_message,
    MasterCreationStates.select_profile,
    F.text == "Отменить",
)
router.message.register(
    cancel_master_creation_by_message,
    MasterCreationStates.waiting_for_password,
    F.text == "Отменить",
)
