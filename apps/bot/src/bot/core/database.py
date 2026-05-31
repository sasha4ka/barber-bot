from bot.core.settings import settings
from core_shared.database import Database

db = Database(settings.POSTGRES_URL)
