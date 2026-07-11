# Data Directory

## Files

| File | Description |
|------|-------------|
| `brent_oil_prices.csv` | Historical Brent crude oil daily closing prices (May 1987 – Sep 2022) |
| `key_events.csv` | Compiled dataset of 22 major geopolitical/economic events |

## brent_oil_prices.csv Format

```
Date,Price
20-May-87,18.63
21-May-87,18.45
...
```

- `Date`: Trading date in `day-Mon-YY` format (e.g. `20-May-87`)
- `Price`: Brent crude spot price in USD per barrel

## Data Source

The official Brent oil price dataset can be downloaded from:
- **EIA (US Energy Information Administration):** https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RBRTE&f=D
- **World Bank Commodity Price Data:** https://www.worldbank.org/en/research/commodity-markets

The included `brent_oil_prices.csv` contains a representative sample for demonstration.
For the full analysis, replace it with the complete EIA dataset.

## key_events.csv Format

Columns: `EventDate`, `EventName`, `Category`, `Description`, `ExpectedPriceEffect`
