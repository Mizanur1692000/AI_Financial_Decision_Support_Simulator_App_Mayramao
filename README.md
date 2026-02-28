# AI Financial Decision Support Simulator

A Django + Django REST Framework (DRF) API that simulates the financial impact of a purchase (full payment or loan) and returns **(1)** a deterministic calculation and **(2)** AI guidance generated with Google Gemini via LangChain.

## What this project does

Given a user’s income/expenses/savings and a proposed purchase:

- Computes disposable income, emergency buffer, loan payment (if applicable), and a simple risk level.
- Calls Gemini to generate structured guidance (JSON) tailored to the user profile and the calculation.
- Returns a single API response that contains the numeric calculation plus AI guidance.

## Tech stack

- Django (project: `financial_simulator`)
- Django REST Framework (app: `simulator`)
- LangChain + `langchain-google-genai`
- Google Gemini model: `gemini-2.5-flash`
- SQLite (default DB)

## Repository structure

- `manage.py` — main Django entrypoint (run commands from repo root)
- `financial_simulator/` — Django project settings + root URLs
- `simulator/` — DRF API (serializer + view + URL routes)
- `simulator/services/calculator.py` — deterministic finance calculation
- `simulator/services/ai_engine.py` — Gemini/LangChain prompt + JSON parsing
- `db.sqlite3` — local SQLite database

## Configuration (.env)

This project loads environment variables using `python-dotenv` from a `.env` file in the repository root.

Create a file named `.env`:

```env
# Required for AI guidance
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional (Django will fall back to a dev key if missing)
SECRET_KEY=your_django_secret_key_here
```

Notes:
- If `GEMINI_API_KEY` is missing or invalid, the `/api/simulate/` endpoint will fail when calling Gemini.
- `DEBUG` is currently `True` in `financial_simulator/settings.py` (development mode).

## Setup (Windows / PowerShell)

From the repository root:

1) Create + activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Run database migrations

```powershell
python manage.py migrate
```

4) Start the server

```powershell
python manage.py runserver
```

Server runs at: http://127.0.0.1:8000/

## API

### POST `/api/simulate/`

Runs the financial simulation and returns:

- `calculation`: numeric outputs + `risk_level`
- `ai_guidance`: structured AI output (assessment title, guidance, insights, alternatives)
- `ai_guidance_text`: a convenience string extracted from `ai_guidance.guidance`

#### Request body (JSON)

Required fields:

- `monthlyIncome` (float, >= 0)
- `rent` (float, >= 0)
- `utilities` (float, >= 0)
- `subscriptionsInsurance` (float, >= 0)
- `existingLoans` (float, >= 0)
- `variableExpenses` (float, >= 0)
- `currentSavings` (float, >= 0)
- `dependents` (int, >= 0)
- `householdResponsibilityLevel` (choice)
  - `all_or_most` | `half` | `small_part` | `not_applicable`
- `incomeStability` (choice)
  - `very_stable` | `mostly_stable` | `sometimes_changes` | `unpredictable`
- `riskTolerance` (choice)
  - `safety` | `balanced` | `risk_ok`
- `purchaseAmount` (float, >= 0)
- `paymentType` (choice)
  - `full` | `loan`

Loan-only fields (required when `paymentType="loan"`):

- `loanDuration` (int, >= 1) — number of months
- `interestRate` (float, >= 0) — annual rate, percent

Optional “Future Goal Plan” fields (used only to enrich AI guidance):

- `planName` (string, optional)
- `targetAmount` (float, optional)
- `targetDate` (date, optional)
  - accepted formats: `DD/MM/YYYY` or `YYYY-MM-DD`
- `goalDescription` (string, optional)

#### Example request (PowerShell)

```powershell
$body = @{
  monthlyIncome = 4500
  rent = 1400
  utilities = 220
  subscriptionsInsurance = 180
  existingLoans = 150
  variableExpenses = 900
  currentSavings = 6000
  dependents = 1
  householdResponsibilityLevel = "half"
  incomeStability = "mostly_stable"
  riskTolerance = "balanced"
  purchaseAmount = 2500
  paymentType = "loan"
  loanDuration = 12
  interestRate = 18
  planName = "Emergency fund"
  targetAmount = 10000
  targetDate = "2026-12-31"
  goalDescription = "Build a 3–6 month safety net."
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/simulate/" -ContentType "application/json" -Body $body
```

#### Example response (shape)

```json
{
  "calculation": {
    "fixed_expenses": 1800.0,
    "baseline_disposable_income": 1350.0,
    "monthly_payment": 295.83,
    "new_disposable_income": 1054.17,
    "savings_after_purchase": 6000.0,
    "emergency_buffer": 8550.0,
    "risk_level": "TIGHT",
    "recovery_months": 0.0
  },
  "ai_guidance": {
    "assessment_title": "Proceed with Caution",
    "risk_level": "TIGHT",
    "guidance": "...",
    "key_insights": [
      {"title": "...", "detail": "..."}
    ],
    "safer_alternatives": ["...", "..."]
  },
  "ai_guidance_text": "..."
}
```

## How the calculation works (high level)

Implemented in `simulator/services/calculator.py`:

- **Fixed expenses** = rent/mortgage + utilities/internet + subscriptions/insurance
- **Baseline expenses** = fixed expenses + existing loan payment + variable expenses
- **Baseline disposable income** = monthly income − baseline expenses
- If `paymentType="loan"`:
  - **Total payable** = purchase + purchase × (interestRate/100) × (loanDuration/12)
  - **Monthly payment** = total payable / loanDuration
- **New disposable income** = baseline disposable income − monthly payment
- If `paymentType="full"`:
  - **Savings after purchase** = current savings − purchase amount
- **Emergency buffer** = baseline expenses × 3
- Risk level is derived from the adjusted disposable-income ratio and savings vs emergency buffer.

Risk levels returned:

- `SAFE`
- `TIGHT`
- `RISKY`

## Troubleshooting

- **400 validation errors**: Check required fields and allowed choice values.
- **AI output not structured**: The model is instructed to return JSON, but if it returns extra text, the system falls back to extracting the first `{...}` JSON object it can find.
- **Gemini failures**: Verify `GEMINI_API_KEY` is set in `.env` and the server was restarted after adding it.

## Development notes

- Root URL config: `financial_simulator/urls.py` mounts the API at `/api/`.
- The main endpoint is implemented in `simulator/views.py` (`FinancialSimulationView`).
- This repo includes a secondary `financial_simulator/manage.py` for convenience, but you can (and should) run `python manage.py ...` from the repo root.
