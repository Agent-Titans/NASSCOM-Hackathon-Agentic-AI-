# SAARTHI — routing & assessment test reports

HTML pass/fail reports from automated routing suites. Open **`index.html`** in a browser (no server needed).

| Report | Description |
|--------|-------------|
| `final_master_report.html` | Overall score, feature matrix, gaps |
| `master50.html` | 50-firm routing test |
| `master100.html` | 100-ticket multi-firm suite |
| `feature_matrix.html` | Feature-wise status |

Regenerate:

```bash
python scripts/run_final_assessment.py
python scripts/run_master50_test.py
```
