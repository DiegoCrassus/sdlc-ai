from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers.agent import router as agent_router
from app.routers.characters import router as characters_router
from app.routers.sheets import router as sheets_router
from app.routers.template import router as template_router
from app.routers.workspaces import router as workspaces_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="RPG-OP API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspaces_router, prefix=settings.api_prefix)
app.include_router(characters_router, prefix=settings.api_prefix)
app.include_router(sheets_router, prefix=settings.api_prefix)
app.include_router(template_router, prefix=settings.api_prefix)
app.include_router(agent_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
