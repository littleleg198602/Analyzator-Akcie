# COMMON_RULES.md

Platí pro všechny agenty.

Projekt:
MT5 analyzátor akcií

Aplikace už existuje a je funkční.
Agenti ji mají rozšiřovat, kontrolovat a vylepšovat, ne přepisovat od nuly.

Aktuální orientace v projektu:
- hlavní vstup aplikace: `main.py`
- spouštěcí BAT pro Windows: `Spustit_MT5_Analyzer.bat`
- načítání MT5 CSV: `mt5_data.py`
- analýzy a scoring: `analysis_engine.py`
- souhrny dashboardu: `dashboard.py`
- kreslení dashboardu: `main.py`
- export do Excelu: `excel_export.py`
- testy: `tests/test_core.py`

Hlavní datové soubory:
- MT5_Portfolio_Positions.csv
- MT5_Analysis_Prices.csv
- TrackedSymbols.csv
- Analyses.csv

Nejdůležitější pravidlo:
MT5_Portfolio_Positions.csv obsahuje historii snapshotů.

Pro aktuální portfolio vždy používej pouze nejnovější SnapshotTime.

Toto pravidlo platí pro:
- počet aktuálních pozic
- total profit
- nejlepší pozici
- nejhorší pozici
- koláč portfolia
- výkon akcií v %
- koncentraci portfolia
- aktuální dashboard metriky

Zakázáno:
- automatické obchodování
- příkazy do MT5
- mazání MT5 CSV historie
- změna reálných MT5 CSV dat
- obchodní doporučení typu koupit/prodat jako funkce aplikace

Povoleno:
- číst CSV
- počítat metriky
- vytvářet grafy
- vyhodnocovat analýzy
- exportovat do Excelu
- psát testy
- psát reporty
- zapisovat návrhy do backlogu

Před změnou kódu:
1) zjisti aktuální stav
2) napiš krátký plán
3) implementuj jen změny z plánu

Po změně:
1) spusť dostupné testy
2) pokud testy chybí, vytvoř základní test
3) aktualizuj report
4) aktualizuj CHANGELOG.md, pokud existuje
