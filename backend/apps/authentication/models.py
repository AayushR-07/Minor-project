from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('practitioner', 'Practitioner/Doctor'),
        ('admin', 'Administrator'),
    ]
    

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
   
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    
    nmc_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    is_nmc_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    fhir_resource_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="The logical ID of the Patient or Practitioner resource on the FHIR server"
    )
    fhir_resource_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="The full, valid HL7 FHIR specification JSON string for this user"
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"