from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 1. Safely generate the SQL profile entry first
        profile = UserProfile.objects.create(user=instance)
        
        if profile.role == 'patient':
            fhir_patient = Patient()
            fhir_patient.active = True
            
            # 2. Strict FHIR Compliance: Only construct structural name components if string values exist
            name_building = HumanName()
            has_name_data = False

            if instance.first_name:
                name_building.given = [instance.first_name]
                has_name_data = True
            else:
                # If no first name exists (like a quick superuser setup), use the username
                name_building.given = [instance.username]
                has_name_data = True

            if instance.last_name:
                name_building.family = instance.last_name
                has_name_data = True

            if has_name_data:
                fhir_patient.name = [name_building]
            
            # Simulate endpoint reference allocation
            profile.fhir_resource_id = f"Patient/local-gen-{instance.id}"
            profile.save()