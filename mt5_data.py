"""Načítání MT5 CSV souborů a normalizace cen/portfolia."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from config import AppConfig
from utils import parse_datetime, parse_float, read_semicolon_csv


@dataclass
class PriceSnapshot:
    snapshot_time: datetime
    symbol: str
    bid: float
    ask: float
    last: float
    spread: float
    point: float
    digits: int
    price_used: float | None


@dataclass
class PortfolioPosition:
    snapshot_time: datetime
    account_login: str
    account_currency: str
    symbol: str
    ticket: str
    type: str
    volume: float
    open_time: datetime | None
    open_price: float
    current_price: float
    percent_from_open: float
    profit: float
    swap: float
    magic: str
    comment: str


def calculate_price_used(bid: float, ask: float, last: float) -> float | None:
    if last > 0:
        return last
    if bid > 0 and ask > 0:
        return (bid + ask) / 2
    if bid > 0:
        return bid
    return None


def load_prices(config: AppConfig) -> list[PriceSnapshot]:
    rows = read_semicolon_csv(config.expanded_mt5_folder / config.analysis_prices_file)
    prices: list[PriceSnapshot] = []
    for row in rows:
        snapshot_time = parse_datetime(row.get("SnapshotTime"))
        symbol = (row.get("Symbol") or "").strip().upper()
        if not snapshot_time or not symbol:
            continue
        bid = parse_float(row.get("Bid"))
        ask = parse_float(row.get("Ask"))
        last = parse_float(row.get("Last"))
        prices.append(
            PriceSnapshot(
                snapshot_time=snapshot_time,
                symbol=symbol,
                bid=bid,
                ask=ask,
                last=last,
                spread=parse_float(row.get("Spread")),
                point=parse_float(row.get("Point")),
                digits=int(parse_float(row.get("Digits"))),
                price_used=calculate_price_used(bid, ask, last),
            )
        )
    return sorted(prices, key=lambda item: (item.symbol, item.snapshot_time))


def load_portfolio(config: AppConfig) -> list[PortfolioPosition]:
    rows = read_semicolon_csv(config.expanded_mt5_folder / config.portfolio_positions_file)
    positions: list[PortfolioPosition] = []
    for row in rows:
        snapshot_time = parse_datetime(row.get("SnapshotTime"))
        if not snapshot_time:
            continue
        positions.append(
            PortfolioPosition(
                snapshot_time=snapshot_time,
                account_login=row.get("AccountLogin", ""),
                account_currency=row.get("AccountCurrency", ""),
                symbol=(row.get("Symbol") or "").strip().upper(),
                ticket=row.get("Ticket", ""),
                type=row.get("Type", ""),
                volume=parse_float(row.get("Volume")),
                open_time=parse_datetime(row.get("OpenTime")),
                open_price=parse_float(row.get("OpenPrice")),
                current_price=parse_float(row.get("CurrentPrice")),
                percent_from_open=parse_float(row.get("PercentFromOpen")),
                profit=parse_float(row.get("Profit")),
                swap=parse_float(row.get("Swap")),
                magic=row.get("Magic", ""),
                comment=row.get("Comment", ""),
            )
        )
    return positions


def latest_positions(positions: list[PortfolioPosition]) -> list[PortfolioPosition]:
    latest: dict[str, PortfolioPosition] = {}
    for pos in positions:
        if not pos.ticket:
            continue
        current = latest.get(pos.ticket)
        if current is None or pos.snapshot_time > current.snapshot_time:
            latest[pos.ticket] = pos
    return sorted(latest.values(), key=lambda item: item.symbol)
