# AI Financial Decision Support Simulator (JVAI)

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

- `monthly_income` (float, >= 0)
- `rent_mortgage` (float, >= 0)
- `utilities_internet` (float, >= 0)
- `subscriptions_insurance` (float, >= 0)
- `existing_loan_payment` (float, >= 0)
- `variable_expenses` (float, >= 0)
- `current_savings` (float, >= 0)
- `dependents` (int, >= 0)
- `household_responsibility` (choice)
  - `all_or_most` | `half` | `small_part` | `not_applicable`
- `income_stability` (choice)
  - `very_stable` | `mostly_stable` | `sometimes_changes` | `unpredictable`
- `risk_tolerance` (choice)
  - `safety` | `balanced` | `risk_ok`
- `purchase_amount` (float, >= 0)
- `payment_type` (choice)
  - `full` | `loan`

Loan-only fields (required when `payment_type="loan"`):

- `loan_duration` (int, >= 1) — number of months
- `interest_rate` (float, >= 0) — annual rate, percent

Optional “Future Goal Plan” fields (used only to enrich AI guidance):

- `goal_plan_name` (string, optional)
- `goal_target_amount` (float, optional)
- `goal_target_date` (date, optional)
  - accepted formats: `DD/MM/YYYY` or `YYYY-MM-DD`
- `goal_short_description` (string, optional)

#### Example request (PowerShell)

```powershell
$body = @{
  monthly_income = 4500
  rent_mortgage = 1400
  utilities_internet = 220
  subscriptions_insurance = 180
  existing_loan_payment = 150
  variable_expenses = 900
  current_savings = 6000
  dependents = 1
  household_responsibility = "half"
  income_stability = "mostly_stable"
  risk_tolerance = "balanced"
  purchase_amount = 2500
  payment_type = "loan"
  loan_duration = 12
  interest_rate = 18
  goal_plan_name = "Emergency fund"
  goal_target_amount = 10000
  goal_target_date = "2026-12-31"
  goal_short_description = "Build a 3–6 month safety net."
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
- If `payment_type="loan"`:
  - **Total payable** = purchase + purchase × (interest_rate/100) × (loan_duration/12)
  - **Monthly payment** = total payable / loan_duration
- **New disposable income** = baseline disposable income − monthly payment
- If `payment_type="full"`:
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
