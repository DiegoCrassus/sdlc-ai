import pytest

from app.backend.utils.asset_id import AssetIdError, format_asset_id, parse_asset_id


def test_format_asset_id():
    assert format_asset_id("stock", "aapl") == "stock:AAPL"


def test_parse_asset_id_valid():
    assert parse_asset_id("crypto:btc") == ("crypto", "BTC")


def test_parse_asset_id_invalid_class():
    with pytest.raises(AssetIdError):
        parse_asset_id("bond:US10Y")


def test_parse_asset_id_missing_symbol():
    with pytest.raises(AssetIdError):
        parse_asset_id("stock:")
