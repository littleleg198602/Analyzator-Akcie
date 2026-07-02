"""Načítání MT5 CSV souborů a normalizace cen/portfolia."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, median

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
    contract_size: float = 0.0
    open_value: float = 0.0
    current_value: float = 0.0
    exposure_value: float = 0.0
    market_value: float = 0.0

    @property
    def estimated_value(self) -> float:
        return abs(self.volume * self.current_price)

    @property
    def value_for_share(self) -> float:
        if self.exposure_value > 0:
            return self.exposure_value
        if self.market_value > 0:
            return self.market_value
        return self.estimated_value

    @property
    def value_source(self) -> str:
        if self.exposure_value > 0:
            return "ExposureValue"
        if self.market_value > 0:
            return "MarketValue"
        return "EstimatedValue"


@dataclass
class SymbolPortfolioRow:
    symbol: str
    positions_count: int
    value: float
    share_pct: float
    profit: float
    weighted_percent_from_open: float
    best_ticket_pct: float
    worst_ticket_pct: float
    value_source: str


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
        prices.append(PriceSnapshot(snapshot_time, symbol, bid, ask, last, parse_float(row.get("Spread")), parse_float(row.get("Point")), int(parse_float(row.get("Digits"))), calculate_price_used(bid, ask, last)))
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
                contract_size=parse_float(row.get("ContractSize")),
                open_value=parse_float(row.get("OpenValue")),
                current_value=parse_float(row.get("CurrentValue")),
                exposure_value=parse_float(row.get("ExposureValue")),
                market_value=parse_float(row.get("MarketValue")),
            )
        )
    return sorted(positions, key=lambda item: item.snapshot_time)


def latest_snapshot_time(positions: list[PortfolioPosition]) -> datetime | None:
    return max((p.snapshot_time for p in positions), default=None)


def latest_snapshot_positions(positions: list[PortfolioPosition]) -> list[PortfolioPosition]:
    latest_time = latest_snapshot_time(positions)
    if latest_time is None:
        return []
    return [p for p in positions if p.snapshot_time == latest_time]


def profit_history_by_snapshot(positions: list[PortfolioPosition]) -> list[tuple[datetime, float]]:
    grouped: dict[datetime, float] = defaultdict(float)
    for pos in positions:
        grouped[pos.snapshot_time] += pos.profit
    return sorted(grouped.items())


def aggregate_by_symbol(positions: list[PortfolioPosition]) -> list[SymbolPortfolioRow]:
    grouped: dict[str, list[PortfolioPosition]] = defaultdict(list)
    for pos in positions:
        if pos.symbol:
            grouped[pos.symbol].append(pos)
    total_value = sum(p.value_for_share for items in grouped.values() for p in items)
    rows: list[SymbolPortfolioRow] = []
    for symbol, items in grouped.items():
        value = sum(p.value_for_share for p in items)
        profit = sum(p.profit for p in items)
        weighted_base = sum(p.value_for_share for p in items if p.value_source != "EstimatedValue")
        if weighted_base > 0:
            weighted_pct = sum(p.percent_from_open * p.value_for_share for p in items if p.value_source != "EstimatedValue") / weighted_base
            source = "ExposureValue/MarketValue"
        else:
            weighted_pct = mean([p.percent_from_open for p in items]) if items else 0.0
            source = "EstimatedValue"
        rows.append(SymbolPortfolioRow(symbol, len(items), value, (value / total_value * 100) if total_value else 0.0, profit, weighted_pct, max(p.percent_from_open for p in items), min(p.percent_from_open for p in items), source))
    return sorted(rows, key=lambda item: item.share_pct, reverse=True)


def portfolio_stats(positions: list[PortfolioPosition]) -> dict[str, float | int | None]:
    values = [p.percent_from_open for p in positions]
    return {
        "total_profit": sum(p.profit for p in positions),
        "open_positions": len(positions),
        "total_value": sum(p.value_for_share for p in positions),
        "avg_percent": mean(values) if values else None,
        "median_percent": median(values) if values else None,
        "positive_count": sum(1 for v in values if v > 0),
        "negative_count": sum(1 for v in values if v < 0),
    }

def symbol_performance_history(positions: list[PortfolioPosition]) -> dict[str, list[tuple[datetime, float]]]:
    """Vrátí časovou řadu procentuálního výkonu podle symbolu přes historii snapshotů.

    Pro každý SnapshotTime agreguje otevřené tickety stejného symbolu. Pokud je
    dostupný ExposureValue/MarketValue, použije vážený průměr; jinak obyčejný
    průměr PercentFromOpen. Symbol se v řadě objeví až od okamžiku, kdy se
    v MT5 historii poprvé objevil, takže nově otevřené akcie začnou kreslit
    čáru později.
    """
    by_time_symbol: dict[tuple[datetime, str], list[PortfolioPosition]] = defaultdict(list)
    for pos in positions:
        if pos.symbol:
            by_time_symbol[(pos.snapshot_time, pos.symbol)].append(pos)

    series: dict[str, list[tuple[datetime, float]]] = defaultdict(list)
    for (snapshot_time, symbol), items in sorted(by_time_symbol.items()):
        weighted_base = sum(p.value_for_share for p in items if p.value_source != "EstimatedValue")
        if weighted_base > 0:
            value = sum(p.percent_from_open * p.value_for_share for p in items if p.value_source != "EstimatedValue") / weighted_base
        else:
            value = mean([p.percent_from_open for p in items]) if items else 0.0
        series[symbol].append((snapshot_time, value))
    return dict(series)

