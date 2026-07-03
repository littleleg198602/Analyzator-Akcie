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
Stav:  Schváleno
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
Stav:  Schváleno

---
ID: IMP-20260703-001
Název: Koncentrace portfolia a Herfindahl index
Kategorie: Portfolio / Risk
Priorita: P1
Dopad: Vysoký
Složitost: Nízká
Popis: Přidat metriku koncentrace portfolia podle podílu symbolů a varování, pokud několik největších pozic tvoří příliš velkou část portfolia.
Proč to přidat: Uživatel rychle uvidí, zda portfolio není přetížené několika akciemi.
Výpočet: Top 1 / Top 3 / Top 5 share a HHI = SUM((PortfolioSharePct/100)^2). Používat pouze poslední SnapshotTime a hodnotu ExposureValue / MarketValue / EstimatedValue.
Zdroj dat: `MT5_Portfolio_Positions.csv`, aktuální snapshot.
Kde v UI: Dashboard summary + tabulka `Podíl v portfoliu`.
Acceptance test: Testovací portfolio se známými váhami vrátí očekávané Top 3 share a HHI.
Stav:  Schváleno

---
ID: IMP-20260703-002
Název: Tahouni a brzdy portfolia podle Profit
Kategorie: Portfolio / Dashboard
Priorita: P1
Dopad: Vysoký
Složitost: Nízká
Popis: Přidat žebříček, které symboly nejvíce přidávají a ubírají absolutní profit v aktuálním portfoliu.
Proč to přidat: Procentuální výkon nestačí; malá pozice může mít velké %, ale malý dopad na účet.
Výpočet: Agregovat Profit podle Symbol z posledního SnapshotTime, seřadit TOP 10 a WORST 10.
Zdroj dat: `MT5_Portfolio_Positions.csv`, aktuální snapshot.
Kde v UI: Dashboard pod grafem výkonu akcií nebo nová tabulka `Tahouni / brzdy`.
Acceptance test: Více ticketů stejného symbolu sečte Profit a správně seřadí symboly.
Stav: Navrženo

---
ID: IMP-20260703-003
Název: Drawdown portfolia v čase
Kategorie: Portfolio / Risk
Priorita: P1
Dopad: Vysoký
Složitost: Střední
Popis: Přidat graf drawdownu celkového profitu portfolia v čase podle historických snapshotů.
Proč to přidat: Uživatel uvidí, jak hluboké byly propady od lokálního maxima profitu.
Výpočet: Pro každý SnapshotTime spočítat TotalProfit, průběžné maximum a Drawdown = TotalProfit - RunningMax; volitelně i DrawdownPct proti hodnotě portfolia.
Zdroj dat: `MT5_Portfolio_Positions.csv`, historie snapshotů.
Kde v UI: Dashboard vedle grafu `Vývoj profitu MT5 portfolia v čase`.
Acceptance test: Historie profitů `[100, 150, 120, 180]` vrátí drawdown `[0, 0, -30, 0]`.
Stav: Zamítnuto

---
ID: IMP-20260703-004
Název: Velikost pozice vs výkon
Kategorie: Portfolio / Visualization
Priorita: P2
Dopad: Střední
Složitost: Střední
Popis: Přidat scatter/bubble pohled, kde osa X je hodnota pozice, osa Y je PercentFromOpen a velikost/barva bodu ukazuje Profit.
Proč to přidat: Pomůže odhalit velké ztrátové pozice i malé extrémně volatilní pozice.
Výpočet: Pro každý symbol z aktuálního snapshotu použít agregovanou hodnotu pozice a weighted PercentFromOpen.
Zdroj dat: `MT5_Portfolio_Positions.csv`, aktuální snapshot.
Kde v UI: Dashboard nebo nová sekce `Riziko pozic`.
Acceptance test: Agregace více ticketů stejného symbolu vytvoří jeden bod s očekávanou hodnotou a weighted %.
Stav: Schváleno

---
ID: IMP-20260703-005
Název: Porovnání analýz 1D / 5D / 14D / Horizon vedle sebe
Kategorie: Analysis / Dashboard
Priorita: P2
Dopad: Střední
Složitost: Nízká
Popis: Přidat tabulku nebo graf, který vedle sebe ukáže průměrný výkon analýz po 1D, 5D, 14D a v horizontu podle Verdict.
Proč to přidat: Uživatel uvidí, jestli jsou analýzy lepší krátkodobě nebo až v delším horizontu.
Výpočet: Agregovat Return1D, Return5D, Return14D, HorizonReturnPct podle Verdict a Result.
Zdroj dat: vypočtené `AnalysisResult` z `analysis_engine.py`.
Kde v UI: Záložka `Výsledky analýz` nebo Dashboard summary.
Acceptance test: Vzorek analýz s pevnými returny vrátí očekávané průměry podle Verdict.
Stav: Schváleno

---
ID: IMP-20260703-006
Název: Missed WATCH opportunities
Kategorie: Analysis / Metrics
Priorita: P2
Dopad: Střední
Složitost: Nízká
Popis: Sledovat WATCH analýzy, které sice nejsou skórované jako HIT/MISS, ale následně výrazně vyrostly.
Proč to přidat: Pomůže zjistit, zda WATCH často znamená promarněnou příležitost.
Výpočet: Pro WATCH vypočítat HorizonReturnPct raw return; pokud je >= konfigurovatelný práh, označit `WATCH OPPORTUNITY`.
Zdroj dat: `Analyses.csv` + `MT5_Analysis_Prices.csv`.
Kde v UI: `Výsledky analýz`, filtr WATCH a dashboard počet missed opportunities.
Acceptance test: WATCH analýza s růstem nad práh je označena jako WATCH OPPORTUNITY, ale neovlivní HIT rate.
Stav: Navrženo

---
ID: IMP-20260703-007
Název: False AVOID metrika
Kategorie: Analysis / Metrics
Priorita: P2
Dopad: Střední
Složitost: Nízká
Popis: Zvýraznit AVOID analýzy, po kterých akcie výrazně vyrostla, a sledovat jejich počet a průměrný růst.
Proč to přidat: AVOID scoring už existuje, ale samostatný pohled na false AVOID pomůže zlepšit kvalitu rozhodování.
Výpočet: AVOID s raw HorizonReturnPct >= AvoidBadPct evidovat jako FalseAvoid; agregovat count, avg return, top false avoids.
Zdroj dat: `AnalysisResult`.
Kde v UI: Dashboard + tabulka `Výsledky analýz`.
Acceptance test: AVOID s raw returnem nad prahem se započítá do FalseAvoid metriky.
Stav: Navrženo

---
ID: IMP-20260703-008
Název: Benchmark analýz proti SPY/QQQ/US500/NAS100
Kategorie: Analysis / Benchmark
Priorita: P3
Dopad: Střední
Složitost: Vysoká
Popis: Porovnat výnos analyzované akcie s benchmarkem ve stejném období.
Proč to přidat: Absolutní výnos neříká, zda analýza překonala trh.
Výpočet: Alpha = StockReturnPct - BenchmarkReturnPct pro stejný AnalysisDateTime a HorizonDays.
Zdroj dat: `MT5_Analysis_Prices.csv`, pokud EA sleduje benchmark symboly; jinak doplnit benchmark do TrackedSymbols.
Kde v UI: `Výsledky analýz` a dashboard hit rate podle alpha.
Acceptance test: Vzorek akcie + benchmarku se známými cenami vrátí správnou alpha hodnotu.
Stav: Schváleno

---
ID: IMP-20260703-009
Název: Doba držení aktuálních pozic
Kategorie: Portfolio / Risk
Priorita: P3
Dopad: Nízký
Složitost: Nízká
Popis: Přidat přehled stáří otevřených pozic podle OpenTime.
Proč to přidat: Uživatel uvidí, které pozice jsou dlouhodobě otevřené a mohou vyžadovat kontrolu.
Výpočet: HoldingDays = LatestSnapshotTime - OpenTime; agregovat max, průměr a top nejstarší pozice.
Zdroj dat: `MT5_Portfolio_Positions.csv`, aktuální snapshot.
Kde v UI: Záložka `MT5 portfolio` a Dashboard summary.
Acceptance test: Pozice s OpenTime před 10 dny vrátí HoldingDays přibližně 10.
Stav: Zamítnuto

---
ID: IMP-20260703-010
Název: Export QA snapshotu dashboardu do Excelu
Kategorie: Export / QA
Priorita: P3
Dopad: Nízký
Složitost: Střední
Popis: Rozšířit Excel export o list s kontrolními součty a datem posledního snapshotu.
Proč to přidat: Uživatel snadno ověří, že export odpovídá aktuálnímu dashboardu.
Výpočet: Exportovat LatestSnapshotTime, TotalProfit, OpenPositions, TotalExposure, Top symbol, Worst symbol a počty analýz.
Zdroj dat: `DashboardSummary`, aktuální snapshot.
Kde v UI: Tlačítko `Export do Excelu`.
Acceptance test: Exportovaný list obsahuje stejné hodnoty jako `build_summary`.
Stav: Schváleno
