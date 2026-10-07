from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.home, name='home'),
    path('depois/', views.later, name='later'),
    path('tarefas/nova/', views.task_create, name='task_create'),
    path('tarefas/<int:pk>/concluir/', views.task_complete, name='task_complete'),
    path('tarefas/<int:pk>/mover/', views.task_move, name='task_move'),
    path('tarefas/<int:pk>/editar/', views.edit, name='edit'),
    path('tarefas/<int:pk>/editar/', views.edit, name='task_update'),
    path('tarefas/<int:pk>/excluir/', views.task_delete, name='task_delete'),
    path('foco/<int:pk>/', views.focus, name='focus'),
    path('foco/<int:pk>/concluir/', views.focus_complete, name='focus_complete'),
    path('foco/<int:pk>/sair/', views.focus_leave, name='focus_leave'),
]
