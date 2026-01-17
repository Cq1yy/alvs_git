# ЛР №9 Git, CI/CD — FastAPI + PostgreSQL

Минимальный учебный проект для лабораторной работы:
- Web интерфейс (HTML главная страница)
- PostgreSQL (таблица users, добавление/просмотр)
- Тесты (pytest)
- CI/CD (GitHub Actions: ruff + pytest)

## Быстрый старт (Docker)+
```bash
docker compose up --build
```

Открыть:
- http://localhost:8000/ — web страница
- http://localhost:8000/docs — Swagger

## Локальный запуск без Docker
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5432/app'
uvicorn app.main:app --reload
```

## Тесты
```bash
pytest -q
```
