# Kaoling

This repository contains the Jupyter notebook `kaoling.ipynb` (final project).

Quick start

1. Create and activate a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Open the notebook:

```powershell
# in this folder
jupyter lab
```

CI

A GitHub Actions workflow is included at `.github/workflows/python-ci.yml` that installs dependencies and runs tests (if any).

Add a GitHub remote and push:

```powershell
git remote add origin <your-repo-url>
git push -u origin main
```

