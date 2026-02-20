from rest_framework import serializers


class FinancialSimulationSerializer(serializers.Serializer):

    monthly_income = serializers.FloatField(min_value=0)

    rent_mortgage = serializers.FloatField(min_value=0)
    utilities_internet = serializers.FloatField(min_value=0)
    subscriptions_insurance = serializers.FloatField(min_value=0)

    existing_loan_payment = serializers.FloatField(min_value=0)
    variable_expenses = serializers.FloatField(min_value=0)
    current_savings = serializers.FloatField(min_value=0)
    dependents = serializers.IntegerField(min_value=0)

    HOUSEHOLD_CHOICES = [
        ("all_or_most", "All or Most of It"),
        ("half", "About Half"),
        ("small_part", "A Small Part"),
        ("not_applicable", "Not Applicable"),
    ]

    INCOME_STABILITY_CHOICES = [
        ("very_stable", "Very Stable"),
        ("mostly_stable", "Mostly Stable"),
        ("sometimes_changes", "Sometimes Changes"),
        ("unpredictable", "Unpredictable"),
    ]

    RISK_TOLERANCE_CHOICES = [
        ("safety", "I Prefer Safety"),
        ("balanced", "Balanced"),
        ("risk_ok", "I'm Okay With Risk"),
    ]

    household_responsibility = serializers.ChoiceField(choices=HOUSEHOLD_CHOICES)
    income_stability = serializers.ChoiceField(choices=INCOME_STABILITY_CHOICES)
    risk_tolerance = serializers.ChoiceField(choices=RISK_TOLERANCE_CHOICES)

    purchase_amount = serializers.FloatField(min_value=0)
    payment_type = serializers.ChoiceField(choices=[("full", "Full"), ("loan", "Loan")])

    loan_duration = serializers.IntegerField(required=False, min_value=1)
    interest_rate = serializers.FloatField(required=False, min_value=0)

    def validate(self, data):
        if data["payment_type"] == "loan":
            if "loan_duration" not in data or "interest_rate" not in data:
                raise serializers.ValidationError(
                    "Loan duration and interest rate required for loan."
                )
        return data
