from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Defines user types in a clinical environment
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('practitioner', 'Practitioner/Doctor'),
        ('admin', 'Administrator'),
    ]
    
    # Links directly to Django's built-in User model (Username, Password, Email)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Store the clinical role
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    
    # Stores the unique string ID corresponding to their FHIR server resource
    fhir_resource_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="The logical ID of the Patient or Practitioner resource on the FHIR server"
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"