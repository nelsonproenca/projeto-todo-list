from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from . import services
from .forms import TaskForm
from .models import Task

DESTINATION_MAP = {'hoje': 'today', 'depois': 'later'}

FULL_DAY_MESSAGE = (
    'Seu dia está cheio (3 tarefas). Conclua ou guarde uma para depois antes de trazer outra.'
)
DAY_DONE_MESSAGE = 'Dia concluído! Nada mais pendente por hoje.'
LIGHT_DONE_MESSAGE = 'Acabaram as tarefas leves de hoje. Desative o filtro para ver as outras.'


def _cansado(request):
    """The "Estou cansado" filter: querystring on GET, hidden field on POST."""
    value = request.POST.get('cansado') or request.GET.get('cansado')
    return value == '1'


def _url(request, name, *args):
    url = reverse(f'tasks:{name}', args=args)
    return f'{url}?cansado=1' if _cansado(request) else url


def _go(request, name, *args):
    return redirect(_url(request, name, *args))


def _render_home(request, form=None, overflow=None):
    cansado = _cansado(request)
    if overflow:
        tasks = services.day_tasks()  # the panel needs all 3 tasks, whatever the filter
    else:
        tasks = services.day_tasks(only_light=cansado)
    context = {
        'tasks': tasks,
        'form': form or TaskForm(),
        'overflow': overflow,
        'cansado': cansado,
        'no_light_tasks': bool(cansado and not overflow and not tasks.exists()),
    }
    return render(request, 'tasks/home.html', context)


def home(request):
    return _render_home(request)


def later(request):
    cansado = _cansado(request)
    tasks = Task.objects.filter(status=Task.Status.LATER)
    if cansado:
        tasks = tasks.filter(energy=Task.Energy.LIGHT)
    return render(request, 'tasks/later.html', {'tasks': tasks, 'cansado': cansado})


@require_POST
def task_create(request):
    form = TaskForm(request.POST)
    if not form.is_valid():
        return _render_home(request, form=form)
    title = form.cleaned_data['title']
    energy = form.cleaned_data['energy']
    destination = DESTINATION_MAP.get(request.POST.get('destino', 'hoje'), 'today')
    try:
        services.create_task(title, energy, destination)
    except services.DayFullError:
        return _render_home(request, overflow={'title': title, 'energy': energy})
    return _go(request, 'home')


@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_title = (request.POST.get('novo_title') or '').strip() or None
    new_energy = request.POST.get('novo_energy') or None
    services.complete_task(task, new_title=new_title, new_energy=new_energy)
    return _go(request, 'home')


@require_POST
def task_move(request, pk):
    task = get_object_or_404(Task, pk=pk)
    destination = DESTINATION_MAP.get(request.POST.get('para'))
    if destination is None:
        return _go(request, 'home')
    try:
        services.move_task(task, destination)
    except services.DayFullError:
        messages.error(request, FULL_DAY_MESSAGE)
        return _go(request, 'later')
    return _go(request, 'later' if destination == 'today' else 'home')


@require_http_methods(['GET', 'POST'])
def edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            services.update_task(task, form.cleaned_data['title'], form.cleaned_data['energy'])
            return _go(request, 'home')
    else:
        form = TaskForm(instance=task)
    return render(
        request, 'tasks/edit.html', {'form': form, 'task': task, 'cansado': _cansado(request)}
    )


@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    services.delete_task(task)
    return _go(request, 'home')


def focus(request, pk):
    task = get_object_or_404(Task, pk=pk, status=Task.Status.TODAY)
    services.start_focus(task)
    context = {
        'task': task,
        'elapsed': services.elapsed_seconds(task),
        'cansado': _cansado(request),
    }
    return render(request, 'tasks/focus.html', context)


@require_POST
def focus_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, status=Task.Status.TODAY)
    cansado = _cansado(request)
    services.complete_task(task)
    upcoming = services.next_task(only_light=cansado)
    if upcoming is not None:
        return _go(request, 'focus', upcoming.pk)
    if cansado and services.has_pending():
        messages.info(request, LIGHT_DONE_MESSAGE)
    else:
        messages.success(request, DAY_DONE_MESSAGE)
    return _go(request, 'home')


@require_POST
def focus_leave(request, pk):
    task = get_object_or_404(Task, pk=pk, status=Task.Status.TODAY)
    services.leave_focus(task)
    return _go(request, 'home')
