# MT5 Analysis Portfolio Dashboard

Tento balíček obsahuje šablonu Excelu `MT5_Analysis_Portfolio_Dashboard.xlsx` a VBA moduly pro vytvoření makro sešitu `.xlsm`, který načítá CSV soubory z MetaTrader 5 common files složky, vyhodnocuje přesnost akciových analýz a sleduje reálné otevřené MT5 pozice.

## Instalace

1. Otevřete `MT5_Analysis_Portfolio_Dashboard.xlsx` v Microsoft Excelu pro Windows.
2. Uložte soubor jako `MT5_Analysis_Portfolio_Dashboard.xlsm`.
3. Otevřete VBA editor pomocí `Alt+F11`.
4. Importujte moduly ze složky `vba/`:
   - `modMT5Import.bas`
   - `modTrackedSymbols.bas`
   - `modAnalysisScoring.bas`
   - `modPortfolioDashboard.bas`
5. Obsah souboru `vba/ThisWorkbook.cls` vložte do objektu `ThisWorkbook`.
6. V listu `CONFIG` zkontrolujte hodnotu `MT5CommonFolderPath`. Výchozí cesta je `%APPDATA%\MetaQuotes\Terminal\Common\Files\`.

## Použití

- Analýzy zapisujte do tabulky `tblAnalyzy` na listu `ANALYZY`.
- Povolené hodnoty `Verdict` jsou `BUY`, `AVOID`, `SHORT`, `WATCH`.
- Povolené hodnoty `Status` jsou `OPEN`, `CLOSED`, `CANCELLED`.
- Makro `RefreshAllMT5Data` načte `MT5_Analysis_Prices.csv` a `MT5_Portfolio_Positions.csv`, dopočítá výsledky analýz, aktuální portfolio a dashboard.
- Makro `UpdateTrackedSymbols` zapíše unikátní symboly z otevřených analýz do `TrackedSymbols.csv`.
- CSV soubory nenechávejte otevřené v Excelu, protože MT5 nemusí umět zapisovat do zamčených souborů.

## Očekávané CSV soubory

`MT5_Analysis_Prices.csv` používá středník a sloupce:

```text
SnapshotTime;Symbol;Bid;Ask;Last;Spread;Point;Digits
```

`MT5_Portfolio_Positions.csv` používá středník a sloupce:

```text
SnapshotTime;AccountLogin;AccountCurrency;Symbol;Ticket;Type;Volume;OpenTime;OpenPrice;CurrentPrice;PercentFromOpen;Profit;Swap;Magic;Comment
```

`TrackedSymbols.csv` má formát:

```text
Symbol
AAPL
MSFT
NVDA
AMD
```
