from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import FinancialSimulationSerializer
from .services.calculator import calculate_financial_impact
from .services.ai_engine import generate_ai_guidance


class FinancialSimulationView(GenericAPIView):
    serializer_class = FinancialSimulationSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        calculation = calculate_financial_impact(validated_data)

        ai_guidance = generate_ai_guidance(
            validated_data,
            calculation
        )

        return Response(
            {
                "calculation": calculation,
                "ai_guidance": ai_guidance,
            },
            status=status.HTTP_200_OK
        )
