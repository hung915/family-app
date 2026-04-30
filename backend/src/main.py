from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.config import settings
from src.members.router import router as members_router

_show_docs = settings.ENV in ('local', 'staging')

app = FastAPI(
    title='Family App API',
    version='0.1.0',
    docs_url='/docs' if _show_docs else None,
    redoc_url='/redoc' if _show_docs else None,
    openapi_url='/openapi.json' if _show_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(auth_router)
app.include_router(members_router)


@app.get('/health', tags=['system'], summary='Health check', status_code=200)
async def health() -> dict[str, str]:
    return {'status': 'ok'}
