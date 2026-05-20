from aiogram import Router, types

from book_bot.bot.general import server_error
from book_bot.bot.handlers.add_appoinotment import router as add_appointment_router
from book_bot.bot.handlers.main import router as main_menu_router
from book_bot.bot.handlers.startup import router as startup_router

router = Router()
router.include_routers(startup_router, main_menu_router, add_appointment_router)


fallback_router = Router()


@fallback_router.callback_query()
async def unknown_callback_handler(callback: types.CallbackQuery):
    await server_error(callback)


router.include_router(fallback_router)
