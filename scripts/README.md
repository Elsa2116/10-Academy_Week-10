# Scripts

| Script                   | Description                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| `run_analysis.py`        | CLI runner — loads data, fits models, saves figures and a JSON results summary             |
| `export_deliverables.py` | Lightweight exporter for `outputs/results.json`, CSV summaries, and a short markdown brief |

## Usage

```bash
# From project root
python scripts/run_analysis.py --data data/brent_oil_prices.csv \
                                --events data/key_events.csv \
                                --output outputs/ \
                                --segments 4
```

If you only need the checked-in data packaged into the expected deliverable files, run:

```bash
python scripts/export_deliverables.py --output outputs/
```

### Arguments

| Flag         | Default                     | Description                                |
| ------------ | --------------------------- | ------------------------------------------ |
| `--data`     | `data/brent_oil_prices.csv` | Path to Brent price CSV                    |
| `--events`   | `data/key_events.csv`       | Path to key events CSV                     |
| `--output`   | `outputs/`                  | Directory for figures and JSON results     |
| `--segments` | `4`                         | Number of price regimes for multi-CP model |
| `--draws`    | `2000`                      | MCMC draw count per chain                  |
| `--tune`     | `2000`                      | MCMC tuning steps                          |
| `--seed`     | `42`                        | Random seed                                |
