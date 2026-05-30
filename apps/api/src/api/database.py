from core_shared.database import Database

from api.settings import settings

db = Database(settings.get_database_url())
