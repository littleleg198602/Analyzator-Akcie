# MT5 analyzátor akcií – desktop program

Toto je jednoduchý Windows/Python program ve stylu `rulechecker-cz`: spouští se přes `Spustit_MT5_Analyzer.bat`, má grafické okno a čte CSV soubory, které zapisuje MT5 Expert Advisor do složky `Common\Files`.

## Spuštění

1. Nainstaluj Python 3 pro Windows.
2. Dvojklikem spusť `Spustit_MT5_Analyzer.bat`.
3. V horním poli zkontroluj cestu k MT5 Common Files, typicky `%APPDATA%\MetaQuotes\Terminal\Common\Files\`.
4. Klikni na `Obnovit MT5 data`.
5. Analýzy zadávej v záložce `Analýzy`.
6. Tlačítko `Zapsat TrackedSymbols.csv` vytvoří soubor pro MT5 EA.

## Co program umí

- Načítá `MT5_Analysis_Prices.csv` a počítá `PriceUsed` podle pravidla Last → midpoint Bid/Ask → Bid.
- Načítá historii `MT5_Portfolio_Positions.csv` a zobrazuje poslední snapshot pro každý ticket.
- Ukládá ruční analýzy do `data/analyzy.csv`.
- Vyhodnocuje BUY, SHORT, AVOID a WATCH v horizontu 1D, 5D, 14D a vlastním horizontu.
- Zobrazuje dashboard v češtině včetně základních grafů.
- Umí zapsat unikátní OPEN symboly do `TrackedSymbols.csv`.

## Excel šablona

Binární `.xlsx` soubor záměrně není uložený v gitu, protože náhled diffu ho neumí zobrazit. Pokud chceš Excel variantu, vygeneruj ji lokálně příkazem `python tools/create_excel_template.py`. Výstup se uloží do `dist/MT5_Analysis_Portfolio_Dashboard.xlsx`. Potom ho v Excelu ulož jako `.xlsm` a importuj VBA moduly ze složky `vba/`.

## Poznámka k CSV

CSV soubory nenechávej otevřené v Excelu. MT5 by do zamčeného souboru nemusel umět zapisovat.


## Nové důležité chování

- Aplikace zobrazuje zadanou MT5 cestu i skutečnou rozbalenou cestu po `os.path.expandvars()`.
- `Analyses.csv` se ukládá do MT5 Common Files složky, aby byla data pohromadě s MT5 CSV.
- Aktuální portfolio, dashboard a grafy používají pouze řádky z nejnovějšího `SnapshotTime`, ne celou historii.
- Pokud MT5 EA neposílá `ExposureValue` nebo `MarketValue`, aplikace použije odhad `ABS(Volume * CurrentPrice)` a zobrazí českou poznámku.
- Export do Excelu vytvoří `.xlsx` přímo z aplikace tlačítkem `Export do Excelu`.
