"""Desktopová aplikace pro MT5 analýzy a portfolio."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from analysis_engine import Analysis, VERDICTS, add_analysis, delete_analysis, evaluate_analyses, export_tracked_symbols, load_analyses, update_analysis
from config import APP_NAME, AppConfig, load_config, save_config
from dashboard import build_summary
from excel_export import export_to_excel
from mt5_data import aggregate_by_symbol, latest_snapshot_positions, load_portfolio, load_prices
from utils import fmt_pct, parse_datetime, parse_float

PERFORMANCE_FILTERS = ("TOP 10 + WORST 10", "Všechny symboly", "TOP 10 nejlepších", "TOP 10 nejhorších")
ANALYSIS_METRICS = ("aktuální výkon", "výkon po 1D", "výkon po 5D", "výkon po 14D", "výkon v horizontu analýzy")


class MT5AnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1320x860")
        self.minsize(1080, 700)
        self.config_data: AppConfig = load_config()
        self.prices = []
        self.positions = []
        self.current_positions = []
        self.analyses = []
        self.results = []
        self.log_var = tk.StringVar(value="")
        self._build_ui()
        self.update_expanded_path_label()
        if self.config_data.auto_refresh_on_start:
            self.refresh_all(show_message=False)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        toolbar = ttk.Frame(self, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")
        for text, command in [
            ("Obnovit MT5 data", self.refresh_all),
            ("Zapsat TrackedSymbols.csv", self.write_tracked_symbols),
            ("Přidat analýzu", self.open_add_dialog),
            ("Upravit analýzu", self.open_edit_dialog),
            ("Smazat analýzu", self.delete_selected_analysis),
            ("Export do Excelu", self.export_excel),
            ("Uložit nastavení", self.save_settings),
        ]:
            ttk.Button(toolbar, text=text, command=command).pack(side="left", padx=2)

        path_frame = ttk.Frame(self, padding=(8, 0, 8, 8))
        path_frame.grid(row=1, column=0, sticky="ew")
        path_frame.columnconfigure(1, weight=1)
        ttk.Label(path_frame, text="Zadaná cesta MT5 Common Files:").grid(row=0, column=0, sticky="w")
        self.folder_var = tk.StringVar(value=self.config_data.mt5_common_folder)
        self.folder_var.trace_add("write", lambda *_: self.update_expanded_path_label())
        ttk.Entry(path_frame, textvariable=self.folder_var).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(path_frame, text="Vybrat...", command=self.pick_folder).grid(row=0, column=2, padx=3)
        ttk.Label(path_frame, text="Skutečná cesta:").grid(row=1, column=0, sticky="w")
        self.expanded_path_var = tk.StringVar()
        ttk.Label(path_frame, textvariable=self.expanded_path_var).grid(row=1, column=1, columnspan=2, sticky="w")

        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=2, column=0, sticky="nsew")
        self.dashboard_tab = ttk.Frame(self.tabs, padding=10)
        self.analysis_tab = ttk.Frame(self.tabs, padding=10)
        self.results_tab = ttk.Frame(self.tabs, padding=10)
        self.portfolio_tab = ttk.Frame(self.tabs, padding=10)
        self.settings_tab = ttk.Frame(self.tabs, padding=10)
        for title, tab in [("Dashboard", self.dashboard_tab), ("Analýzy", self.analysis_tab), ("Výsledky analýz", self.results_tab), ("MT5 portfolio", self.portfolio_tab), ("Nastavení / Log", self.settings_tab)]:
            self.tabs.add(tab, text=title)
        self._build_dashboard_tab()
        self._build_analysis_tab()
        self._build_results_tab()
        self._build_portfolio_tab()
        self._build_settings_tab()

    def _build_dashboard_tab(self) -> None:
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.columnconfigure(1, weight=1)
        self.dashboard_tab.rowconfigure(2, weight=1)
        self.summary_text = tk.Text(self.dashboard_tab, height=12, wrap="word")
        self.summary_text.grid(row=0, column=0, columnspan=2, sticky="ew")
        controls = ttk.Frame(self.dashboard_tab)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(controls, text="Výkon akcií:").pack(side="left")
        self.performance_filter_var = tk.StringVar(value=PERFORMANCE_FILTERS[0])
        ttk.Combobox(controls, textvariable=self.performance_filter_var, values=PERFORMANCE_FILTERS, state="readonly", width=20).pack(side="left", padx=4)
        ttk.Label(controls, text="Analýzy:").pack(side="left", padx=(16, 0))
        self.analysis_metric_var = tk.StringVar(value=ANALYSIS_METRICS[-1])
        ttk.Combobox(controls, textvariable=self.analysis_metric_var, values=ANALYSIS_METRICS, state="readonly", width=24).pack(side="left", padx=4)
        ttk.Button(controls, text="Překreslit grafy", command=self._redraw_dashboard).pack(side="left", padx=4)
        self.share_canvas = tk.Canvas(self.dashboard_tab, height=260, bg="white")
        self.share_canvas.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        self.performance_canvas = tk.Canvas(self.dashboard_tab, height=260, bg="white")
        self.performance_canvas.grid(row=2, column=1, sticky="nsew", padx=4, pady=4)
        self.analysis_canvas = tk.Canvas(self.dashboard_tab, height=260, bg="white")
        self.analysis_canvas.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self.profit_canvas = tk.Canvas(self.dashboard_tab, height=260, bg="white")
        self.profit_canvas.grid(row=3, column=1, sticky="nsew", padx=4, pady=4)
        self.share_tree = self._make_tree(self.dashboard_tab, ("Symbol", "Hodnota", "Podíl %", "Profit", "% výkon"), height=6)
        self.share_tree.grid(row=4, column=0, sticky="nsew", padx=4)
        self.symbol_perf_tree = self._make_tree(self.dashboard_tab, ("Symbol", "Pozic", "Weighted %", "Profit", "Hodnota", "Best %", "Worst %"), height=6)
        self.symbol_perf_tree.grid(row=4, column=1, sticky="nsew", padx=4)
        self.symbol_history_canvas = tk.Canvas(self.dashboard_tab, height=300, bg="white")
        self.symbol_history_canvas.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=4, pady=8)

    def _build_analysis_tab(self) -> None:
        ttk.Label(self.analysis_tab, text="Analýzy se ukládají do Analyses.csv v MT5 Common Files složce. Přidání/upravení/smazání je přes horní tlačítka.").pack(anchor="w")
        self.analysis_tree = self._make_tree(self.analysis_tab, ("ID", "Čas", "Symbol", "Verdikt", "Horizont", "Start", "Target", "Stop", "Risk", "Status", "Důvod"))
        self.analysis_tree.pack(fill="both", expand=True, pady=8)

    def _build_results_tab(self) -> None:
        self.results_tree = self._make_tree(self.results_tab, ("ID", "Čas", "Symbol", "Verdikt", "Start", "Current", "Cur %", "1D", "5D", "14D", "Horizont", "Runup", "Drawdown", "Výsledek"))
        self.results_tree.pack(fill="both", expand=True)

    def _build_portfolio_tab(self) -> None:
        controls = ttk.Frame(self.portfolio_tab)
        controls.pack(fill="x")
        ttk.Label(controls, text="Zobrazení:").pack(side="left")
        self.portfolio_mode_var = tk.StringVar(value="poslední snapshot")
        ttk.Combobox(controls, textvariable=self.portfolio_mode_var, values=("poslední snapshot", "celá historie"), state="readonly", width=18).pack(side="left", padx=4)
        ttk.Button(controls, text="Překreslit", command=self._redraw_portfolio_tree).pack(side="left")
        self.portfolio_summary_var = tk.StringVar()
        ttk.Label(self.portfolio_tab, textvariable=self.portfolio_summary_var, justify="left").pack(anchor="w", pady=4)
        self.portfolio_tree = self._make_tree(self.portfolio_tab, ("Čas", "Symbol", "Ticket", "Typ", "Volume", "OpenTime", "Open", "Current", "%", "Profit", "Swap", "Komentář", "Exposure/Estimated"))
        self.portfolio_tree.pack(fill="both", expand=True)

    def _build_settings_tab(self) -> None:
        self.settings_tab.columnconfigure(1, weight=1)
        self.setting_vars: dict[str, tk.StringVar] = {}
        fields = ["analysis_prices_file", "portfolio_positions_file", "tracked_symbols_file", "analyses_file", "buy_success_pct", "buy_fail_pct", "short_success_pct", "short_fail_pct", "avoid_bad_pct", "default_horizon_days", "auto_refresh_on_start"]
        for row, field in enumerate(fields):
            ttk.Label(self.settings_tab, text=field).grid(row=row, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=str(getattr(self.config_data, field)))
            self.setting_vars[field] = var
            ttk.Entry(self.settings_tab, textvariable=var).grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(self.settings_tab, text="Log:").grid(row=len(fields), column=0, sticky="nw", pady=8)
        self.log_text = tk.Text(self.settings_tab, height=12)
        self.log_text.grid(row=len(fields), column=1, sticky="nsew", pady=8)

    def _make_tree(self, parent, columns: tuple[str, ...], height: int = 18) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="w")
        return tree

    def log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, "log_text"):
            self.log_text.insert("end", f"{stamp} {message}\n")
            self.log_text.see("end")

    def update_expanded_path_label(self) -> None:
        cfg = self._config_from_ui(save=False)
        self.expanded_path_var.set(str(cfg.expanded_mt5_folder))

    def _config_from_ui(self, save: bool = True) -> AppConfig:
        cfg = self.config_data
        cfg.mt5_common_folder = self.folder_var.get().strip() if hasattr(self, "folder_var") else cfg.mt5_common_folder
        if hasattr(self, "setting_vars"):
            for field, var in self.setting_vars.items():
                value = var.get().strip()
                current = getattr(cfg, field)
                if isinstance(current, bool):
                    setattr(cfg, field, value.upper() in {"TRUE", "1", "ANO", "YES"})
                elif isinstance(current, int):
                    setattr(cfg, field, int(parse_float(value, current)))
                elif isinstance(current, float):
                    setattr(cfg, field, parse_float(value, current))
                else:
                    setattr(cfg, field, value)
        if save:
            save_config(cfg)
        return cfg

    def pick_folder(self) -> None:
        folder = filedialog.askdirectory(title="Vyber MT5 Common\\Files složku")
        if folder:
            self.folder_var.set(folder)

    def save_settings(self) -> None:
        self._config_from_ui(save=True)
        self.update_expanded_path_label()
        messagebox.showinfo(APP_NAME, "Nastavení bylo uloženo.")
        self.log("Nastavení bylo uloženo")

    def refresh_all(self, show_message: bool = True) -> None:
        try:
            self.config_data = self._config_from_ui(save=True)
            self.update_expanded_path_label()
            if not self.config_data.expanded_mt5_folder.exists():
                self.log("Cesta neexistuje")
            self.prices = load_prices(self.config_data)
            self.positions = load_portfolio(self.config_data)
            self.current_positions = latest_snapshot_positions(self.positions)
            self.analyses = load_analyses(self.config_data)
            self.results = evaluate_analyses(self.config_data, self.analyses, self.prices)
            self.redraw_all()
            msg = f"MT5 data obnovena. Ceny: {len(self.prices)}, historie pozic: {len(self.positions)}, aktuální pozice: {len(self.current_positions)}, analýzy: {len(self.analyses)}"
            self.log(msg)
            if show_message:
                messagebox.showinfo(APP_NAME, msg)
        except PermissionError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            self.log(str(exc))
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Chyba: {exc}")
            self.log(f"Chyba: {exc}")

    def open_add_dialog(self) -> None:
        self._analysis_dialog(None)

    def open_edit_dialog(self) -> None:
        selected = self.analysis_tree.selection()
        if not selected:
            messagebox.showwarning(APP_NAME, "Vyber analýzu k úpravě.")
            return
        analysis_id = self.analysis_tree.item(selected[0], "values")[0]
        item = next((a for a in self.analyses if a.analysis_id == analysis_id), None)
        if item:
            self._analysis_dialog(item)

    def _analysis_dialog(self, item: Analysis | None) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Upravit analýzu" if item else "Přidat analýzu")
        fields = ["AnalysisID", "AnalysisDateTime", "Symbol", "Verdict", "HorizonDays", "StartPrice", "TargetPct", "StopPct", "Risk", "Reason", "Status", "Notes"]
        defaults = {
            "AnalysisID": item.analysis_id if item else "",
            "AnalysisDateTime": (item.analysis_datetime if item else datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": item.symbol if item else "",
            "Verdict": item.verdict if item else "BUY",
            "HorizonDays": str(item.horizon_days if item else self.config_data.default_horizon_days),
            "StartPrice": str(item.start_price or "") if item else "",
            "TargetPct": str(item.target_pct or "") if item else "",
            "StopPct": str(item.stop_pct or "") if item else "",
            "Risk": item.risk if item else "",
            "Reason": item.reason if item else "",
            "Status": item.status if item else "OPEN",
            "Notes": item.notes if item else "",
        }
        vars_: dict[str, tk.StringVar] = {}
        for row, field in enumerate(fields):
            ttk.Label(dialog, text=field).grid(row=row, column=0, sticky="w", padx=6, pady=2)
            var = tk.StringVar(value=defaults[field])
            vars_[field] = var
            if field == "Verdict":
                widget = ttk.Combobox(dialog, textvariable=var, values=VERDICTS, state="readonly")
            elif field == "Status":
                widget = ttk.Combobox(dialog, textvariable=var, values=("OPEN", "CLOSED", "CANCELLED"), state="readonly")
            else:
                widget = ttk.Entry(dialog, textvariable=var, width=48)
            widget.grid(row=row, column=1, sticky="ew", padx=6, pady=2)

        def save_item() -> None:
            dt = parse_datetime(vars_["AnalysisDateTime"].get()) or datetime.now().replace(microsecond=0)
            symbol = vars_["Symbol"].get().strip().upper()
            if not symbol:
                messagebox.showwarning(APP_NAME, "Zadej symbol.")
                return
            analysis_id = vars_["AnalysisID"].get().strip() or dt.strftime("%Y%m%d-%H%M%S-") + symbol
            new_item = Analysis(analysis_id, dt, symbol, vars_["Verdict"].get().upper(), int(parse_float(vars_["HorizonDays"].get(), self.config_data.default_horizon_days)), parse_float(vars_["StartPrice"].get()), parse_float(vars_["TargetPct"].get()), parse_float(vars_["StopPct"].get()), vars_["Risk"].get(), vars_["Reason"].get(), vars_["Status"].get().upper(), vars_["Notes"].get())
            if item:
                update_analysis(self.config_data, new_item)
                self.log("Analýza upravena")
                messagebox.showinfo(APP_NAME, "Analýza upravena")
            else:
                analyses = load_analyses(self.config_data)
                if any(a.analysis_id == new_item.analysis_id for a in analyses):
                    messagebox.showerror(APP_NAME, "AnalysisID musí být unikátní.")
                    return
                analyses.append(new_item)
                from analysis_engine import save_analyses
                save_analyses(self.config_data, analyses)
                self.log("Analýza uložena")
                messagebox.showinfo(APP_NAME, "Analýza uložena")
            dialog.destroy()
            self.refresh_all(show_message=False)

        ttk.Button(dialog, text="Uložit", command=save_item).grid(row=len(fields), column=1, sticky="e", padx=6, pady=8)

    def delete_selected_analysis(self) -> None:
        selected = self.analysis_tree.selection()
        if not selected:
            messagebox.showwarning(APP_NAME, "Vyber analýzu ke smazání.")
            return
        analysis_id = self.analysis_tree.item(selected[0], "values")[0]
        if messagebox.askyesno(APP_NAME, f"Smazat analýzu {analysis_id}?"):
            if delete_analysis(self.config_data, analysis_id):
                self.log("Analýza smazána")
                messagebox.showinfo(APP_NAME, "Analýza smazána")
                self.refresh_all(show_message=False)

    def write_tracked_symbols(self) -> None:
        try:
            count = export_tracked_symbols(self.config_data, load_analyses(self.config_data))
            msg = f"TrackedSymbols.csv zapsán. Počet symbolů: {count}"
            self.log(msg)
            messagebox.showinfo(APP_NAME, msg)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Chyba zápisu: {exc}")

    def export_excel(self) -> None:
        try:
            summary = build_summary(self.results, self.current_positions, self.positions)
            path = export_to_excel(self.config_data.expanded_mt5_folder, self.analyses, self.results, self.current_positions, self.positions, summary)
            messagebox.showinfo(APP_NAME, f"Export do Excelu vytvořen:\n{path}")
            self.log(f"Export do Excelu vytvořen: {path}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Export selhal: {exc}")
            self.log(f"Export selhal: {exc}")

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
            self.analysis_tree.insert("", "end", values=(a.analysis_id, a.analysis_datetime, a.symbol, a.verdict, a.horizon_days, a.start_price or "", a.target_pct or "", a.stop_pct or "", a.risk, a.status, a.reason))

    def _redraw_results_tree(self) -> None:
        self._clear_tree(self.results_tree)
        for r in self.results:
            self.results_tree.insert("", "end", values=(r.analysis.analysis_id, r.analysis.analysis_datetime, r.analysis.symbol, r.analysis.verdict, r.analysis.start_price, r.current_price or "", fmt_pct(r.current_return_pct), fmt_pct(r.return_1d), fmt_pct(r.return_5d), fmt_pct(r.return_14d), fmt_pct(r.horizon_return_pct), fmt_pct(r.max_runup_pct), fmt_pct(r.max_drawdown_pct), r.result))

    def _redraw_portfolio_tree(self) -> None:
        self._clear_tree(self.portfolio_tree)
        items = self.positions if self.portfolio_mode_var.get() == "celá historie" else self.current_positions
        for p in items:
            self.portfolio_tree.insert("", "end", values=(p.snapshot_time, p.symbol, p.ticket, p.type, p.volume, p.open_time or "", p.open_price, p.current_price, fmt_pct(p.percent_from_open), f"{p.profit:.2f}", p.swap, p.comment, f"{p.value_for_share:.2f}"))
        if self.current_positions:
            best_profit = max(self.current_positions, key=lambda p: p.profit)
            worst_profit = min(self.current_positions, key=lambda p: p.profit)
            total = sum(p.profit for p in self.current_positions)
            exposure = sum(p.value_for_share for p in self.current_positions)
            self.portfolio_summary_var.set(f"Total Profit: {total:.2f} | Number of open positions: {len(self.current_positions)} | Best Profit: {best_profit.symbol} {best_profit.profit:.2f} | Worst Profit: {worst_profit.symbol} {worst_profit.profit:.2f} | Total Exposure/Estimated: {exposure:.2f}")
        else:
            self.portfolio_summary_var.set("Žádné aktuální pozice.")

    def _redraw_dashboard(self) -> None:
        summary = build_summary(self.results, self.current_positions, self.positions)
        self.summary_text.delete("1.0", "end")
        best_a = summary.best_analysis
        worst_a = summary.worst_analysis
        lines = [
            f"Celkem analýz: {summary.total_analyses}",
            f"Skórovatelné analýzy: {summary.scorable_analyses}",
            f"BUY hit rate: {fmt_pct(summary.buy_hit_rate * 100) if summary.buy_hit_rate is not None else ''}",
            f"SHORT hit rate: {fmt_pct(summary.short_hit_rate * 100) if summary.short_hit_rate is not None else ''}",
            f"AVOID hit rate: {fmt_pct(summary.avoid_hit_rate * 100) if summary.avoid_hit_rate is not None else ''}",
            f"HIT/MISS/NEUTRAL/WATCH: {summary.result_counts.get('HIT',0)} / {summary.result_counts.get('MISS',0)} / {summary.result_counts.get('NEUTRAL',0)} / {summary.result_counts.get('WATCH ONLY',0)}",
            f"Nejlepší analýza: {best_a.analysis.symbol + ' ' + fmt_pct(best_a.horizon_return_pct) if best_a else ''}",
            f"Nejhorší analýza: {worst_a.analysis.symbol + ' ' + fmt_pct(worst_a.horizon_return_pct) if worst_a else ''}",
            f"Aktuální profit MT5: {summary.portfolio_profit:.2f}",
            f"Počet aktuálně otevřených pozic: {summary.open_positions}",
            f"Celková hodnota/expozice: {summary.total_value:.2f}",
            f"Největší pozice podle podílu: {summary.largest_position.symbol + ' ' + fmt_pct(summary.largest_position.share_pct) if summary.largest_position else ''}",
            f"Průměrný % výkon: {fmt_pct(summary.avg_percent)} | Medián: {fmt_pct(summary.median_percent)} | Plus: {summary.positive_count} | Mínus: {summary.negative_count}",
        ]
        if summary.uses_estimated_share:
            lines.append("Poznámka: Podíl je odhad podle Volume × CurrentPrice. Pro přesný výpočet je potřeba ExposureValue z MT5 EA.")
        if summary.uses_average_performance:
            lines.append("Poznámka: Výkon podle symbolu je počítán jako průměr otevřených ticketů. Pro přesnější výpočet doplň ExposureValue z MT5 EA.")
        self.summary_text.insert("end", "\n".join(lines))
        self._redraw_share_table(summary.symbol_rows)
        perf_rows = self._select_symbol_rows(summary.symbol_rows)
        self._redraw_symbol_perf_table(perf_rows)
        self._draw_pie_chart(self.share_canvas, {r.symbol: r.share_pct for r in summary.symbol_rows}, "Procentuální podíl v portfoliu")
        self._draw_horizontal_bar_chart(self.performance_canvas, {r.symbol: r.weighted_percent_from_open for r in perf_rows}, "Výkon akcií v % vůči sobě")
        self._draw_horizontal_bar_chart(self.analysis_canvas, self._analysis_chart_data(), "Výkon analyzovaných akcií v %")
        self._draw_line_chart(self.profit_canvas, summary.profit_history, "Vývoj profitu MT5 portfolia v čase")
        self._draw_multi_line_chart(self.symbol_history_canvas, summary.symbol_performance_history, summary.symbol_rows, "Porovnání zisku/ztráty akcií v portfoliu v čase")

    def _select_symbol_rows(self, rows):
        sorted_rows = sorted(rows, key=lambda r: r.weighted_percent_from_open, reverse=True)
        mode = self.performance_filter_var.get()
        if mode == "Všechny symboly":
            return sorted_rows
        if mode == "TOP 10 nejlepších":
            return sorted_rows[:10]
        if mode == "TOP 10 nejhorších":
            return list(reversed(sorted_rows[-10:]))
        return sorted_rows[:10] + list(reversed(sorted_rows[-10:]))

    def _analysis_chart_data(self) -> dict[str, float]:
        metric = self.analysis_metric_var.get()
        attr = {"aktuální výkon": "current_return_pct", "výkon po 1D": "return_1d", "výkon po 5D": "return_5d", "výkon po 14D": "return_14d", "výkon v horizontu analýzy": "horizon_return_pct"}[metric]
        pairs = [(f"{r.analysis.symbol} {r.analysis.verdict}", getattr(r, attr)) for r in self.results if getattr(r, attr) is not None]
        pairs.sort(key=lambda x: x[1], reverse=True)
        selected = pairs[:10] + list(reversed(pairs[-10:]))
        return dict(selected)

    def _redraw_share_table(self, rows) -> None:
        self._clear_tree(self.share_tree)
        for r in rows:
            self.share_tree.insert("", "end", values=(r.symbol, f"{r.value:.2f}", fmt_pct(r.share_pct), f"{r.profit:.2f}", fmt_pct(r.weighted_percent_from_open)))

    def _redraw_symbol_perf_table(self, rows) -> None:
        self._clear_tree(self.symbol_perf_tree)
        for r in rows:
            self.symbol_perf_tree.insert("", "end", values=(r.symbol, r.positions_count, fmt_pct(r.weighted_percent_from_open), f"{r.profit:.2f}", f"{r.value:.2f}", fmt_pct(r.best_ticket_pct), fmt_pct(r.worst_ticket_pct)))

    def _draw_pie_chart(self, canvas: tk.Canvas, data: dict[str, float], title: str) -> None:
        canvas.delete("all"); canvas.update_idletasks(); w=max(canvas.winfo_width(), 360); h=max(canvas.winfo_height(), 240)
        canvas.create_text(w/2, 16, text=title, font=("Segoe UI", 11, "bold"))
        data = {k: v for k, v in data.items() if v > 0}
        if not data:
            canvas.create_text(w/2, h/2, text="Žádná data"); return
        other = sum(v for v in data.values() if v < 1)
        data = {k: v for k, v in data.items() if v >= 1}
        if other: data["Ostatní"] = other
        colors = ["#2f80ed", "#27ae60", "#f2994a", "#eb5757", "#9b51e0", "#56ccf2", "#6fcf97"]
        start=0; total=sum(data.values()); x0=30; y0=45; size=min(w*0.45, h-70)
        for i,(label,value) in enumerate(data.items()):
            extent=value/total*360
            canvas.create_arc(x0,y0,x0+size,y0+size,start=start,extent=extent,fill=colors[i%len(colors)],outline="white")
            canvas.create_text(w*0.62,55+i*20,anchor="w",text=f"{label}: {value:.1f} %")
            start += extent

    def _draw_horizontal_bar_chart(self, canvas: tk.Canvas, data: dict[str, float], title: str) -> None:
        canvas.delete("all"); canvas.update_idletasks(); w=max(canvas.winfo_width(), 420); h=max(canvas.winfo_height(), 240)
        canvas.create_text(w/2, 16, text=title, font=("Segoe UI", 11, "bold"))
        if not data:
            canvas.create_text(w/2, h/2, text="Žádná data"); return
        items=list(data.items())[:20]; max_abs=max(abs(v) for _,v in items) or 1; zero=w/2; top=40; row_h=max(16,(h-55)/len(items))
        canvas.create_line(zero, top-5, zero, h-20, fill="#555")
        for i,(label,value) in enumerate(items):
            y=top+i*row_h; bar=(abs(value)/max_abs)*(w/2-90)
            x1=zero if value>=0 else zero-bar; x2=zero+bar if value>=0 else zero
            canvas.create_rectangle(x1,y,x2,y+row_h*0.65,fill="#27ae60" if value>=0 else "#eb5757")
            canvas.create_text(8,y+row_h*0.32,anchor="w",text=label[:16])
            canvas.create_text(x2+4 if value>=0 else x1-4,y+row_h*0.32,anchor="w" if value>=0 else "e",text=fmt_pct(value))

    def _draw_line_chart(self, canvas: tk.Canvas, data, title: str) -> None:
        canvas.delete("all"); canvas.update_idletasks(); w=max(canvas.winfo_width(), 420); h=max(canvas.winfo_height(), 240)
        canvas.create_text(w/2, 16, text=title, font=("Segoe UI", 11, "bold"))
        if len(data) < 2:
            canvas.create_text(w/2, h/2, text="Málo dat"); return
        vals=[v for _,v in data]; mn=min(vals); mx=max(vals); span=mx-mn or 1; pts=[]
        for i,(_,v) in enumerate(data):
            x=40+i*(w-70)/(len(data)-1); y=h-35-(v-mn)/span*(h-70); pts.extend([x,y])
        canvas.create_line(*pts, fill="#2f80ed", width=2)
        canvas.create_text(45,35,anchor="w",text=f"max {mx:.2f}"); canvas.create_text(45,h-25,anchor="w",text=f"min {mn:.2f}")

    def _draw_multi_line_chart(self, canvas: tk.Canvas, series: dict[str, list[tuple]], current_rows, title: str) -> None:
        canvas.delete("all"); canvas.update_idletasks(); w=max(canvas.winfo_width(), 700); h=max(canvas.winfo_height(), 280)
        canvas.create_text(w/2, 16, text=title, font=("Segoe UI", 11, "bold"))
        if not series:
            canvas.create_text(w/2, h/2, text="Žádná historie procentuálního výkonu")
            return
        preferred = [r.symbol for r in sorted(current_rows, key=lambda r: r.share_pct, reverse=True)[:8]]
        symbols = preferred or sorted(series.keys())[:8]
        points = [(t, v) for sym in symbols for t, v in series.get(sym, [])]
        if len(points) < 2:
            canvas.create_text(w/2, h/2, text="Málo bodů pro časový graf")
            return
        times = sorted({t for t, _ in points})
        values = [v for _, v in points]
        min_v = min(values + [0]); max_v = max(values + [0]); span = max_v - min_v or 1
        left=65; right=w-150; top=42; bottom=h-45
        zero_y = bottom - (0 - min_v) / span * (bottom - top)
        canvas.create_line(left, zero_y, right, zero_y, fill="#777", dash=(3, 3))
        canvas.create_line(left, top, left, bottom, fill="#999")
        canvas.create_line(left, bottom, right, bottom, fill="#999")
        colors=["#2f80ed", "#eb5757", "#27ae60", "#f2994a", "#9b51e0", "#56ccf2", "#6fcf97", "#bb6bd9"]
        time_index={t:i for i,t in enumerate(times)}
        for idx, sym in enumerate(symbols):
            pts=[]
            for t, v in series.get(sym, []):
                x = left + time_index[t] * (right-left) / max(1, len(times)-1)
                y = bottom - (v - min_v) / span * (bottom-top)
                pts.extend([x,y])
            if len(pts) >= 4:
                canvas.create_line(*pts, fill=colors[idx % len(colors)], width=2)
                for x,y in zip(pts[0::2], pts[1::2]):
                    canvas.create_oval(x-3, y-3, x+3, y+3, fill=colors[idx % len(colors)], outline="white")
            canvas.create_text(right+12, top+idx*18, anchor="w", text=sym, fill=colors[idx % len(colors)])
        canvas.create_text(left, top-12, anchor="w", text=f"max {max_v:+.1f} %")
        canvas.create_text(left, bottom+16, anchor="w", text=f"min {min_v:+.1f} %")
        if times:
            canvas.create_text(left, h-18, anchor="w", text=times[0].strftime("%d.%m %H:%M"))
            canvas.create_text(right, h-18, anchor="e", text=times[-1].strftime("%d.%m %H:%M"))


def main() -> None:
    app = MT5AnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
