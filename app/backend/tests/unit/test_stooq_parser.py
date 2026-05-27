"""Tests for Stooq HTML parser using saved fixtures."""

from pathlib import Path

from app.backend.src.market_data.scraping.stooq_parser import parse_stooq_quote_page

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_stooq_aapl_fixture() -> None:
    html = (FIXTURES / "stooq_aapl_quote.html").read_text(encoding="utf-8")
    result = parse_stooq_quote_page(
        html,
        symbol="AAPL",
        source_url="https://stooq.com/q/?s=aapl.us",
    )
    assert result is not None
    assert result.symbol == "AAPL"
    assert result.price == 189.50
    assert result.change_percent == 0.35


def test_parse_stooq_returns_none_on_empty_html() -> None:
    assert parse_stooq_quote_page("", symbol="X", source_url="https://stooq.com/q/?s=x") is None
