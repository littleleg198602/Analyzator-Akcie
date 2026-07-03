# AGENTS.md

Projekt: MT5 analyzátor akcií

Tento repozitář používá tři Codex agenty:

1) BUILD AGENT
2) QA AGENT
3) IMPROVEMENT AGENT

Při každém spuštění nejdříve přečti:
- tento AGENTS.md
- agents/COMMON_RULES.md
- příslušný agentní soubor podle příkazu uživatele

Mapování příkazů:

"spusť agenta build"
=> agents/BUILD_AGENT.md

"spusť agenta kvalita"
"spusť QA agenta"
=> agents/QA_AGENT.md

"spusť agenta vylepšení"
"spusť vylepšovacího agenta"
=> agents/IMPROVEMENT_AGENT.md

Nevymýšlej vlastní proces, pokud je proces definovaný v agentním souboru.

Vždy zapisuj výsledek práce do odpovídajícího reportu ve složce reports/.

Nikdy:
- neobchoduj
- neposílej příkazy do MT5
- nemaž MT5 CSV historii
- nepřepisuj reálná MT5 data
- nedělej nákupní/prodejní doporučení jako funkce aplikace

Priorita projektu:
1) správnost výpočtů
2) stabilita aplikace
3) čitelnost dashboardu
4) vyhodnocení analýz
5) export a testy
