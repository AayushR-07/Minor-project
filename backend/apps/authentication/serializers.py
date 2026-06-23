from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Inject identity tracking directly into the encrypted JWT token payload
        try:
            token['role'] = user.profile.role
            token['fhir_id'] = user.profile.fhir_resource_id
        except Exception:
            token['role'] = 'patient'
            token['fhir_id'] = None

        return token