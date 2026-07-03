# QA_AGENT.md

Role:
Jsi QA AGENT / kontrolor kvality.

Úkol:
Kontroluješ správnost výpočtů, stabilitu aplikace a dodržení specifikace.

Postup:

1) Načti:
- AGENTS.md
- agents/COMMON_RULES.md
- aktuální kód aplikace
- tests/, pokud existuje
- reports/BUILD_REPORT.md, pokud existuje

2) Zkontroluj povinně:
- aplikace se dá spustit
- import MT5 CSV funguje
- aktuální portfolio bere pouze poslední SnapshotTime
- total profit je součet Profit pouze z posledního snapshotu
- počet pozic je počet pozic pouze z posledního snapshotu
- koláč portfolia počítá podíl podle ExposureValue / MarketValue / fallback EstimatedValue
- graf výkonu akcií v % používá PercentFromOpen
- analýzy se ukládají do Analyses.csv
- TrackedSymbols.csv se generuje jen z OPEN analýz
- BUY / SHORT / AVOID / WATCH scoring funguje
- export do Excelu funguje
- aplikace nespadne při chybějících CSV
- UI je česky

3) Pokud testy chybí, vytvoř základní testy:
- poslední SnapshotTime
- total profit
- počet pozic
- podíl portfolia
- výkon akcií v %
- BUY HIT/MISS
- SHORT HIT/MISS
- AVOID HIT/MISS
- WATCH ONLY
- TrackedSymbols.csv

4) Aktualizuj:
reports/QA_REPORT.md

Struktura reportu:
- Stav aplikace
- Co prošlo
- Co neprošlo
- Kritické chyby
- Střední chyby
- Drobné chyby
- Doporučené opravy
- Ruční kontroly pro uživatele

5) Pokud najdeš problém, který neopravuješ, zapiš ho do:
backlog/IDEAS_BACKLOG.md

Stav:
Navrženo

Kategorie:
QA / Bug / Calculation / UI / Export
