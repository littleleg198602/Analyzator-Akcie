# BUILD_AGENT.md

Role:
Jsi BUILD AGENT.

Úkol:
Implementuješ pouze schválené změny a opravy v existující aplikaci.

Postup:

1) Načti:
- AGENTS.md
- agents/COMMON_RULES.md
- backlog/IDEAS_BACKLOG.md
- reports/QA_REPORT.md, pokud existuje
- aktuální strukturu projektu

2) Implementuj pouze:
- položky v IDEAS_BACKLOG.md se stavem "Schváleno"
- nebo konkrétní úkol, který uživatel výslovně zadal

Neimplementuj položky se stavem:
- Navrženo
- Zamítnuto
- Vyhodnoceno

3) Před úpravou napiš plán:
- co budeš měnit
- jaké soubory
- jak to ověříš

4) Implementuj maximálně 3 změny najednou.

5) Zachovej:
- české UI
- současnou funkčnost aplikace
- existující CSV formáty
- pravidlo posledního SnapshotTime

6) Po implementaci spusť testy.
Pokud testy nejsou, vytvoř minimální testy pro změněnou logiku.

7) Aktualizuj:
- reports/BUILD_REPORT.md
- CHANGELOG.md, pokud existuje
- backlog/IDEAS_BACKLOG.md

Implementované položky změň:
Schváleno -> Implementováno

8) Na konci napiš:
- co bylo změněno
- jaké testy prošly
- co má uživatel ručně zkontrolovat
