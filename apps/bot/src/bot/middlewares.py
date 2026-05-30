from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from core_shared.database import Database
from core_shared.services.user import get_user

from bot.core.exceptions import InternalError
from bot.keyboards.register_user import get_ask_phone_keyboard
from bot.states import RegistrationStates


class UserProfileCheckMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, types.Message):
            return await handler(event, data)

        state: FSMContext = data.get("state")  # type: ignore
        if state:
            current_state = await state.get_state()
            if current_state == RegistrationStates.waiting_for_phone:
                return await handler(event, data)

        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        async with self.db.session_scope() as session:
            user = await get_user(tg_id=event.from_user.id, session=session)

            if not user:
                await state.set_state(RegistrationStates.waiting_for_phone)
                await event.answer(
                    "⛔ Доступ ограничен. \n"
                    "Необходимо завершить регистрацию профиля. \n"
                    "Пожалуйста, поделитесь своим контактом",
                    reply_markup=get_ask_phone_keyboard(),
                )
                return

        data["user"] = user
        return await handler(event, data)


class IsAdminCheckMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, (types.Message, types.CallbackQuery)):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        async with self.db.session_scope() as session:
            user = await get_user(tg_id=event.from_user.id, session=session)

        if not user:
            return
        if not user.is_admin:
            return

        data["user"] = user
        return await handler(event, data)


class CatchInternalErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, types.Message):
            try:
                return await handler(event, data)
            except InternalError:
                await event.answer("Произошла внутренняя ошибка. Попробуйте позже!")
                return
        if isinstance(event, types.CallbackQuery):
            try:
                return await handler(event, data)
            except InternalError:
                await event.answer("Серверная ошибка... Попробуйте позже!")


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.db.session_scope() as session:
            data["session"] = session
            return await handler(event, data)
