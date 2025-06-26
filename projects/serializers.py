from rest_framework import serializers
from .models import Project
from accounts.models import CustomUser

class ProjectSerializer(serializers.ModelSerializer):
    members=serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)

    class Meta:
        model=Project
        fields=['id','name','description','created_at','created_by','members']
        read_only_fields=['id','created_at','created_by']

    def create(self,validated_data):
        members=validated_data.pop('members',[])
        validated_data.pop('created_by',None)
    
        project=Project.objects.create(
        created_by=self.context['request'].user,
        **validated_data
    )
        project.members.set(members)
        return project

    
from .models import Task
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields='__all__'
        read_only_fields=['created_at']
