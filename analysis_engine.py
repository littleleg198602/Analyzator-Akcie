"""Ukládání analýz a výpočet úspěšnosti."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from config import ANALYSES_FILE, AppConfig
from mt5_data import PriceSnapshot
from utils import parse_datetime, parse_float, read_semicolon_csv, write_semicolon_csv

ANALYSIS_FIELDS = [
    "AnalysisID", "AnalysisDateTime", "Symbol", "Verdict", "HorizonDays", "StartPrice",
    "TargetPct", "StopPct", "Risk", "Reason", "Status", "Notes",
]
VERDICTS = ("BUY", "AVOID", "SHORT", "WATCH")
STATUSES = ("OPEN", "CLOSED", "CANCELLED")


@dataclass
class Analysis:
    analysis_id: str
    analysis_datetime: datetime
    symbol: str
    verdict: str
    horizon_days: int
    start_price: float
    target_pct: float
    stop_pct: float
    risk: str
    reason: str
    status: str
    notes: str


@dataclass
class AnalysisResult:
    analysis: Analysis
    current_price: float | None
    current_return_pct: float | None
    price_1d: float | None
    return_1d: float | None
    price_5d: float | None
    return_5d: float | None
    price_14d: float | None
    return_14d: float | None
    horizon_price: float | None
    horizon_return_pct: float | None
    max_runup_pct: float | None
    max_drawdown_pct: float | None
    result: str
    comment: str


def load_analyses(config: AppConfig) -> list[Analysis]:
    rows = read_semicolon_csv(ANALYSES_FILE)
    analyses: list[Analysis] = []
    for row in rows:
        dt = parse_datetime(row.get("AnalysisDateTime"))
        symbol = (row.get("Symbol") or "").strip().upper()
        if not dt or not symbol:
            continue
        analyses.append(
            Analysis(
                analysis_id=row.get("AnalysisID") or str(uuid4()),
                analysis_datetime=dt,
                symbol=symbol,
                verdict=(row.get("Verdict") or "WATCH").strip().upper(),
                horizon_days=int(parse_float(row.get("HorizonDays"), config.default_horizon_days)),
                start_price=parse_float(row.get("StartPrice")),
                target_pct=parse_float(row.get("TargetPct")),
                stop_pct=parse_float(row.get("StopPct")),
                risk=row.get("Risk", ""),
                reason=row.get("Reason", ""),
                status=(row.get("Status") or "OPEN").strip().upper(),
                notes=row.get("Notes", ""),
            )
        )
    return analyses


def save_analyses(analyses: list[Analysis]) -> None:
    rows = []
    for item in analyses:
        rows.append({
            "AnalysisID": item.analysis_id,
            "AnalysisDateTime": item.analysis_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": item.symbol,
            "Verdict": item.verdict,
            "HorizonDays": item.horizon_days,
            "StartPrice": item.start_price or "",
            "TargetPct": item.target_pct or "",
            "StopPct": item.stop_pct or "",
            "Risk": item.risk,
            "Reason": item.reason,
            "Status": item.status,
            "Notes": item.notes,
        })
    write_semicolon_csv(ANALYSES_FILE, ANALYSIS_FIELDS, rows)


def add_analysis(config: AppConfig, symbol: str, verdict: str, horizon_days: int | None, start_price: float, reason: str, risk: str = "", notes: str = "") -> Analysis:
    item = Analysis(
        analysis_id=str(uuid4()),
        analysis_datetime=datetime.now().replace(microsecond=0),
        symbol=symbol.strip().upper(),
        verdict=verdict.strip().upper(),
        horizon_days=horizon_days or config.default_horizon_days,
        start_price=start_price,
        target_pct=0.0,
        stop_pct=0.0,
        risk=risk,
        reason=reason,
        status="OPEN",
        notes=notes,
    )
    analyses = load_analyses(config)
    analyses.append(item)
    save_analyses(analyses)
    return item


def first_price_at_or_after(prices: list[PriceSnapshot], symbol: str, moment: datetime) -> float | None:
    candidates = [p for p in prices if p.symbol == symbol and p.price_used and p.snapshot_time >= moment]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item.snapshot_time).price_used


def latest_price(prices: list[PriceSnapshot], symbol: str) -> float | None:
    candidates = [p for p in prices if p.symbol == symbol and p.price_used]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.snapshot_time).price_used


def raw_return(start_price: float, price: float | None) -> float | None:
    if start_price <= 0 or not price or price <= 0:
        return None
    return (price / start_price - 1) * 100


def performance_return(verdict: str, start_price: float, price: float | None) -> float | None:
    if start_price <= 0 or not price or price <= 0:
        return None
    if verdict == "SHORT":
        return (start_price / price - 1) * 100
    return raw_return(start_price, price)


def score_result(config: AppConfig, verdict: str, perf_ret: float | None, raw_ret: float | None) -> str:
    if verdict == "WATCH":
        return "WATCH ONLY"
    if perf_ret is None:
        return "ČEKÁ NA DATA"
    if verdict == "BUY":
        return threshold_score(perf_ret, config.buy_success_pct, config.buy_fail_pct)
    if verdict == "SHORT":
        return threshold_score(perf_ret, config.short_success_pct, config.short_fail_pct)
    if verdict == "AVOID":
        if raw_ret is None:
            return "ČEKÁ NA DATA"
        if raw_ret >= config.avoid_bad_pct:
            return "MISS"
        if raw_ret <= 0:
            return "HIT"
        return "NEUTRAL"
    return "NEZNÁMÉ"


def threshold_score(value: float, success: float, fail: float) -> str:
    if value >= success:
        return "HIT"
    if value <= fail:
        return "MISS"
    return "NEUTRAL"


def evaluate_analyses(config: AppConfig, analyses: list[Analysis], prices: list[PriceSnapshot]) -> list[AnalysisResult]:
    results: list[AnalysisResult] = []
    for item in analyses:
        start_price = item.start_price or first_price_at_or_after(prices, item.symbol, item.analysis_datetime) or 0.0
        current = latest_price(prices, item.symbol)
        p1 = first_price_at_or_after(prices, item.symbol, item.analysis_datetime + timedelta(days=1))
        p5 = first_price_at_or_after(prices, item.symbol, item.analysis_datetime + timedelta(days=5))
        p14 = first_price_at_or_after(prices, item.symbol, item.analysis_datetime + timedelta(days=14))
        ph = first_price_at_or_after(prices, item.symbol, item.analysis_datetime + timedelta(days=item.horizon_days))
        horizon_raw = raw_return(start_price, ph)
        horizon_perf = performance_return(item.verdict, start_price, ph)
        in_window = [p for p in prices if p.symbol == item.symbol and p.price_used and item.analysis_datetime <= p.snapshot_time <= item.analysis_datetime + timedelta(days=item.horizon_days)]
        raw_returns = [raw_return(start_price, p.price_used) for p in in_window]
        raw_returns = [r for r in raw_returns if r is not None]
        result = score_result(config, item.verdict, horizon_perf, horizon_raw)
        results.append(AnalysisResult(
            analysis=item,
            current_price=current,
            current_return_pct=performance_return(item.verdict, start_price, current),
            price_1d=p1,
            return_1d=performance_return(item.verdict, start_price, p1),
            price_5d=p5,
            return_5d=performance_return(item.verdict, start_price, p5),
            price_14d=p14,
            return_14d=performance_return(item.verdict, start_price, p14),
            horizon_price=ph,
            horizon_return_pct=horizon_perf,
            max_runup_pct=max(raw_returns) if raw_returns else None,
            max_drawdown_pct=min(raw_returns) if raw_returns else None,
            result=result,
            comment="Vyhodnoceno proti první dostupné ceně v daném horizontu nebo později.",
        ))
    return results


def export_tracked_symbols(config: AppConfig, analyses: list[Analysis]) -> int:
    symbols = sorted({a.symbol for a in analyses if a.status == "OPEN" and a.symbol})
    path = config.expanded_mt5_folder / config.tracked_symbols_file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Symbol\n" + "\n".join(symbols) + ("\n" if symbols else ""), encoding="utf-8")
    return len(symbols)
