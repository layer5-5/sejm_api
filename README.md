# sejm-client

A typed Python client for the Polish Sejm API (`api.sejm.gov.pl`) and ELI API (`api.sejm.gov.pl/eli`).

## Installation

```bash
pip install sejm-client
# or from source
pip install git+https://github.com/layer5-5/sejm_api.git
```

## Quick start

```python
from sejm_client import SejmClient, EliClient, EliPublisher

client = SejmClient()

# All processes from the current term
processes = client.get_processes(limit=50)

# Only Dziennik Ustaw (actual statutes and regulations)
du_processes = client.get_processes(publisher=EliPublisher.DU)

# Only Monitor Polski (government announcements, appointments)
mp_processes = client.get_processes(publisher=EliPublisher.MP)
```

## Publishers

The Polish legal system publishes acts in two official gazette series:

| Code | Name | Description |
|------|------|-------------|
| `EliPublisher.DU` | Dziennik Ustaw | Statutes, regulations, decrees — the primary source of binding law |
| `EliPublisher.MP` | Monitor Polski | Government announcements, ministerial appointments, state honours, non-binding resolutions |

## Processes

```python
from sejm_client import SejmClient, EliPublisher
from datetime import date

client = SejmClient()

# Recent DU bills from the last 30 days
processes = client.get_processes(
    publisher=EliPublisher.DU,
    date_from=date(2024, 1, 1),
)

for proc in processes:
    print(proc.title)
    print(proc.eli)       # e.g. "DU/2024/1615"
    print(proc.passed)    # bool
```

## ELI — fetching act text

Acts published in Dziennik Ustaw have machine-readable text available via the ELI API.
Use the act metadata to find the correct download URL — **do not** use `EliClient.get_act_text_url()`
as it constructs an incorrect path.

```python
import requests, io, pdfplumber
from sejm_client import EliClient

eli_client = EliClient()

# Get act metadata
r = requests.get("https://api.sejm.gov.pl/eli/acts/DU/2024/1615")
data = r.json()

# Find the original PDF in the texts array (type "O")
for text in data.get("texts", []):
    if text["type"] == "O" and text["fileName"].endswith(".pdf"):
        url = f"https://api.sejm.gov.pl/eli/acts/DU/2024/1615/text/O/{text['fileName']}"
        pdf_bytes = requests.get(url).content
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            full_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        break
```

Text types in the `texts` array:

| Type | Description |
|------|-------------|
| `H`  | HTML version |
| `O`  | Original PDF (use this for text extraction) |
| `I`  | Issuance/promulgation PDF |
| `T`  | Consolidated text PDF |

## Bills

```python
from sejm_client import SejmClient, BillStatus

client = SejmClient()

active = client.get_active_bills()
passed = client.get_passed_bills()
recent = client.get_recent_bills(days=30)
```

## MPs and Clubs

```python
mps   = client.get_mps(active_only=True)
clubs = client.get_clubs()
```

## EliClient

```python
from sejm_client import EliClient, ActStatus

eli = EliClient()

# Acts from a specific year
acts = eli.get_acts(publisher="DU", year=2024)

# Recent acts
recent = eli.get_recent_acts(days=30)

# Single act by ELI
act = eli.get_act_by_eli("DU/2024/1615")
print(act.text_pdf)   # bool — whether PDF text is available
print(act.text_html)  # bool — whether HTML text is available
```
