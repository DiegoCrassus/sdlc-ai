"""Parse Stooq HTML pages for fallback scraping."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from bs4 import BeautifulSoup


@dataclass
class ScrapedQuote:
    symbol: str
    price: float
    change_percent: float | None
    source_url: str
    fetched_at: datetime


def parse_stooq_quote_page(html: str, *, symbol: str, source_url: str) -> ScrapedQuote | None:
    """Extract last price from a Stooq symbol page HTML fixture or live page."""
    soup = BeautifulSoup(html, "html.parser")

    # Primary: id="f13" is commonly used for last price on Stooq pages
    price_el = soup.find(id="f13")
    if price_el:
        price_text = price_el.get_text(strip=True).replace(",", ".")
        try:
            price = float(re.sub(r"[^\d.\-]", "", price_text))
            change_el = soup.find(id="f14")
            change_pct = None
            if change_el:
                pct_match = re.search(r"([\-\d.]+)\s*%", change_el.get_text())
                if pct_match:
                    change_pct = float(pct_match.group(1))
            return ScrapedQuote(
                symbol=symbol.upper(),
                price=price,
                change_percent=change_pct,
                source_url=source_url,
                fetched_at=datetime.now(UTC),
            )
        except ValueError:
            pass

    # Fallback: meta or table cell with numeric price
    for cell in soup.select("td, span"):
        text = cell.get_text(strip=True)
        if re.match(r"^\d[\d,.]+$", text) and len(text) >= 3:
            try:
                price = float(text.replace(",", "."))
                return ScrapedQuote(
                    symbol=symbol.upper(),
                    price=price,
                    change_percent=None,
                    source_url=source_url,
                    fetched_at=datetime.now(UTC),
                )
            except ValueError:
                continue
    return None
