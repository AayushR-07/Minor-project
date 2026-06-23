from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # This explicitly forces DRF to protect this specific endpoint
def protected_health_check(request):
    return Response({
        "status": "Healthy",
        "message": f"Welcome back, {request.user.username}!",
        "clinical_context": "This data can only be seen because you possess a verified JWT security key."
    })    