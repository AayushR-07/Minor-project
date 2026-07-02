import uuid
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from .services import verify_nmc_credentials
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        
        try:
            token['role'] = user.profile.role
            token['fhir_id'] = user.profile.fhir_resource_id
        except Exception:
            token['role'] = 'patient'
            token['fhir_id'] = None

        return token
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    
    
    nmc_number = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 
                  'nmc_number', 'date_of_birth', 'phone_number']

    def validate(self, attrs):
        role = attrs.get('role')
        if role == 'practitioner':
            nmc_no = attrs.get('nmc_number')
            if not nmc_no:
                raise serializers.ValidationError({"nmc_number": "NMC Number is required for doctors."})
            
            nmc_data = verify_nmc_credentials(nmc_no)
            if not nmc_data:
                raise serializers.ValidationError({"nmc_number": "NMC record not found in the council registry."})
            
            # Use official names from Nepal Medical Council to prevent identity fraud
            attrs['first_name'] = nmc_data['first_name']
            attrs['last_name'] = nmc_data['last_name']
            self.context['nmc_data'] = nmc_data
            
        return attrs
    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop('role')
        nmc_number = validated_data.pop('nmc_number', None)
        date_of_birth = validated_data.pop('date_of_birth', None)
        phone_number = validated_data.pop('phone_number', None)
        password = validated_data.pop('password')
        
        # 1. Create and save the base User account
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Generate a unique logical FHIR ID reference
        generated_fhir_id = str(uuid.uuid4())
        fhir_payload = {}

        # 2. Compile role-specific configurations & FHIR schemas
        if role == 'practitioner':
            nmc_data = self.context.get('nmc_data')
            fhir_payload = {
                "resourceType": "Practitioner",
                "id": generated_fhir_id,
                "identifier": [{
                    "system": "https://www.nmc.org.np",
                    "value": nmc_number
                }],
                "name": [{
                    "use": "official",
                    "text": f"Dr. {user.first_name} {user.last_name}",
                    "family": user.last_name,
                    "given": [user.first_name]
                }],
                "qualification": [{
                    "code": {
                        "text": nmc_data['specialization']
                    }
                }]
            }
            
            # Using update_or_create handles BOTH scenarios smoothly:
            # - If a signal created a profile, this updates it.
            # - If no signal exists, this creates a fresh one.
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": role,
                    "nmc_number": nmc_number,
                    "specialization": nmc_data['specialization'],
                    "is_nmc_verified": True,
                    "fhir_resource_id": generated_fhir_id,
                    "fhir_resource_data": fhir_payload
                }
            )
            
        elif role == 'patient':
            fhir_payload = {
                "resourceType": "Patient",
                "id": generated_fhir_id,
                "name": [{
                    "use": "official",
                    "family": user.last_name,
                    "given": [user.first_name]
                }],
                "telecom": [{
                    "system": "phone",
                    "value": phone_number,
                    "use": "mobile"
                }] if phone_number else [],
                "birthDate": str(date_of_birth) if date_of_birth else None
            }
            
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": role,
                    "date_of_birth": date_of_birth,
                    "phone_number": phone_number,
                    "fhir_resource_id": generated_fhir_id,
                    "fhir_resource_data": fhir_payload
                }
            )
            
        return user
    
    