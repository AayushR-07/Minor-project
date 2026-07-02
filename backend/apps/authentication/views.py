from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer

class CustomLoginView(TokenObtainPairView):
   
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_health_check(request):
    return Response({
        "status": "Healthy",
        "message": f"Welcome back, {request.user.username}!",
        "clinical_context": "This data can only be seen because you possess a verified JWT security key."
    })