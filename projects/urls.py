from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView,TaskDetailView,TaskListCreateView,TaskCreateView,TaskListView,ProjectCreateView,ProjectListView,TaskUpdateView,TaskDeleteView,ProjectDeleteView,ProjectUpdateView
urlpatterns = [
    path('api/projects/',ProjectListCreateView.as_view(),name='project-list-create'),
    path('api/projects/<int:pk>/',ProjectDetailView.as_view(),name='project-detail'),
    path('api/tasks/',TaskListCreateView.as_view(),name='task-list-create'),
    path('api/tasks/<int:pk>/',TaskDetailView.as_view(),name='task-detail'),

#for templates
    path('',ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/',ProjectDetailView.as_view(), name='project_detail'),
    path('create/',ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    path('<int:project_id>/tasks/',TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/',TaskDetailView.as_view(), name='task_detail'),
    path('<int:project_id>/tasks/create/',TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
]


#if registered as collab they can only view all no post