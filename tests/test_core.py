from datetime import datetime
from pathlib import Path
import tempfile

from analysis_engine import Analysis, evaluate_analyses, export_tracked_symbols, save_analyses, load_analyses
from config import AppConfig
from dashboard import build_summary
from excel_export import export_to_excel
from mt5_data import aggregate_by_symbol, latest_snapshot_positions, load_portfolio, load_prices
from utils import parse_datetime, parse_float


def make_config(tmp: Path) -> AppConfig:
    return AppConfig(mt5_common_folder=str(tmp))


def test_import_prices_portfolio_latest_snapshot_and_score_buy():
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
            "SnapshotTime;AccountLogin;AccountCurrency;Symbol;Ticket;Type;Volume;OpenTime;OpenPrice;CurrentPrice;PercentFromOpen;Profit;Swap;Magic;Comment;ExposureValue\n"
            "2026-01-14 10:00:00;1;USD;AAPL;7;BUY;1;2026-01-01 10:00:00;100;105;5;50;0;0;old;105\n"
            "2026-01-15 10:00:00;1;USD;AAPL;7;BUY;1;2026-01-01 10:00:00;100;110.1;10.1;101;0;0;new;110.1\n"
            "2026-01-15 10:00:00;1;USD;MSFT;8;BUY;2;2026-01-01 10:00:00;50;60;20;40;0;0;new;120\n",
            encoding="utf-8",
        )
        cfg = make_config(tmp)
        prices = load_prices(cfg)
        positions = load_portfolio(cfg)
        current = latest_snapshot_positions(positions)
        assert len(prices) == 4
        assert prices[0].price_used == 100.1
        assert len(current) == 2
        summary = build_summary([], current, positions)
        assert summary.open_positions == 2
        assert summary.portfolio_profit == 141
        assert round(sum(r.share_pct for r in aggregate_by_symbol(current)), 6) == 100
        analysis = Analysis("a1", datetime(2026, 1, 1, 10), "AAPL", "BUY", 14, 100.1, 0, 0, "", "", "OPEN", "")
        result = evaluate_analyses(cfg, [analysis], prices)[0]
        assert round(result.return_1d or 0, 2) == 3.0
        assert result.result == "HIT"


def test_analyses_csv_and_tracked_symbols_in_common_folder():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        cfg = make_config(tmp)
        analyses = [
            Analysis("a1", datetime.now(), "AAPL", "BUY", 14, 0, 0, 0, "", "", "OPEN", ""),
            Analysis("a2", datetime.now(), "AAPL", "WATCH", 14, 0, 0, 0, "", "", "OPEN", ""),
            Analysis("a3", datetime.now(), "MSFT", "BUY", 14, 0, 0, 0, "", "", "CLOSED", ""),
        ]
        save_analyses(cfg, analyses)
        assert (tmp / "Analyses.csv").exists()
        assert len(load_analyses(cfg)) == 3
        assert export_tracked_symbols(cfg, analyses) == 1
        assert (tmp / "TrackedSymbols.csv").read_text(encoding="utf-8") == "Symbol\nAAPL\n"


def test_parsing_and_excel_export():
    assert parse_float("1 234,5") == 1234.5
    assert parse_float("1,234.5") == 1234.5
    assert parse_datetime("7/2/2026 1:02 PM") is not None
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        cfg = make_config(tmp)
        result_path = export_to_excel(tmp, [], [], [], [], build_summary([], [], []))
        assert result_path.exists()
        assert result_path.suffix == ".xlsx"
