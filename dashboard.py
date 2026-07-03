"""Výpočty souhrnů pro GUI dashboard."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from analysis_engine import AnalysisResult
from mt5_data import PortfolioPosition, SymbolPortfolioRow, aggregate_by_symbol, portfolio_stats, profit_history_by_snapshot, symbol_performance_history


@dataclass
class DashboardSummary:
    total_analyses: int
    scorable_analyses: int
    buy_hit_rate: float | None
    short_hit_rate: float | None
    avoid_hit_rate: float | None
    result_counts: Counter
    best_analysis: AnalysisResult | None
    worst_analysis: AnalysisResult | None
    portfolio_profit: float
    open_positions: int
    total_value: float
    largest_position: SymbolPortfolioRow | None
    top5_positions: list[SymbolPortfolioRow]
    best_position: PortfolioPosition | None
    worst_position: PortfolioPosition | None
    avg_percent: float | None
    median_percent: float | None
    positive_count: int
    negative_count: int
    symbol_rows: list[SymbolPortfolioRow]
    profit_history: list[tuple]
    symbol_performance_history: dict[str, list[tuple]]
    uses_estimated_share: bool
    uses_average_performance: bool


def hit_rate(results: list[AnalysisResult], verdict: str) -> float | None:
    scoped = [r for r in results if r.analysis.verdict == verdict and r.result in {"HIT", "MISS"}]
    if not scoped:
        return None
    return sum(1 for r in scoped if r.result == "HIT") / len(scoped)


def build_summary(results: list[AnalysisResult], current_positions: list[PortfolioPosition], all_positions: list[PortfolioPosition]) -> DashboardSummary:
    counts = Counter(r.result for r in results)
    scorable = sum(counts[name] for name in ("HIT", "MISS", "NEUTRAL"))
    result_with_return = [r for r in results if r.horizon_return_pct is not None]
    best_analysis = max(result_with_return, key=lambda r: r.horizon_return_pct or 0, default=None)
    worst_analysis = min(result_with_return, key=lambda r: r.horizon_return_pct or 0, default=None)
    symbol_rows = aggregate_by_symbol(current_positions)
    stats = portfolio_stats(current_positions)
    return DashboardSummary(
        total_analyses=len(results),
        scorable_analyses=scorable,
        buy_hit_rate=hit_rate(results, "BUY"),
        short_hit_rate=hit_rate(results, "SHORT"),
        avoid_hit_rate=hit_rate(results, "AVOID"),
        result_counts=counts,
        best_analysis=best_analysis,
        worst_analysis=worst_analysis,
        portfolio_profit=float(stats["total_profit"] or 0),
        open_positions=int(stats["open_positions"] or 0),
        total_value=float(stats["total_value"] or 0),
        largest_position=symbol_rows[0] if symbol_rows else None,
        top5_positions=symbol_rows[:5],
        best_position=max(current_positions, key=lambda p: p.percent_from_open, default=None),
        worst_position=min(current_positions, key=lambda p: p.percent_from_open, default=None),
        avg_percent=stats["avg_percent"],
        median_percent=stats["median_percent"],
        positive_count=int(stats["positive_count"] or 0),
        negative_count=int(stats["negative_count"] or 0),
        symbol_rows=symbol_rows,
        profit_history=profit_history_by_snapshot(all_positions),
        symbol_performance_history=symbol_performance_history(all_positions),
        uses_estimated_share=any(row.value_source == "EstimatedValue" for row in symbol_rows),
        uses_average_performance=any(row.value_source == "EstimatedValue" for row in symbol_rows),
    )
