from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Inline panel to show Profile choices inside the User change page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Clinical FHIR Profiles"

# Define a new User admin structure
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_fhir_id', 'is_staff')
    
    # Custom columns to display relational values in the list table
    def get_role(self, obj):
        return obj.profile.role
    get_role.short_description = 'Clinical Role'

    def get_fhir_id(self, obj):
        return obj.profile.fhir_resource_id
    get_fhir_id.short_description = 'FHIR Resource ID'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)