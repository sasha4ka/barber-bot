from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards.startup import get_ask_phone_keyboard
from book_bot.bot.states import RegistrationStates
from book_bot.services.user import get_user


class UserProfileCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, types.Message):
            return await handler(event, data)

        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state == RegistrationStates.waiting_for_phone:
                return await handler(event, data)

        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        user = await get_user(tg_id=event.from_user.id)
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
