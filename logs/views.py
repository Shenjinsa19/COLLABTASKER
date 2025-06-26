from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import ActivityLog
from .serializers import ActivityLogSerializer

class ActivityLogListView(generics.ListAPIView):
    queryset=ActivityLog.objects.all().order_by('-timestamp')
    serializer_class=ActivityLogSerializer
    permission_classes=[permissions.IsAuthenticated]  #rem ad auth
