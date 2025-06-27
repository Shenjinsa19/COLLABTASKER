from django.shortcuts import render,redirect
from rest_framework import generics, permissions
from .models import Project,Task
from .serializers import ProjectSerializer,TaskSerializer
from .permissions import IsAdminPMOrReadOnly
from django.core.mail import send_mail
from django.conf import settings
from .tasks import send_task_assignment_email
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







#for templ


from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.core.cache import cache

# Import your models and celery tasks
from .models import Project, Task
from .tasks import send_task_assignment_email

class HomePageView(TemplateView):
    template_name = 'collabtasker/home.html'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name', 'description', 'members']  
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'collab':
            messages.warning(request, "Collaborators are not allowed to create projects.")
            return redirect('project_list')  
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Invalidate project list cache for this user after creating new project
        cache.delete(f'user_projects_{self.request.user.id}')
        return response
    
import logging
logger = logging.getLogger(__name__)
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    # def get_queryset(self):
    #     cache_key = f'user_projects_{self.request.user.id}'
    #     projects = cache.get(cache_key)
    #     if not projects:
    #         projects = Project.objects.filter(created_by=self.request.user).select_related('created_by').prefetch_related('members').all()
    #         cache.set(cache_key, projects, 300)  # Cache for 5 minutes
    #     return projects
    def get_queryset(self):
      cache_key = f'user_projects_{self.request.user.id}'
      projects = cache.get(cache_key)
      if projects:
        logger.info(f'Cache hit for {cache_key}')
        print(f'Cache hit for {cache_key}')
      else:
        logger.info(f'Cache miss for {cache_key}, querying DB')
        print(f'Cache miss for {cache_key}, querying DB')
        projects = Project.objects.filter(created_by=self.request.user)
        cache.set(cache_key, projects, 300)
      return projects







class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_object(self, queryset=None):
        project_id = self.kwargs.get('pk')
        cache_key = f'project_{project_id}'
        project = cache.get(cache_key)
        if not project:
            project = super().get_object(queryset)
            cache.set(cache_key, project, 300)  # Cache for 5 minutes
        return project

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ['name', 'description', 'members']
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'collab':
            return HttpResponseForbidden("Collaborators cannot update projects.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Invalidate cache for updated project and user project list
        cache.delete(f'project_{self.object.pk}')
        cache.delete(f'user_projects_{self.request.user.id}')
        return response

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and getattr(request.user, 'role', None) == 'collab':
            return HttpResponseForbidden("Collaborators cannot delete projects.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project_id = project.pk
        response = super().delete(request, *args, **kwargs)
        # Invalidate cache for deleted project and user project list
        cache.delete(f'project_{project_id}')
        cache.delete(f'user_projects_{request.user.id}')
        return response


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'assigned_to', 'deadline', 'priority', 'status']
    template_name = 'projects/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        if request.user.role == 'collab':
            messages.warning(request, "Collaborators are not allowed to create tasks.")
            return redirect('task_list', project_id=self.project.id)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter assigned_to queryset to project members only
        form.fields['assigned_to'].queryset = self.project.members.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        form.instance.project = self.project
        response = super().form_valid(form)
        # Send task assignment email asynchronously via Celery
        assigned_user = form.instance.assigned_to
        user_email = assigned_user.email
        task_title = form.instance.title
        send_task_assignment_email.delay(user_email, task_title)

        # Invalidate task list cache for this project
        cache.delete(f'tasks_project_{self.project.id}')
        return response

    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'project_id': self.project.id})


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'assigned_to', 'deadline', 'priority', 'status']
    template_name = 'projects/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.task = self.get_object()
        self.project = self.task.project
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter assigned_to queryset to project members only
        form.fields['assigned_to'].queryset = self.project.members.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Invalidate cache for this project's tasks
        cache.delete(f'tasks_project_{self.project.id}')
        return response

    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'project_id': self.project.id})


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'projects/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        cache_key = f'tasks_project_{project_id}'
        tasks = cache.get(cache_key)
        if not tasks:
            tasks = Task.objects.filter(project__id=project_id).select_related('assigned_to', 'project').all()
            cache.set(cache_key, tasks, 300)  # Cache for 5 minutes
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('project_id'))
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'projects/task_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'collab':
            return HttpResponseForbidden("Collaborators cannot delete tasks.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        project_id = self.get_object().project.id
        response = super().delete(request, *args, **kwargs)
        # Invalidate task list cache for this project
        cache.delete(f'tasks_project_{project_id}')
        return response

    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'project_id': self.object.project.id})
