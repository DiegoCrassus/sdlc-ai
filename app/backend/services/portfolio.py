"""Simulated portfolio persistence and transactions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.errors import AppError
from app.backend.models import (
    DEFAULT_PORTFOLIO_CASH,
    DEFAULT_PORTFOLIO_CURRENCY,
    DEFAULT_PORTFOLIO_NAME,
    HoldingRow,
    PortfolioRow,
    TransactionRow,
)
from app.backend.schemas import (
    Holding,
    PaginatedHoldings,
    PaginatedTransactions,
    Portfolio,
    Transaction,
    TransactionCreate,
    TransactionResponse,
    TransactionType,
)
from app.backend.services import market_data


def _holding_from_row(
    row: HoldingRow,
    *,
    market_price: float,
    source: str,
    asset=None,
) -> Holding:
    market_value = row.quantity * market_price
    cost_basis = row.quantity * row.avg_cost
    return Holding(
        asset_id=row.asset_id,
        asset=asset,
        quantity=row.quantity,
        avg_cost=row.avg_cost,
        market_price=market_price,
        market_value=market_value,
        cost_basis=cost_basis,
        unrealized_pnl=market_value - cost_basis,
        source=source,  # type: ignore[arg-type]
    )


async def _portfolio_totals(session: AsyncSession, portfolio_id: str) -> tuple[float, float]:
    """Return (total_cost_basis, holdings_market_value) for open positions."""
    result = await session.execute(
        select(HoldingRow).where(HoldingRow.portfolio_id == portfolio_id)
    )
    rows = result.scalars().all()
    total_cost_basis = 0.0
    holdings_market_value = 0.0
    for row in rows:
        quote = await market_data.get_quote(row.asset_id)
        market_value = row.quantity * quote.price
        total_cost_basis += row.quantity * row.avg_cost
        holdings_market_value += market_value
    return total_cost_basis, holdings_market_value


async def _row_to_portfolio(session: AsyncSession, row: PortfolioRow) -> Portfolio:
    total_cost_basis, holdings_market_value = await _portfolio_totals(session, row.id)
    total_value = row.cash_balance + holdings_market_value
    return Portfolio(
        id=row.id,
        name=row.name,
        base_currency=row.base_currency,
        cash_balance=row.cash_balance,
        total_value=total_value,
        total_cost_basis=total_cost_basis,
        unrealized_pnl=holdings_market_value - total_cost_basis,
        updated_at=row.updated_at,
    )


async def _transaction_from_row(row: TransactionRow) -> Transaction:
    return Transaction(
        id=row.id,
        type=row.type,  # type: ignore[arg-type]
        asset_id=row.asset_id,
        quantity=row.quantity,
        price=row.price,
        total=row.total,
        source=row.source,  # type: ignore[arg-type]
        executed_at=row.executed_at,
        note=row.note,
    )


async def get_or_create_portfolio(session: AsyncSession) -> Portfolio:
    result = await session.execute(select(PortfolioRow).limit(1))
    row = result.scalar_one_or_none()
    if row is None:
        now = datetime.now(UTC)
        row = PortfolioRow(
            id=str(uuid.uuid4()),
            name=DEFAULT_PORTFOLIO_NAME,
            base_currency=DEFAULT_PORTFOLIO_CURRENCY,
            cash_balance=DEFAULT_PORTFOLIO_CASH,
            updated_at=now,
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return await _row_to_portfolio(session, row)


async def _get_portfolio_row(session: AsyncSession) -> PortfolioRow:
    result = await session.execute(select(PortfolioRow).limit(1))
    row = result.scalar_one_or_none()
    if row is None:
        await get_or_create_portfolio(session)
        result = await session.execute(select(PortfolioRow).limit(1))
        row = result.scalar_one()
    return row


async def list_holdings(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedHoldings:
    portfolio = await _get_portfolio_row(session)
    total_result = await session.execute(
        select(func.count())
        .select_from(HoldingRow)
        .where(HoldingRow.portfolio_id == portfolio.id)
    )
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(HoldingRow)
        .where(HoldingRow.portfolio_id == portfolio.id)
        .order_by(HoldingRow.asset_id)
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()

    items: list[Holding] = []
    for row in rows:
        quote = await market_data.get_quote(row.asset_id)
        asset = await market_data.get_asset(row.asset_id)
        items.append(
            _holding_from_row(
                row,
                market_price=quote.price,
                source=quote.source,
                asset=asset,
            )
        )

    return PaginatedHoldings(items=items, total=total, limit=limit, offset=offset)


async def list_transactions(
    session: AsyncSession,
    *,
    asset_id: str | None = None,
    tx_type: TransactionType | None = None,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedTransactions:
    portfolio = await _get_portfolio_row(session)
    filters = [TransactionRow.portfolio_id == portfolio.id]
    if asset_id:
        filters.append(TransactionRow.asset_id == asset_id)
    if tx_type:
        filters.append(TransactionRow.type == tx_type)

    total_result = await session.execute(
        select(func.count()).select_from(TransactionRow).where(*filters)
    )
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(TransactionRow)
        .where(*filters)
        .order_by(TransactionRow.executed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()
    items = [await _transaction_from_row(r) for r in rows]
    return PaginatedTransactions(items=items, total=total, limit=limit, offset=offset)


async def execute_transaction(
    session: AsyncSession,
    body: TransactionCreate,
) -> TransactionResponse:
    portfolio_row = await _get_portfolio_row(session)

    try:
        await market_data.get_asset(body.asset_id)
    except AppError as exc:
        if exc.code == "NOT_FOUND":
            raise
        raise

    quote = await market_data.get_quote(body.asset_id)
    price = quote.price
    total = body.quantity * price
    now = datetime.now(UTC)

    if body.type == "buy":
        if total > portfolio_row.cash_balance:
            raise AppError(
                "UNPROCESSABLE",
                "Insufficient cash for purchase",
                status_code=422,
                details={
                    "cash_balance": portfolio_row.cash_balance,
                    "required": total,
                },
            )
        holding_result = await session.execute(
            select(HoldingRow).where(
                HoldingRow.portfolio_id == portfolio_row.id,
                HoldingRow.asset_id == body.asset_id,
            )
        )
        holding_row = holding_result.scalar_one_or_none()
        if holding_row:
            new_qty = holding_row.quantity + body.quantity
            holding_row.avg_cost = (
                holding_row.quantity * holding_row.avg_cost + total
            ) / new_qty
            holding_row.quantity = new_qty
        else:
            holding_row = HoldingRow(
                portfolio_id=portfolio_row.id,
                asset_id=body.asset_id,
                quantity=body.quantity,
                avg_cost=price,
            )
            session.add(holding_row)
        portfolio_row.cash_balance -= total

    else:  # sell
        holding_result = await session.execute(
            select(HoldingRow).where(
                HoldingRow.portfolio_id == portfolio_row.id,
                HoldingRow.asset_id == body.asset_id,
            )
        )
        holding_row = holding_result.scalar_one_or_none()
        if not holding_row or holding_row.quantity < body.quantity:
            held = holding_row.quantity if holding_row else 0.0
            raise AppError(
                "UNPROCESSABLE",
                "Insufficient quantity to sell",
                status_code=422,
                details={"held": held, "requested": body.quantity},
            )
        holding_row.quantity -= body.quantity
        if holding_row.quantity == 0:
            await session.delete(holding_row)
            holding_row = None
        portfolio_row.cash_balance += total

    portfolio_row.updated_at = now
    tx_row = TransactionRow(
        id=str(uuid.uuid4()),
        portfolio_id=portfolio_row.id,
        type=body.type,
        asset_id=body.asset_id,
        quantity=body.quantity,
        price=price,
        total=total,
        source=quote.source,
        executed_at=now,
        note=body.note,
    )
    session.add(tx_row)
    await session.commit()
    await session.refresh(portfolio_row)
    await session.refresh(tx_row)

    portfolio = await _row_to_portfolio(session, portfolio_row)
    transaction = await _transaction_from_row(tx_row)

    holding: Holding | None = None
    if body.type == "buy" and holding_row is not None:
        await session.refresh(holding_row)
        asset = await market_data.get_asset(body.asset_id)
        holding = _holding_from_row(
            holding_row,
            market_price=price,
            source=quote.source,
            asset=asset,
        )
    elif body.type == "sell" and holding_row is not None:
        await session.refresh(holding_row)
        asset = await market_data.get_asset(body.asset_id)
        holding = _holding_from_row(
            holding_row,
            market_price=price,
            source=quote.source,
            asset=asset,
        )

    return TransactionResponse(
        transaction=transaction,
        portfolio=portfolio,
        holding=holding,
    )
