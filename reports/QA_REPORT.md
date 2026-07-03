# QA_REPORT.md

Datum poslední aktualizace: 2026-07-03

## Stav aplikace
QA agent byl spuštěn příkazem `spusť agenta kvalita`.

Aplikace je Python/Tkinter projekt pro MT5 analyzátor akcií. Kontrola proběhla bez změny aplikační logiky.

Zjištěná struktura:
- Hlavní vstup aplikace: `main.py`
- Načítání MT5 CSV: `mt5_data.py`
- Aktuální portfolio / agregace: `mt5_data.py`
- Souhrny dashboardu: `dashboard.py`
- Kreslení dashboardu: `main.py`
- Analýzy a scoring: `analysis_engine.py`
- Export do Excelu: `excel_export.py`
- Testy: `tests/test_core.py`

## Co prošlo
- Import hlavních modulů prošel (`main`, `mt5_data`, `analysis_engine`, `dashboard`, `excel_export`).
- `pytest` prošel: 3 testy prošly.
- `py_compile` prošel pro hlavní Python soubory.
- Testy ověřují import cen a portfolia z MT5 CSV.
- Testy ověřují, že aktuální portfolio bere pouze poslední `SnapshotTime`.
- Testy ověřují total profit z aktuálního snapshotu.
- Testy ověřují počet aktuálních pozic z aktuálního snapshotu.
- Testy ověřují podíl portfolia podle agregace symbolů.
- Testy ověřují časovou řadu výkonu symbolů.
- Testy ověřují BUY scoring na vzorku.
- Testy ověřují uložení a načtení `Analyses.csv`.
- Testy ověřují `TrackedSymbols.csv` pouze z OPEN analýz bez duplicit.
- Testy ověřují parsing desetinné čárky/tečky a datum `7/2/2026 1:02 PM`.
- Testy ověřují vytvoření Excel exportu `.xlsx`.
- Bezpečnostní rychlá kontrola nenašla volání MT5 obchodních funkcí typu `OrderSend`, `CTrade`, `MetaTrader5` nebo `mt5.order`.

## Co neprošlo
- Nebyla provedena plná ruční GUI kontrola ve Windows, protože aktuální prostředí je headless/linuxové.
- Nebyl ručně ověřen skutečný zápis do uživatelské složky `%APPDATA%\MetaQuotes\Terminal\Common\Files\` ve Windows.

## Kritické chyby
- Žádné kritické chyby nebyly automatizovanou kontrolou nalezeny.

## Střední chyby
- Žádné střední chyby nebyly automatizovanou kontrolou nalezeny.

## Drobné chyby
- Ruční Windows smoke test zůstává doporučený, protože Tkinter GUI nelze plnohodnotně otevřít v tomto headless prostředí.

## Doporučené opravy
- Při dalším QA běhu ve Windows ručně ověřit otevření GUI přes `Spustit_MT5_Analyzer.bat`.
- Doplnit samostatné testy pro SHORT HIT/MISS, AVOID HIT/MISS a WATCH ONLY, aby byl QA checklist pokryt ještě detailněji než současným základním testem.
- Doplnit test chybějících CSV souborů, pokud bude BUILD agent příště upravovat loader nebo chybové hlášky.

## Ruční kontroly pro uživatele
- Spustit aplikaci ve Windows přes `Spustit_MT5_Analyzer.bat`.
- Ověřit, že se zobrazí české UI a skutečná rozbalená MT5 cesta.
- Ověřit refresh proti reálným MT5 CSV souborům.
- Ověřit, že dashboard po refreshi používá pouze nejnovější `SnapshotTime`.
- Ověřit, že `TrackedSymbols.csv` se zapisuje do správné MT5 Common Files složky.
- Ověřit Excel export tlačítkem `Export do Excelu` v reálném Windows prostředí.

## Spuštěné příkazy
- `python3 -m pip install --user -r requirements.txt`
- `python3 -m pytest -q`
- `python3 -m py_compile config.py utils.py mt5_data.py analysis_engine.py dashboard.py excel_export.py main.py tools/create_excel_template.py`
- `python3 - <<'PY' ... import main, mt5_data, analysis_engine, dashboard, excel_export ... PY`
- `rg -n "OrderSend|trade|buy\(|sell\(|MetaTrader5|mt5\.order|PositionClose|CTrade" . || true`
