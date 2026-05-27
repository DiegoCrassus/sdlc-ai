"""Simulated portfolio routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.database import get_db
from app.backend.errors import AppError
from app.backend.schemas import (
    PaginatedHoldings,
    PaginatedTransactions,
    Portfolio,
    TransactionCreate,
    TransactionResponse,
    TransactionType,
)
from app.backend.services import portfolio as portfolio_service
from app.backend.utils.asset_id import format_asset_id, parse_asset_id

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def _normalize_asset_id(asset_id: str) -> str:
    try:
        asset_class, symbol = parse_asset_id(asset_id)
    except Exception as exc:
        raise AppError("VALIDATION_ERROR", str(exc)) from exc
    return format_asset_id(asset_class, symbol)


@router.get("", response_model=Portfolio)
async def get_portfolio(session: AsyncSession = Depends(get_db)) -> Portfolio:
    return await portfolio_service.get_or_create_portfolio(session)


@router.get("/holdings", response_model=PaginatedHoldings)
async def list_holdings(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> PaginatedHoldings:
    return await portfolio_service.list_holdings(session, limit=limit, offset=offset)


@router.get("/transactions", response_model=PaginatedTransactions)
async def list_transactions(
    asset_id: str | None = Query(None),
    type: TransactionType | None = Query(None, alias="type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> PaginatedTransactions:
    normalized = _normalize_asset_id(asset_id) if asset_id else None
    return await portfolio_service.list_transactions(
        session,
        asset_id=normalized,
        tx_type=type,
        limit=limit,
        offset=offset,
    )


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    body: TransactionCreate,
    session: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    normalized = _normalize_asset_id(body.asset_id)
    payload = body.model_copy(update={"asset_id": normalized})
    return await portfolio_service.execute_transaction(session, payload)
