from django.urls import path
from .views import FinancialSimulationView

urlpatterns = [
    path("simulate/", FinancialSimulationView.as_view(), name="simulate"),
]
