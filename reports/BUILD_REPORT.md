# BUILD_REPORT.md

Datum poslední aktualizace: 2026-07-03

## Stav
Agentní systém byl přidán jako dokumentační a řídicí vrstva pro Codex. Nebyly provedeny změny funkční logiky aplikace.

## Zjištěná struktura projektu
- Hlavní vstup aplikace: `main.py`
- Windows launcher: `Spustit_MT5_Analyzer.bat`
- Načítání MT5 CSV: `mt5_data.py`
- Výpočty portfolia: `mt5_data.py`, souhrny v `dashboard.py`
- Kreslení dashboardu: `main.py`
- Analýzy a scoring: `analysis_engine.py`
- Excel export: `excel_export.py`
- Testy: `tests/test_core.py`

## Provedené změny
- Vytvořen hlavní rozcestník `AGENTS.md`.
- Vytvořeny instrukce pro BUILD, QA a IMPROVEMENT agenta ve složce `agents/`.
- Vytvořeny reportovací soubory ve složce `reports/`.
- Vytvořen backlog ve složce `backlog/`.

## Testy
- Agentní změna je dokumentační; pro lehkou kontrolu projektu byly spuštěny existující testy.

## Ruční kontrola pro uživatele
- Ověřit, že příkazy pro agenty v `AGENTS.md` odpovídají očekávanému způsobu práce v Codexu.
- Při dalším použití napsat jeden z příkazů: `spusť agenta build`, `spusť QA agenta`, `spusť agenta vylepšení`.
