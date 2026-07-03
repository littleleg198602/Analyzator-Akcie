# QA_REPORT.md

Datum poslední aktualizace: 2026-07-03

## Stav aplikace
Aplikace existuje jako Python/Tkinter projekt. Agentní systém byl přidán bez změny aplikační logiky.

## Co prošlo
- Projektová struktura byla zjištěna.
- Hlavní vstup aplikace je `main.py`.
- MT5 CSV se načítají v `mt5_data.py`.
- Portfolio a agregace se počítají v `mt5_data.py` a `dashboard.py`.
- Dashboard se kreslí v `main.py`.
- Testy existují v `tests/test_core.py`.

## Co neprošlo
- Žádná aplikační chyba nebyla v rámci přidání agentního systému zjištěna.

## Kritické chyby
- Žádné.

## Střední chyby
- Žádné.

## Drobné chyby
- Žádné.

## Doporučené opravy
- Při dalším běhu QA agenta projít povinný QA checklist z `agents/QA_AGENT.md`.

## Ruční kontroly pro uživatele
- Spustit aplikaci ve Windows přes `Spustit_MT5_Analyzer.bat`.
- Ověřit, že MT5 Common Files cesta odpovídá lokálnímu profilu Windows.
