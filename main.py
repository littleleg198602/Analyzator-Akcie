"""Desktopová aplikace pro MT5 analýzy a portfolio."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from analysis_engine import VERDICTS, add_analysis, evaluate_analyses, export_tracked_symbols, load_analyses, save_analyses
from config import APP_NAME, AppConfig, load_config, save_config
from dashboard import build_summary
from mt5_data import latest_positions, load_portfolio, load_prices
from utils import fmt_pct, parse_float


class MT5AnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(980, 620)
        self.config_data: AppConfig = load_config()
        self.prices = []
        self.positions = []
        self.latest_positions = []
        self.analyses = []
        self.results = []
        self._build_ui()
        if self.config_data.auto_refresh_on_start:
            self.refresh_all(show_message=False)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(self, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")
        ttk.Button(toolbar, text="Obnovit MT5 data", command=self.refresh_all).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Zapsat TrackedSymbols.csv", command=self.write_tracked_symbols).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Uložit nastavení", command=self.save_settings).pack(side="left", padx=3)
        ttk.Label(toolbar, text="MT5 Common Files:").pack(side="left", padx=(20, 3))
        self.folder_var = tk.StringVar(value=self.config_data.mt5_common_folder)
        ttk.Entry(toolbar, textvariable=self.folder_var, width=62).pack(side="left", fill="x", expand=True, padx=3)
        ttk.Button(toolbar, text="Vybrat…", command=self.pick_folder).pack(side="left", padx=3)

        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, sticky="nsew")
        self.dashboard_tab = ttk.Frame(self.tabs, padding=10)
        self.analysis_tab = ttk.Frame(self.tabs, padding=10)
        self.results_tab = ttk.Frame(self.tabs, padding=10)
        self.portfolio_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.analysis_tab, text="Analýzy")
        self.tabs.add(self.results_tab, text="Výsledky analýz")
        self.tabs.add(self.portfolio_tab, text="MT5 portfolio")
        self._build_dashboard_tab()
        self._build_analysis_tab()
        self.results_tree = self._make_tree(self.results_tab, ("ID", "Symbol", "Verdikt", "1D", "5D", "14D", "Horizont", "Výsledek"))
        self.portfolio_tree = self._make_tree(self.portfolio_tab, ("Čas", "Symbol", "Ticket", "Typ", "Volume", "Open", "Current", "%", "Profit", "Komentář"))

    def _build_dashboard_tab(self) -> None:
        self.summary_text = tk.Text(self.dashboard_tab, height=16, wrap="word")
        self.summary_text.pack(fill="x")
        charts = ttk.Frame(self.dashboard_tab)
        charts.pack(fill="both", expand=True, pady=8)
        self.result_canvas = tk.Canvas(charts, height=220, bg="white")
        self.result_canvas.pack(side="left", fill="both", expand=True, padx=4)
        self.portfolio_canvas = tk.Canvas(charts, height=220, bg="white")
        self.portfolio_canvas.pack(side="left", fill="both", expand=True, padx=4)

    def _build_analysis_tab(self) -> None:
        form = ttk.LabelFrame(self.analysis_tab, text="Nová analýza", padding=8)
        form.pack(fill="x")
        self.symbol_var = tk.StringVar()
        self.verdict_var = tk.StringVar(value="BUY")
        self.horizon_var = tk.StringVar(value=str(self.config_data.default_horizon_days))
        self.start_price_var = tk.StringVar()
        self.reason_var = tk.StringVar()
        labels = [("Symbol", self.symbol_var), ("Horizont dnů", self.horizon_var), ("Start cena", self.start_price_var), ("Důvod", self.reason_var)]
        ttk.Label(form, text="Symbol").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.symbol_var, width=12).grid(row=1, column=0, padx=3, sticky="ew")
        ttk.Label(form, text="Verdikt").grid(row=0, column=1, sticky="w")
        ttk.Combobox(form, textvariable=self.verdict_var, values=VERDICTS, width=10, state="readonly").grid(row=1, column=1, padx=3)
        for idx, (label, var) in enumerate(labels[1:], start=2):
            ttk.Label(form, text=label).grid(row=0, column=idx, sticky="w")
            ttk.Entry(form, textvariable=var, width=18 if label != "Důvod" else 50).grid(row=1, column=idx, padx=3, sticky="ew")
        ttk.Button(form, text="Přidat analýzu", command=self.add_analysis_from_form).grid(row=1, column=5, padx=6)
        self.analysis_tree = self._make_tree(self.analysis_tab, ("ID", "Čas", "Symbol", "Verdikt", "Horizont", "Start", "Status", "Důvod"))

    def _make_tree(self, parent: ttk.Frame, columns: tuple[str, ...]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="w")
        tree.pack(fill="both", expand=True, pady=8)
        return tree

    def pick_folder(self) -> None:
        folder = filedialog.askdirectory(title="Vyber MT5 Common\\Files složku")
        if folder:
            self.folder_var.set(folder)

    def save_settings(self) -> None:
        self.config_data.mt5_common_folder = self.folder_var.get().strip()
        save_config(self.config_data)
        messagebox.showinfo(APP_NAME, "Nastavení bylo uloženo.")

    def refresh_all(self, show_message: bool = True) -> None:
        self.config_data.mt5_common_folder = self.folder_var.get().strip()
        save_config(self.config_data)
        self.prices = load_prices(self.config_data)
        self.positions = load_portfolio(self.config_data)
        self.latest_positions = latest_positions(self.positions)
        self.analyses = load_analyses(self.config_data)
        self.results = evaluate_analyses(self.config_data, self.analyses, self.prices)
        self.redraw_all()
        if show_message:
            messagebox.showinfo(APP_NAME, f"Hotovo. Ceny: {len(self.prices)}, pozice: {len(self.positions)}, analýzy: {len(self.analyses)}")

    def add_analysis_from_form(self) -> None:
        symbol = self.symbol_var.get().strip().upper()
        if not symbol:
            messagebox.showwarning(APP_NAME, "Zadej symbol.")
            return
        add_analysis(
            self.config_data,
            symbol=symbol,
            verdict=self.verdict_var.get(),
            horizon_days=int(parse_float(self.horizon_var.get(), self.config_data.default_horizon_days)),
            start_price=parse_float(self.start_price_var.get()),
            reason=self.reason_var.get(),
        )
        self.symbol_var.set("")
        self.start_price_var.set("")
        self.reason_var.set("")
        self.refresh_all(show_message=False)

    def write_tracked_symbols(self) -> None:
        count = export_tracked_symbols(self.config_data, load_analyses(self.config_data))
        messagebox.showinfo(APP_NAME, f"Zapsáno symbolů do TrackedSymbols.csv: {count}")

    def redraw_all(self) -> None:
        self._redraw_analysis_tree()
        self._redraw_results_tree()
        self._redraw_portfolio_tree()
        self._redraw_dashboard()

    def _clear_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

    def _redraw_analysis_tree(self) -> None:
        self._clear_tree(self.analysis_tree)
        for a in self.analyses:
            self.analysis_tree.insert("", "end", values=(a.analysis_id[:8], a.analysis_datetime, a.symbol, a.verdict, a.horizon_days, a.start_price or "", a.status, a.reason))

    def _redraw_results_tree(self) -> None:
        self._clear_tree(self.results_tree)
        for r in self.results:
            self.results_tree.insert("", "end", values=(r.analysis.analysis_id[:8], r.analysis.symbol, r.analysis.verdict, fmt_pct(r.return_1d), fmt_pct(r.return_5d), fmt_pct(r.return_14d), fmt_pct(r.horizon_return_pct), r.result))

    def _redraw_portfolio_tree(self) -> None:
        self._clear_tree(self.portfolio_tree)
        for p in self.latest_positions:
            self.portfolio_tree.insert("", "end", values=(p.snapshot_time, p.symbol, p.ticket, p.type, p.volume, p.open_price, p.current_price, fmt_pct(p.percent_from_open), f"{p.profit:.2f}", p.comment))

    def _redraw_dashboard(self) -> None:
        summary = build_summary(self.results, self.latest_positions, self.positions)
        self.summary_text.delete("1.0", "end")
        best = summary.best_position
        worst = summary.worst_position
        lines = [
            f"Celkem analýz: {summary.total_analyses}",
            f"Skórovatelné analýzy: {summary.scorable_analyses}",
            f"BUY hit rate: {fmt_pct(summary.buy_hit_rate * 100) if summary.buy_hit_rate is not None else ''}",
            f"SHORT hit rate: {fmt_pct(summary.short_hit_rate * 100) if summary.short_hit_rate is not None else ''}",
            f"AVOID hit rate: {fmt_pct(summary.avoid_hit_rate * 100) if summary.avoid_hit_rate is not None else ''}",
            f"HIT/MISS/NEUTRAL/WATCH: {summary.result_counts.get('HIT',0)} / {summary.result_counts.get('MISS',0)} / {summary.result_counts.get('NEUTRAL',0)} / {summary.result_counts.get('WATCH ONLY',0)}",
            f"Aktuální profit MT5: {summary.portfolio_profit:.2f}",
            f"Počet otevřených pozic: {summary.open_positions}",
            f"Nejlepší pozice: {best.symbol + ' ' + fmt_pct(best.percent_from_open) if best else ''}",
            f"Nejhorší pozice: {worst.symbol + ' ' + fmt_pct(worst.percent_from_open) if worst else ''}",
        ]
        self.summary_text.insert("end", "\n".join(lines))
        self._draw_bar_chart(self.result_canvas, {k: summary.result_counts.get(k, 0) for k in ("HIT", "MISS", "NEUTRAL", "WATCH ONLY")}, "Výsledky analýz")
        self._draw_bar_chart(self.portfolio_canvas, {p.symbol + "\n" + p.ticket: p.percent_from_open for p in self.latest_positions[:10]}, "MT5 pozice podle %")

    def _draw_bar_chart(self, canvas: tk.Canvas, data: dict[str, float], title: str) -> None:
        canvas.delete("all")
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 220)
        canvas.create_text(width / 2, 16, text=title, font=("Segoe UI", 11, "bold"))
        if not data:
            canvas.create_text(width / 2, height / 2, text="Žádná data")
            return
        max_value = max(abs(v) for v in data.values()) or 1
        bar_width = max(20, (width - 60) / len(data) - 10)
        zero_y = height - 35
        for i, (label, value) in enumerate(data.items()):
            x1 = 35 + i * (bar_width + 10)
            bar_h = (abs(value) / max_value) * (height - 80)
            y1 = zero_y - bar_h if value >= 0 else zero_y
            y2 = zero_y if value >= 0 else zero_y + bar_h
            canvas.create_rectangle(x1, y1, x1 + bar_width, y2, fill="#2f80ed" if value >= 0 else "#eb5757")
            canvas.create_text(x1 + bar_width / 2, y1 - 10 if value >= 0 else y2 + 10, text=f"{value:.1f}")
            canvas.create_text(x1 + bar_width / 2, height - 15, text=label[:12])


def main() -> None:
    app = MT5AnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
