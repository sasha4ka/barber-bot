from api.settings import settings
from core_shared.database import Database

db = Database(settings.POSTGRES_URL)
