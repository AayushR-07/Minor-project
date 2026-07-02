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

class DashboardMeView(APIView):
  
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile  
        
        
        dashboard_data = {
            "account_status": "Active",
            "user_context": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
            },
            "security_claims": {
                "assigned_role": profile.role,
                "fhir_id": profile.fhir_resource_id,
            },
            
            "fhir_standard_payload": profile.fhir_resource_data
        }
        
        
        if profile.role == 'practitioner':
            dashboard_data["clinical_profile"] = {
                "nmc_number": profile.nmc_number,
                "specialization": profile.specialization,
                "is_council_verified": profile.is_nmc_verified
            }
            
            dashboard_data["dashboard_metrics"] = {
                "assigned_patients_count": 0,
                "pending_consultations": 0,
                "recent_diagnostic_reports_issued": []
            }
            
        elif profile.role == 'patient':
            dashboard_data["demographics"] = {
                "date_of_birth": profile.date_of_birth,
                "phone_number": profile.phone_number
            }
            
            dashboard_data["medical_file_summary"] = {
                "allergies_recorded": 0,
                "active_medications": [],
                "lab_report_history_count": 0
            }

        return Response(dashboard_data)