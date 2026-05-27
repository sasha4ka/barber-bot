import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards.admin_panel import (
    AdminPanelButtons,
    admin_panel_keyboard,
    ask_contact_keyboard,
    create_master_keyboard,
)
from book_bot.bot.keyboards.main_menu import main_menu_keyboard
from book_bot.bot.middlewares import IsAdminCheckMiddleware
from book_bot.bot.states import AdminPanelStates
from book_bot.core.exceptions import InternalError
from book_bot.models.models import User
from book_bot.services.master import get_masters
from book_bot.services.slot import generate_slots_for_date
from book_bot.services.user import get_user, get_user_count

router = Router()
router.message.middleware(IsAdminCheckMiddleware())


@router.message(F.text == "⚙️Админ-панель")
async def admin_panel_handler(message: types.Message, user: User, state: FSMContext):
    await state.set_state(AdminPanelStates.main_menu)
    user_count = await get_user_count()
    await message.answer(
        (
            f"<b>Админ-панель</b>\n👤 Пользователей: {user_count}\n(Вы можете отправить контакт для просмотра профиля пользователя)"
        ),
        reply_markup=admin_panel_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminPanelStates.main_menu, F.text == AdminPanelButtons.back.value)
async def back_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=main_menu_keyboard(is_admin=True)
    )


@router.message(
    AdminPanelStates.main_menu, F.text == AdminPanelButtons.generate_slots.value
)
async def generate_slots_handler(message: types.Message, state: FSMContext):
    target_date = datetime.datetime.now().date()
    work_start = datetime.time(10)
    work_end = datetime.time(18)

    await generate_slots_for_date(
        target_date=target_date, work_start=work_start, work_end=work_end
    )
    await message.reply("Слоты созданы успешно")


@router.message(AdminPanelStates.main_menu, F.user_shared)
async def show_profile_handler(message: types.Message, state: FSMContext):
    contact = message.user_shared
    if not contact:
        raise InternalError

    user = await get_user(tg_id=contact.user_id)
    if not user:
        await message.answer("Пользователь не является клиентом салона!")
        return

    text = (
        f"<b>Профиль пользователя {user.full_name}:</b>\n"
        f"📞 Телефон: {user.phone}\n"
        f"🆔 Telegram ID: {user.tg_id}\n"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(AdminPanelStates.main_menu, F.text == AdminPanelButtons.users.value)
async def users_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, поделитесь контактом пользователя.",
        reply_markup=ask_contact_keyboard(),
    )


@router.message(AdminPanelStates.main_menu, F.text == AdminPanelButtons.masters)
async def print_masters(message: types.Message, state: FSMContext):
    masters = await get_masters()
    text = "<b>Список мастеров:</b>\n" + "\n".join(
        [master.full_name for master in masters]
    )
    await message.answer(
        text, reply_markup=create_master_keyboard(), parse_mode=ParseMode.HTML
    )
