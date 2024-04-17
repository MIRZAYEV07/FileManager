from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from logging.config import fileConfig
import logging
from auth import authentication
from database.database import get_db, init_db
from database.minio_client import get_minio_client
from routers import user, file_manger

from fastapi import FastAPI
from loguru import logger
from fastapi_pagination import add_pagination
from database.database_populate import create_users
import sentry_sdk
import os
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException, status, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import httpx


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()


OPENAPI_DASHBOARD_LOGIN = os.getenv('USERNAME', 'admin')
OPENAPI_DASHBOARD_PASSWORD = os.getenv('PASSWORD', 'ping1234')

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis')
security = HTTPBasic()

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.5,
    profiles_sample_rate=1.0,
)

# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Filemanager service ",
    description="This is a Filemanager service ",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)
app.mount("/static", StaticFiles(directory="static"), name="static")

logger.info("Starting application...")

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, OPENAPI_DASHBOARD_LOGIN)
    correct_password = secrets.compare_digest(credentials.password, OPENAPI_DASHBOARD_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs")
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs", oauth2_redirect_url="/docs/oauth2-redirect",
                               swagger_js_url="/static/swagger-ui-bundle.js", swagger_css_url="/static/swagger-ui.css")


@app.get("/openapi.json")
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)


app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(file_manger.router)


app_infrastucture = FastAPI(
    title="Filemanager Vision Infrastructure",
    description="This documentation provides information about integration with Filemanager Infrastructure")

app_infrastucture.include_router(authentication.router)
app.mount("/infrastructure", app_infrastucture)


add_pagination(app)
add_pagination(app_infrastucture)


@app.on_event("startup")
async def startup():
    logger.info("Startup event")
    db = next(get_db())
    try:
        await init_db()
    except Exception as e:
        print(e)

    try:
        create_users(db)

    except Exception as e:
        print(e)
        pass


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

