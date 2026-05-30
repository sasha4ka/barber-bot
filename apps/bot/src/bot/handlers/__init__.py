from aiogram import Router, types

from bot.core.database import db
from bot.core.exceptions import InternalError
from bot.handlers.add_appointment import router as add_appointment_router
from bot.handlers.add_master import router as add_master_router
from bot.handlers.admin_panel import router as admin_panel_router
from bot.handlers.main_menu import router as main_menu_router
from bot.handlers.register_user import router as register_user_router
from bot.middlewares import CatchInternalErrorMiddleware, DatabaseMiddleware

router = Router()

router.message.middleware(CatchInternalErrorMiddleware())
router.callback_query.middleware(CatchInternalErrorMiddleware())
router.message.middleware(DatabaseMiddleware(db))
router.callback_query.middleware(DatabaseMiddleware(db))

router.include_routers(
    register_user_router,
    main_menu_router,
    add_appointment_router,
    admin_panel_router,
    add_master_router,
)


fallback_router = Router()


@fallback_router.callback_query()
async def unknown_callback_handler(callback: types.CallbackQuery):
    raise InternalError


router.include_router(fallback_router)
