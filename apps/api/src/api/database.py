from core_shared.database import Database

from api.settings import settings

db = Database(settings.POSTGRES_URL)
