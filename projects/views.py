from django.shortcuts import render,redirect
from rest_framework import generics, permissions
from .models import Project,Task
from .serializers import ProjectSerializer,TaskSerializer
from .permissions import IsAdminPMOrReadOnly
from django.core.mail import send_mail
from django.conf import settings

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset=Project.objects.all()
    serializer_class=ProjectSerializer
    permission_classes=[permissions.IsAuthenticated,IsAdminPMOrReadOnly]

    def perform_create(self,serializer):
        serializer.save(created_by=self.request.user)
    # def form_valid(self, form):
    #     form.instance.created_by=self.request.user
    #     response=super().form_valid(form)
    #     members=form.instance.members.all()
    #     for member in members:
    #         send_mail(
    #             subject=f"You have been added to project: {form.instance.name}",
    #             message=f"Hello {member.get_full_name() or member.username},\n\n"
    #                     f"You have been assigned to the project '{form.instance.name}'. Please check your dashboard.",
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             recipient_list=[member.email],
    #             fail_silently=False,
    #         )
    #     return response

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Project.objects.all()
    serializer_class=ProjectSerializer
    permission_classes=[permissions.IsAuthenticated,IsAdminPMOrReadOnly]


from projects.tasks import send_task_assignment_email
class TaskListCreateView(generics.ListCreateAPIView):
    queryset=Task.objects.all()
    serializer_class=TaskSerializer
    permission_classes=[permissions.IsAuthenticated, IsAdminPMOrReadOnly]

    def perform_create(self,serializer):
        task=serializer.save(created_by=self.request.user)
        if task.assigned_to:
            send_task_assignment_email.delay(
                task.assigned_to.email,
                task.title
            )

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Task.objects.all()
    serializer_class=TaskSerializer
    permission_classes=[permissions.IsAuthenticated,IsAdminPMOrReadOnly]


#furthr needed -----------------dont remove
# from django.core.cache import cache
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .serializers import TaskSerializer
# @api_view(['GET'])
# def cached_task_list(request):
#     user = request.user
#     cache_key = f"user_{user.id}_task_list"
#     data = cache.get(cache_key)
#     if data is None:
#         tasks = Task.objects.filter(assigned_to=user)
#         serializer = TaskSerializer(tasks, many=True)
#         data = serializer.data
#         cache.set(cache_key, data, timeout=60)  
#     return Response(data)




#for templates

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden


class HomePageView(TemplateView):
    template_name='collabtasker/home.html'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name', 'description','members']  
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'collab':
            messages.warning(request, "Collaborators are not allowed to create projects.")
            return redirect('project_list')  
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProjectListView(LoginRequiredMixin, ListView):
    model=Project
    template_name='projects/project_list.html'
    context_object_name='projects'

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ['name', 'description', 'members']
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')

    def dispatch(self, request, *args, **kwargs):   #bfr view
        if request.user.role == 'collab':
            return HttpResponseForbidden("Collaborators cannot update projects.")
        return super().dispatch(request, *args, **kwargs)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'collab':
            return HttpResponseForbidden("Collaborators cannot delete projects.")
        return super().dispatch(request, *args, **kwargs)




class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'description', 'assigned_to', 'deadline', 'priority', 'status']
    template_name = 'projects/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        if request.user.role == 'collab':
            messages.warning(request, "Collaborators are not allowed to create tasks.")
            return redirect('task_list', project_id=self.project.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        form.instance.project = self.project
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'project_id': self.project.id})

class TaskListView(ListView):
    model = Task
    template_name = 'projects/task_list.html' 
    context_object_name = 'tasks'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Task.objects.filter(project__id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('project_id'))
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'

class TaskUpdateView(UpdateView):
    model = Task
    fields = ['title', 'description', 'assigned_to', 'deadline', 'priority', 'status']
    template_name = 'projects/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.task = self.get_object()
        self.project = self.task.project
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'project_id': self.project.id})

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model=Task
    template_name='projects/task_confirm_delete.html'

    def dispatch(self, request,*args,**kwargs):
        if request.user.role == 'collab':
            return HttpResponseForbidden("Collaborators cannot delete tasks.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('task_list',kwargs={'project_id': self.object.project.id})