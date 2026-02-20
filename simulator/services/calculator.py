def calculate_financial_impact(data: dict):

    fixed_expenses = (
        data["rent_mortgage"]
        + data["utilities_internet"]
        + data["subscriptions_insurance"]
    )

    baseline_expenses = (
        fixed_expenses
        + data["existing_loan_payment"]
        + data["variable_expenses"]
    )

    disposable_income = data["monthly_income"] - baseline_expenses

    monthly_payment = 0
    total_payable = data["purchase_amount"]

    if data["payment_type"] == "loan":
        total_payable = data["purchase_amount"] + (
            data["purchase_amount"]
            * (data["interest_rate"] / 100)
            * (data["loan_duration"] / 12)
        )
        monthly_payment = total_payable / data["loan_duration"]

    new_disposable_income = disposable_income - monthly_payment

    savings_after_purchase = data["current_savings"]

    if data["payment_type"] == "full":
        savings_after_purchase -= data["purchase_amount"]

    emergency_buffer = baseline_expenses * 3
    income_ratio = new_disposable_income / data["monthly_income"]

    risk_multiplier = 1.0

    if data["income_stability"] == "unpredictable":
        risk_multiplier += 0.2
    if data["risk_tolerance"] == "safety":
        risk_multiplier += 0.1

    adjusted_ratio = income_ratio * risk_multiplier

    if adjusted_ratio > 0.30 and savings_after_purchase > emergency_buffer:
        risk_level = "SAFE"
    elif adjusted_ratio > 0.10:
        risk_level = "TIGHT"
    else:
        risk_level = "RISKY"

    recovery_months = 0
    if data["payment_type"] == "full" and new_disposable_income > 0:
        recovery_months = data["purchase_amount"] / new_disposable_income

    return {
        "fixed_expenses": round(fixed_expenses, 2),
        "baseline_disposable_income": round(disposable_income, 2),
        "monthly_payment": round(monthly_payment, 2),
        "new_disposable_income": round(new_disposable_income, 2),
        "savings_after_purchase": round(savings_after_purchase, 2),
        "emergency_buffer": round(emergency_buffer, 2),
        "risk_level": risk_level,
        "recovery_months": round(recovery_months, 2),
    }
