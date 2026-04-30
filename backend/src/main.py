from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.config import settings
from src.exceptions import AppError
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


# ── Exception handlers ────────────────────────────────────────────────────────


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={'code': exc.CODE, 'detail': exc.MESSAGE},
        headers=getattr(exc, 'headers', None),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {
            'field': '.'.join(str(part) for part in e['loc'][1:]),
            'message': e['msg'],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            'code': 'VALIDATION_ERROR',
            'detail': 'Invalid request data',
            'errors': errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    detail = str(exc) if settings.ENV in ('local', 'staging') else 'An unexpected error occurred'
    return JSONResponse(
        status_code=500,
        content={'code': 'INTERNAL_ERROR', 'detail': detail},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(members_router)


@app.get('/health', tags=['system'], summary='Health check', status_code=200)
async def health() -> dict[str, str]:
    return {'status': 'ok'}
