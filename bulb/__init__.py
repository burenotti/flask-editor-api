from .api import router
from .app import app

app.include_router(router)
