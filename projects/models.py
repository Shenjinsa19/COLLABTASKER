from django.db import models
from accounts.models import CustomUser
class Project(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='created_projects')
    members=models.ManyToManyField(CustomUser,related_name='projects')
    def __str__(self):
        return self.name
class Task(models.Model):
    STATUS_CHOICES = (
        ('todo','To Do'),
        ('inprogress','In Progress'),
        ('completed','Completed'),
    )

    PRIORITY_CHOICES = (
        ('low','Low'),
        ('medium','Medium'),
        ('high','High'),
    )
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='tasks')
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    assigned_to=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='tasks')
    deadline=models.DateField()
    priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES)
    status=models.CharField(max_length=15,choices=STATUS_CHOICES,default='todo')
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True,related_name='created_tasks')
    updated_by=models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='tasks_updated',null=True, blank=True)

    def __str__(self):
        return self.title
