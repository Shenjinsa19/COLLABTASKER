# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer,LoginSerializer
from django.core.cache import cache

from .tasks import send_welcome_email
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
       user = serializer.save()
       print("Registered user:", user.email)
       subject = "Welcome to CollabTasker"
       message = f"Hi {user.name}, thanks for registering!"
       result = send_welcome_email.delay(user.email, subject, message)
    #    print("Task ID:", result.id)




class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data
        refresh=RefreshToken.for_user(user)
        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "user":{
                "email":user.email,
                "name":user.name,
                "role":user.role,
            }
        })




from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout


class WebLoginView(View):
    def get(self, request):
        cached_email = cache.get('recent_email')
        cached_password = cache.get('recent_password')
        return render(request, 'accounts/login.html', {
            'cached_email': cached_email,
            'cached_password': cached_password,
        })

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('home')

        return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})



class WebRegisterView(View):
    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})

        user = CustomUser.objects.create_user(name=name, email=email, password=password)

        # ✅ Store in Redis cache for 5 minutes
        cache.set('recent_email', email, timeout=300)
        cache.set('recent_password', password, timeout=300)

        # Send welcome email using Celery
        subject = "Welcome to CollabTasker"
        message = f"Hi {user.name}, thanks for registering!"
        send_welcome_email.delay(user.email, subject, message)

        return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
