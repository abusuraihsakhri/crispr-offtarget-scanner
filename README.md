# CRISPR Off-Target Scanner

> **Domain:** Computational Biology & AI Drug Discovery  
> **Reference Guidelines & Standards:** `wwPDB, IUPAC & CLSI Computational Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

CRISPR Off-Target Scanner is a Python-based tool for scanning and scoring potential off-target sites in CRISPR-Cas9 gene editing experiments. It provides:

- **Lookup scoring**: Token overlap and substring scoring for guide RNA target identification
- **CSV batch processing**: Process multiple queries from CSV files
- **REST API**: FastAPI-based REST endpoints for integration with analysis pipelines
- **Security**: Zero-PHI outbound guard and HMAC-SHA256 tamper-evident audit trail

---

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/crispr-offtarget-scanner.git
cd crispr-offtarget-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Deployment

```bash
# Build and run with Docker Compose
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
docker-compose up --build

# Or build and run manually
docker build -t crispr-offtarget-scanner .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") crispr-offtarget-scanner
```

---

## Usage

### Command Line Interface

#### Single Lookup
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
```

#### Batch CSV Processing
```bash
python cli.py batch -i input.csv -o results.csv
```

#### Chat Query
```bash
python cli.py chat "Explain CRISPR off-target effects"
```

#### Verify Audit Trail
```bash
python cli.py verify-audit
```

#### Start API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Direct Module Usage

```python
from crispr_offtarget import lookup, process_csv

# Single lookup
result = lookup("cas9 guide rna")
print(result["top_hit"], result["score"])

# Batch processing
results = process_csv("input.csv", "output.csv")
```

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Chat with supervisor |
| `/api/audit/logs` | GET | Get audit trail |

---

## Security

### Audit Secret Key

The application requires an `AUDIT_SECRET_KEY` environment variable for HMAC-SHA256 audit trail signing. **Never hardcode secrets in production.**

```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_hex(32))"

# Set the environment variable
export AUDIT_SECRET_KEY="your-generated-key"
```

### Zero-PHI Guard

The system includes a PHI (Protected Health Information) outbound guard that detects and blocks:
- Medical Record Numbers (MRN)
- Social Security Numbers
- Phone numbers
- Email addresses
- Patient names and dates of birth

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=.

# Run simulation benchmark
python simulator.py 1000
```

---

## Project Structure

```
crispr-offtarget-scanner/
├── agents/                 # Enterprise agent framework
│   ├── __init__.py
│   ├── api.py             # FastAPI REST server
│   ├── base.py            # Security, PHI guard, audit trail
│   ├── llm_factory.py     # LLM provider factory
│   ├── models.py          # Pydantic data models
│   ├── supervisor.py      # Task orchestrator
│   └── workers.py         # Specialized evaluation workers
├── tests/                  # Test suite
│   ├── test_crispr_offtarget_scanner.py
│   └── test_enrichment.py
├── cli.py                  # Command line interface
├── crispr_offtarget.py     # Core lookup and CSV processing
├── enrichment.py           # Feature enrichment engines
├── simulator.py            # High-throughput simulation
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker build configuration
├── docker-compose.yml     # Docker Compose configuration
└── openapi_spec.json      # OpenAPI specification
```

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
