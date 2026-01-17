import logging
from logging.handlers import RotatingFileHandler
from typing import Generator
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_log_level
from .crud import create_user, list_users
from .db import SessionLocal, init_db
from .schemas import LoginRequest, UserCreate, UserOut

logging.basicConfig(level=getattr(logging, get_log_level().upper(), logging.INFO))
logger = logging.getLogger("app")


# Отдельный логгер для авторизации (пишем в файл auth.log)
def _setup_auth_logger() -> logging.Logger:
    level = getattr(logging, get_log_level().upper(), logging.INFO)

    auth_logger = logging.getLogger("auth")
    auth_logger.setLevel(level)

    # Чтобы при автоперезапуске (uvicorn --reload) не навешивались дублирующие хэндлеры
    if not any(isinstance(h, RotatingFileHandler) for h in auth_logger.handlers):
        handler = RotatingFileHandler(
            "auth.log",
            maxBytes=1_000_000,  # 1 MB
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        auth_logger.addHandler(handler)

    # Не дублируем записи в основном logger'е (stdout)
    auth_logger.propagate = False
    return auth_logger


auth_logger = _setup_auth_logger()

app = FastAPI(title="Lab 9 — FastAPI + PostgreSQL")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
templates = Jinja2Templates(directory="app/templates")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("DB initialized")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/users", response_model=list[UserOut])
def api_list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    return list_users(db)


@app.post("/api/users", response_model=UserOut)
def api_create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    try:
        return create_user(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")


@app.post("/api/auth/login")
def login(payload: LoginRequest, request: Request) -> dict:
    client_ip = request.client.host if request.client else "unknown"

    # Пишем авторизационные события в auth.log
    auth_logger.info("LOGIN ATTEMPT | username=%s | ip=%s", payload.username, client_ip)

    # Демо-проверка (в реальном проекте тут была бы проверка пароля)
    if payload.password != "secret":
        auth_logger.warning("LOGIN FAIL | username=%s | ip=%s", payload.username, client_ip)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    auth_logger.info("LOGIN OK | username=%s | ip=%s", payload.username, client_ip)
    return {"status": "ok", "username": payload.username}
