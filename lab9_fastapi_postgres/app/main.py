import logging
from typing import Generator

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

app = FastAPI(title="Lab 9 — FastAPI + PostgreSQL")
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
    # Демонстрация логирования для лабораторной (можно доработать в отдельной ветке)
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Login attempt: username=%s ip=%s", payload.username, client_ip)

    # Демо-проверка (в реальном проекте тут была бы проверка пароля)
    if payload.password != "secret":
        logger.warning("Login failed: username=%s ip=%s", payload.username, client_ip)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Login success: username=%s ip=%s", payload.username, client_ip)
    return {"status": "ok", "username": payload.username}
