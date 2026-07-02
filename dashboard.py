"""Výpočty souhrnů pro GUI dashboard."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from analysis_engine import AnalysisResult
from mt5_data import PortfolioPosition


@dataclass
class DashboardSummary:
    total_analyses: int
    scorable_analyses: int
    buy_hit_rate: float | None
    short_hit_rate: float | None
    avoid_hit_rate: float | None
    result_counts: Counter
    portfolio_profit: float
    open_positions: int
    best_position: PortfolioPosition | None
    worst_position: PortfolioPosition | None
    profit_history: list[tuple[str, float]]


def hit_rate(results: list[AnalysisResult], verdict: str) -> float | None:
    scoped = [r for r in results if r.analysis.verdict == verdict and r.result in {"HIT", "MISS"}]
    if not scoped:
        return None
    return sum(1 for r in scoped if r.result == "HIT") / len(scoped)


def build_summary(results: list[AnalysisResult], latest_positions: list[PortfolioPosition], all_positions: list[PortfolioPosition]) -> DashboardSummary:
    counts = Counter(r.result for r in results)
    scorable = sum(counts[name] for name in ("HIT", "MISS", "NEUTRAL"))
    best = max(latest_positions, key=lambda p: p.percent_from_open, default=None)
    worst = min(latest_positions, key=lambda p: p.percent_from_open, default=None)
    grouped: defaultdict[str, float] = defaultdict(float)
    for pos in all_positions:
        grouped[pos.snapshot_time.strftime("%Y-%m-%d %H:%M:%S")] += pos.profit
    return DashboardSummary(
        total_analyses=len(results),
        scorable_analyses=scorable,
        buy_hit_rate=hit_rate(results, "BUY"),
        short_hit_rate=hit_rate(results, "SHORT"),
        avoid_hit_rate=hit_rate(results, "AVOID"),
        result_counts=counts,
        portfolio_profit=sum(p.profit for p in latest_positions),
        open_positions=len(latest_positions),
        best_position=best,
        worst_position=worst,
        profit_history=sorted(grouped.items()),
    )
