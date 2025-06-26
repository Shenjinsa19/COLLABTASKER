from django.urls import path
from .views import RegisterView,LoginView,LogoutView,WebLoginView,WebRegisterView

urlpatterns = [
    path('api/register/',RegisterView.as_view(),name='api-register'),
    path('api/login/',LoginView.as_view(),name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),


#for templates
    path('register/', WebRegisterView.as_view(), name='register'),
    path('login/', WebLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
