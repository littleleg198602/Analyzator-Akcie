"""Konfigurace aplikace MT5 analyzátor."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

APP_NAME = "MT5 analyzátor akcií"
CONFIG_FILE = Path("config.json")
DATA_DIR = Path("data")
ANALYSES_FILE = DATA_DIR / "analyzy.csv"


@dataclass
class AppConfig:
    mt5_common_folder: str = "%APPDATA%\\MetaQuotes\\Terminal\\Common\\Files\\"
    analysis_prices_file: str = "MT5_Analysis_Prices.csv"
    portfolio_positions_file: str = "MT5_Portfolio_Positions.csv"
    tracked_symbols_file: str = "TrackedSymbols.csv"
    buy_success_pct: float = 3.0
    buy_fail_pct: float = -3.0
    short_success_pct: float = 3.0
    short_fail_pct: float = -3.0
    avoid_bad_pct: float = 5.0
    default_horizon_days: int = 14
    auto_refresh_on_start: bool = True

    @property
    def expanded_mt5_folder(self) -> Path:
        expanded = os.path.expandvars(self.mt5_common_folder)
        return Path(expanded).expanduser()


def load_config() -> AppConfig:
    DATA_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        cfg = AppConfig()
        save_config(cfg)
        return cfg
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        defaults = asdict(AppConfig())
        defaults.update(raw)
        return AppConfig(**defaults)
    except Exception:
        return AppConfig()


def save_config(config: AppConfig) -> None:
    CONFIG_FILE.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")
