from django.urls import path
from .views import RegisterView, CustomLoginView, protected_health_check
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('test-health/', protected_health_check, name='protected_health_check'),
]