from aiogram import Router

from book_bot.bot.handlers.add_appoinotment import router as add_appointment_router
from book_bot.bot.handlers.main import router as main_menu_router
from book_bot.bot.handlers.startup import router as startup_router

router = Router()
router.include_routers(startup_router, main_menu_router, add_appointment_router)
