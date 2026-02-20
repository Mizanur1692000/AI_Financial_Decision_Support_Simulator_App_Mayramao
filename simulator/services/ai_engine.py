from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from django.conf import settings


def generate_ai_guidance(user_data: dict, calculation: dict):

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_template("""
You are a conservative financial advisor.

User Profile:
Income: {monthly_income}
Dependents: {dependents}
Income Stability: {income_stability}
Risk Tolerance: {risk_tolerance}

Financial Results:
Risk Level: {risk_level}
Disposable Income After Purchase: {new_disposable_income}
Savings After Purchase: {savings_after_purchase}
Emergency Buffer Needed: {emergency_buffer}
Monthly Payment: {monthly_payment}

Explain:
1. Why this is SAFE, TIGHT or RISKY.
2. Long-term impact.
3. Safer alternative if risky.

Keep response concise and practical.
""")

    chain = prompt | llm

    response = chain.invoke({
        **user_data,
        **calculation
    })

    return response.content
