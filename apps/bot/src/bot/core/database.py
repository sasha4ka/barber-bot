from core_shared.database import Database

from bot.core.settings import settings

db = Database(settings.POSTGRES_URL)
