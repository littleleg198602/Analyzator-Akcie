from datetime import datetime
from pathlib import Path
import tempfile

from analysis_engine import Analysis, evaluate_analyses, export_tracked_symbols
from config import AppConfig
from mt5_data import load_portfolio, load_prices, latest_positions


def make_config(tmp: Path) -> AppConfig:
    return AppConfig(mt5_common_folder=str(tmp))


def test_import_prices_portfolio_and_score_buy():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        (tmp / "MT5_Analysis_Prices.csv").write_text(
            "SnapshotTime;Symbol;Bid;Ask;Last;Spread;Point;Digits\n"
            "2026-01-01 10:00:00;AAPL;100;100.2;100.1;0.2;0.01;2\n"
            "2026-01-02 10:00:00;AAPL;103;103.2;103.1;0.2;0.01;2\n"
            "2026-01-06 10:00:00;AAPL;106;106.2;106.1;0.2;0.01;2\n"
            "2026-01-15 10:00:00;AAPL;110;110.2;110.1;0.2;0.01;2\n",
            encoding="utf-8",
        )
        (tmp / "MT5_Portfolio_Positions.csv").write_text(
            "SnapshotTime;AccountLogin;AccountCurrency;Symbol;Ticket;Type;Volume;OpenTime;OpenPrice;CurrentPrice;PercentFromOpen;Profit;Swap;Magic;Comment\n"
            "2026-01-15 10:00:00;1;USD;AAPL;7;BUY;1;2026-01-01 10:00:00;100;110.1;10.1;101;0;0;test\n",
            encoding="utf-8",
        )
        cfg = make_config(tmp)
        prices = load_prices(cfg)
        positions = load_portfolio(cfg)
        assert len(prices) == 4
        assert prices[0].price_used == 100.1
        assert len(latest_positions(positions)) == 1
        analysis = Analysis("a1", datetime(2026, 1, 1, 10), "AAPL", "BUY", 14, 100.1, 0, 0, "", "", "OPEN", "")
        result = evaluate_analyses(cfg, [analysis], prices)[0]
        assert round(result.return_1d or 0, 2) == 3.0
        assert result.result == "HIT"


def test_export_tracked_symbols():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        cfg = make_config(tmp)
        analyses = [
            Analysis("a1", datetime.now(), "AAPL", "BUY", 14, 0, 0, 0, "", "", "OPEN", ""),
            Analysis("a2", datetime.now(), "AAPL", "WATCH", 14, 0, 0, 0, "", "", "OPEN", ""),
            Analysis("a3", datetime.now(), "MSFT", "BUY", 14, 0, 0, 0, "", "", "CLOSED", ""),
        ]
        assert export_tracked_symbols(cfg, analyses) == 1
        assert (tmp / "TrackedSymbols.csv").read_text(encoding="utf-8") == "Symbol\nAAPL\n"
