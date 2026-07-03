# IMPROVEMENT_REPORT.md

Datum poslední aktualizace: 2026-07-03

## Co aplikace už umí
- Načítá MT5 CSV soubory `MT5_Portfolio_Positions.csv` a `MT5_Analysis_Prices.csv`.
- Pro aktuální portfolio používá poslední `SnapshotTime`.
- Agreguje portfolio podle symbolu a počítá podíl v portfoliu přes `ExposureValue`, `MarketValue` nebo fallback `EstimatedValue`.
- Zobrazuje dashboard s koláčem portfolia, výkonem akcií v %, časovým porovnáním výkonu a vývojem profitu portfolia.
- Umožňuje ručně přidávat/upravovat/mazat analýzy v `Analyses.csv`.
- Vyhodnocuje BUY / SHORT / AVOID / WATCH analýzy v horizontech 1D, 5D, 14D a vlastním horizontu.
- Generuje `TrackedSymbols.csv` z OPEN analýz.
- Exportuje data do Excelu.
- Má základní testy pro import, latest snapshot, BUY scoring, ukládání analýz, tracked symbols, parsing a Excel export.

## Slabiny, které byly nalezeny
- Dashboard zatím neukazuje koncentraci portfolia jako jednoznačnou rizikovou metriku.
- Portfolio ukazuje procentuální výkon, ale chybí přehled absolutních tahounů a brzd podle Profit.
- Je k dispozici vývoj profitu, ale chybí drawdown od průběžného maxima.
- Chybí pohled na vztah velikosti pozice a výkonu.
- Výsledky analýz mají 1D/5D/14D/horizon hodnoty, ale chybí agregované porovnání těchto horizontů podle Verdict.
- WATCH analýzy nejsou skórované, ale chybí metrika promarněných WATCH příležitostí.
- AVOID scoring existuje, ale chybí samostatný pohled na false AVOID případy.
- Chybí benchmark proti širšímu trhu, pokud budou dostupná benchmarková data.
- QA report už doporučil rozšířit testy pro SHORT / AVOID / WATCH a chybějící/prázdné CSV.

## Nové návrhy
Do `backlog/IDEAS_BACKLOG.md` bylo zapsáno 10 návrhů:

1. `IMP-20260703-001` Koncentrace portfolia a Herfindahl index
2. `IMP-20260703-002` Tahouni a brzdy portfolia podle Profit
3. `IMP-20260703-003` Drawdown portfolia v čase
4. `IMP-20260703-004` Velikost pozice vs výkon
5. `IMP-20260703-005` Porovnání analýz 1D / 5D / 14D / Horizon vedle sebe
6. `IMP-20260703-006` Missed WATCH opportunities
7. `IMP-20260703-007` False AVOID metrika
8. `IMP-20260703-008` Benchmark analýz proti SPY/QQQ/US500/NAS100
9. `IMP-20260703-009` Doba držení aktuálních pozic
10. `IMP-20260703-010` Export QA snapshotu dashboardu do Excelu

## TOP 3 doporučené návrhy
1. `IMP-20260703-001` Koncentrace portfolia a Herfindahl index
2. `IMP-20260703-002` Tahouni a brzdy portfolia podle Profit
3. `IMP-20260703-003` Drawdown portfolia v čase

## Proč zrovna tyto
- Mají vysoký dopad na přehled rizika a zdraví portfolia.
- Používají už dostupná data z `MT5_Portfolio_Positions.csv`.
- Nevyžadují externí API ani obchodní příkazy do MT5.
- Jsou přímo navázané na prioritu projektu: správnost výpočtů, stabilita a čitelnost dashboardu.

## Co má uživatel schválit
Pokud chceš pokračovat implementací, napiš například:

- `schvaluji návrhy IMP-20260703-001, IMP-20260703-002, IMP-20260703-003`
- nebo `implementuj top návrhy`

Teprve potom je má BUILD AGENT implementovat.

## Další možné směry
- Po implementaci TOP 3 doplnit testy pro nové metriky.
- Přidat benchmark pouze v případě, že EA bude spolehlivě sledovat benchmark symboly.
- Rozšířit Excel export o stejné metriky jako dashboard.
- Přidat konfigurovatelné prahy rizika pro koncentraci a drawdown.
