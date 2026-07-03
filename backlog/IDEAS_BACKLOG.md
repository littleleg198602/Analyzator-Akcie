# IDEAS_BACKLOG.md

Backlog návrhů pro MT5 analyzátor akcií.

Stavy:
- Navrženo
- Schváleno
- Implementováno
- Zamítnuto
- Vyhodnoceno

Pravidla:
- BUILD AGENT smí implementovat pouze položky se stavem `Schváleno` nebo konkrétní úkol výslovně zadaný uživatelem.
- IMPROVEMENT AGENT sem zapisuje nové návrhy se stavem `Navrženo`.
- QA AGENT sem zapisuje nalezené chyby nebo doporučení, pokud je sám neopravuje.
- Žádný návrh nesmí zavádět automatické obchodování ani posílání příkazů do MT5.

## Položky

_Zatím žádné položky. Spusť `spusť agenta vylepšení`, aby IMPROVEMENT AGENT doplnil návrhy._

---
ID: QA-20260703-001
Název: Rozšířit testy scoringu pro SHORT / AVOID / WATCH
Kategorie: QA / Calculation
Priorita: P2
Dopad: Střední
Složitost: Nízká
Popis: Současné testy pokrývají základní BUY scénář, ale QA checklist vyžaduje samostatné ověření SHORT HIT/MISS, AVOID HIT/MISS a WATCH ONLY.
Proč to přidat: Zvýší jistotu, že scoring pravidla fungují pro všechny typy analýz.
Výpočet: Vytvořit vzorky cen a analýz, kde SHORT dosáhne HIT/MISS, AVOID dosáhne HIT/MISS a WATCH vrátí WATCH ONLY.
Zdroj dat: Testovací CSV data v dočasné složce.
Kde v UI: Bez UI; testovací vrstva `tests/`.
Acceptance test: `pytest` obsahuje explicitní asserty pro SHORT HIT/MISS, AVOID HIT/MISS a WATCH ONLY.
Stav: Navrženo

---
ID: QA-20260703-002
Název: Otestovat chybějící a prázdné MT5 CSV soubory
Kategorie: QA / Bug
Priorita: P2
Dopad: Střední
Složitost: Nízká
Popis: Doplnit testy, že aplikace nespadne při chybějícím `MT5_Analysis_Prices.csv`, chybějícím `MT5_Portfolio_Positions.csv`, prázdném CSV nebo CSV pouze s hlavičkou.
Proč to přidat: QA checklist vyžaduje stabilitu při chybějících CSV a prázdných datech.
Výpočet: Loader má vracet prázdné seznamy a dashboard má zobrazit nulové souhrny bez výjimky.
Zdroj dat: Dočasné testovací složky bez CSV nebo s prázdnými CSV.
Kde v UI: Refresh / import dat.
Acceptance test: `pytest` ověří, že loadery a summary builder nespadnou na chybějících a prázdných souborech.
Stav: Navrženo
