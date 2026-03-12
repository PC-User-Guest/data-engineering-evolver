# Data Engineering Project Evolver

A portfolio-quality system that automatically generates realistic GitHub activity in a Data Engineering repository. Perfect for showcasing expertise across Python, Java, SQL, PySpark, MLflow, Great Expectations, FastAPI, Streamlit, and Terraform.

## Overview

The **Data Engineering Project Evolver** is an automated platform that maintains a GitHub repository with daily, realistic contributions. It simulates a living data platform for a fictional e-commerce company, showcasing:

- **Data Ingestion**: Java data generator creates synthetic sales CSV files
- **ETL Pipelines**: PySpark jobs aggregate and transform data
- **Data Quality**: Great Expectations validates data constraints
- **ML Tracking**: MLflow logs experiments and models
- **ML Services**: FastAPI exposes prediction endpoints
- **Visualization**: Streamlit dashboard displays insights
- **Infrastructure**: Terraform provisions local services (Postgres, MinIO, Redis)

## Repository Structure

```
.
├── .github/
│   └── workflows/           # GitHub Actions (CI & scheduled automation)
├── api/                     # FastAPI application
├── dashboard/               # Streamlit dashboard
├── data_pipelines/          # PySpark ETL jobs
├── infra/                   # Terraform IaC (Docker provider)
├── java_generator/          # Java data generator (Maven)
├── mlflow/                  # MLflow experiment tracking
├── quality/                 # Great Expectations validation suites
├── scripts/                 # Orchestration and utility scripts
├── tests/                   # pytest test suite
├── state/                   # JSON state management (backlog, completed tasks)
├── .gitignore               # Standard Python/Java/Terraform ignores
└── requirements.txt         # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Java 11+ (for Maven builds)
- Terraform (optional, for infrastructure provisioning)
- Git with SSH or HTTPS access to GitHub

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/data-engineering-evolver.git
cd data-engineering-evolver

# Create a Python virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Build Java generator
cd java_generator
mvn package
cd ..
```

### Running Components Locally

#### 1. **Generate Sample Data**
```bash
cd java_generator
java -jar target/data-generator-1.0-SNAPSHOT.jar ../data/sample_sales.csv 1000
cd ..
```

#### 2. **Run PySpark ETL**
```bash
export ETL_INPUT=data/sample_sales.csv
export ETL_OUTPUT=data/parquet_output
python -m data_pipelines.etl
```

#### 3. **Run Data Quality Validation**
```bash
export GE_DATA=data/sample_sales.csv
python -m quality.validate
```

#### 4. **Train ML Model**
```bash
export MLFLOW_DATA=data/parquet_output
python -m mlflow.experiment
```

#### 5. **Start FastAPI Service**
```bash
export MLFLOW_MODEL_PATH=mlruns/0/model  # Update with actual model path
uvicorn api.main:app --reload --port 8000
```
Then visit: http://localhost:8000/docs for interactive API docs.

#### 6. **Run Streamlit Dashboard**
```bash
export DASHBOARD_DATA=data/sample_sales.csv
streamlit run dashboard/app.py
```

#### 7. **Deploy Infrastructure (Terraform)**
```bash
cd infra
terraform init
terraform plan
terraform apply
cd ..
```

### Testing

Run the pytest suite locally:
```bash
pytest -v
```

Or let GitHub Actions run tests automatically on push:
```bash
git push origin main
```

## Automated GitHub Activity

### CI/CD Pipeline
The `.github/workflows/test.yml` workflow runs automatically on every push and PR to ensure code quality.

### Daily Automation
The `.github/workflows/orchestrate.yml` workflow runs on a daily schedule (midnight UTC) to:

1. Load pending tasks from `state/backlog.json`
2. Generate realistic code changes (add ETL functions, update dashboards, etc.)
3. Create feature branches with meaningful commits
4. Open pull requests describing the changes
5. Auto-merge PRs to increase repository activity
6. Update task completion state

**Manual Trigger:**  
You can manually trigger the orchestration workflow from the GitHub UI under Actions > Daily Automation > Run Workflow.

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GH_TOKEN` | GitHub API token for creating PRs/merges | `ghp_xxxxx...` |
| `GITHUB_REPOSITORY` | Repository name (auto-set by Actions) | `PC-User-Guest/data-engineering-evolver` |
| `ETL_INPUT` | Input CSV path for PySpark job | `data/sample_sales.csv` |
| `ETL_OUTPUT` | Output Parquet path for PySpark | `data/parquet_output` |
| `GE_DATA` | Data path for validation | `data/sample_sales.csv` |
| `MLFLOW_DATA` | Data path for model training | `data/parquet_output` |
| `MLFLOW_MODEL_PATH` | MLflow model artifact URI | `mlruns/0/model` |
| `API_URL` | FastAPI service URL (from dashboard) | `http://localhost:8000/predict` |
| `DASHBOARD_DATA` | Data path for Streamlit | `data/sample_sales.csv` |

## Architecture

### Data Flow

```
Java Generator → CSV → PySpark ETL → Parquet
                         ↓
                    Great Expectations (validation)
                         ↓
                    MLflow (model training)
                         ↓
                    FastAPI (serve predictions)
                         ↓
                    Streamlit (visualize)
```

### Automation Flow

```
GitHub Schedule (cron) → orchestrate.yml workflow
    ↓
    1. Load backlog.json
    2. Select pending tasks
    3. Generate code changes (via generate_changes.py)
    4. Create feature branches
    5. Commit and push
    6. Create PRs via GitHub API
    7. Auto-merge
    8. Update state/completed_tasks.json
```

## Quality & Security

### Code Quality
- **Zero hardcoded secrets**: All sensitive values use environment variables
- **Graceful degradation**: Tests skip if dependencies unavailable
- **Type hints**: Functions include type annotations
- **Logging**: Comprehensive logging to file and stdout
- **Error handling**: Exceptions caught and logged, not silently ignored

### Dependency Management
- Uses pinned versions where possible
- Regular updates via Dependabot (can be enabled)
- No bloated or unused dependencies

### Testing
- Unit tests for core modules (pipelines, API)
- Tests run in CI on every push
- CI validates before merging

### Infrastructure as Code
- Terraform configurations define reproducible infrastructure
- Docker provider for local development
- No hardcoded credentials in IaC

## Troubleshooting

### Python Environment Issues

**`ModuleNotFoundError: No module named 'data_pipelines'` or `'api'`**
- **Cause**: Package `__init__.py` files missing or Python path not configured
- **Solution**:
  ```bash
  # Ensure all package directories have __init__.py
  touch data_pipelines/__init__.py
  touch api/__init__.py
  touch dashboard/__init__.py
  touch mlflow/__init__.py
  touch quality/__init__.py
  
  # Or run pytest from repo root:
  cd /path/to/data-engineering-evolver
  pytest -q
  ```

### FastAPI & Testing Issues

**`RuntimeError: The starlette.testclient module requires the httpx package`**
- **Cause**: httpx dependency missing (required by FastAPI test client)
- **Solution**:
  ```bash
  pip install httpx
  # Or reinstall requirements:
  pip install -r requirements.txt --force-reinstall
  ```

**`AttributeError: <module 'api.main'> has no attribute 'model'`**
- **Cause**: Global `model` variable not declared at module level in api/main.py
- **Solution**: Model is now declared globally at startup; ensure your api/main.py has `model = None` at module level

### Dependency & Version Issues

**Pandas/NumPy version conflicts**
- **Solution**: Use compatible versions as specified in requirements.txt
  ```bash
  pip install pandas>=2.0 numpy>=1.24 scikit-learn>=1.0
  ```

### CI/CD Workflow Issues

**CI Workflow Fails**
- Check the GitHub Actions logs: https://github.com/your-repo/actions
- Common issues:
  - Missing `GH_TOKEN` secret (set in GitHub Settings > Secrets > New repository secret)
  - PySpark/MLflow not installed (tests skip automatically if unavailable)
  - Branch conflicts (resolved with force push in orchestration)

**Orchestration Doesn't Generate Activity**
- Manually trigger: GitHub UI → Actions → Daily Automation → Run Workflow
- Check logs: Your repository will output `orchestrate.log` (download from Actions artifacts)
- Ensure `state/backlog.json` contains tasks (verify with `git log` to see state changes)
- Verify `GH_TOKEN` is set and valid (test with: `curl -H "Authorization: token $GH_TOKEN" https://api.github.com/user`)

### Local Execution Issues

**`PySpark not available` warnings in tests**
- **Expected behavior**: Tests skip gracefully if PySpark isn't installed
- **Solution**: Install PySpark if needed
  ```bash
  pip install pyspark>=3.3
  ```

**Port already in use when starting services**
- **FastAPI**:
  ```bash
  uvicorn api.main:app --port 8001  # Use different port
  ```
- **Streamlit**:
  ```bash
  streamlit run dashboard/app.py --server.port 8502
  ```
- **Terraform Docker containers**:
  ```bash
  docker ps  # List containers
  docker stop container_name  # Stop conflicting containers
  ```

### Terraform Issues

**`terraform init` requires Docker provider configuration**
- Ensure Docker is installed and running
- For Windows/WSL2:
  ```bash
  # Verify docker socket
  ls /var/run/docker.sock  # Linux
  # On Windows with Docker Desktop, Docker should be running
  ```

**"docker provider not supported" error**
- Verify Terraform version compatibility (requires v0.13+):
  ```bash
  terraform version
  ```

### General Debugging

**Enable verbose logging**
- Orchestration script:
  ```bash
  tail -f orchestrate.log
  ```
- Tests with more detail:
  ```bash
  pytest -vv --tb=long
  ```
- Terraform:
  ```bash
  TF_LOG=DEBUG terraform apply
  ```

## Contributing

This project generates its own contributions via the orchestration workflow. To manually add features:

1. Create a new branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -am "feat: describe change"`
3. Push and create a PR: `git push origin feature/my-feature`
4. The CI workflow will validate your changes

## License

This project is open source and available under the MIT License.

## About

Built to demonstrate a complete, production-quality data engineering platform with automated GitHub activity generation. Perfect for portfolio showcases, learning, and experimenting with modern data stack technologies.