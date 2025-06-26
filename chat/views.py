from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from projects.models import Project

@login_required(login_url='login')
def chat_room(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'chat/chat_room.html', {
        'project_id': project_id,
        'project': project,
    })
