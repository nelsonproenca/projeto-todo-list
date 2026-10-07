"""Business rules for tasks.

Every write that can put a task in the day goes through this module, so the
DAY_LIMIT rule cannot be bypassed by any view.
"""
from django.db import transaction
from django.utils import timezone

from .models import Task

DAY_LIMIT = 3

DESTINATIONS = {
    'today': Task.Status.TODAY,
    'later': Task.Status.LATER,
}


class DayFullError(Exception):
    """The day already has DAY_LIMIT pending tasks."""


def day_tasks(only_light=False):
    tasks = Task.objects.filter(status=Task.Status.TODAY)
    if only_light:
        tasks = tasks.filter(energy=Task.Energy.LIGHT)
    return tasks


def has_pending(only_light=False):
    return day_tasks(only_light=only_light).exists()


def _stop_focus(task):
    """Fold a running focus session into focus_seconds (caller saves)."""
    if task.focus_started_at is not None:
        running = (timezone.now() - task.focus_started_at).total_seconds()
        task.focus_seconds += max(0, int(running))
        task.focus_started_at = None


def _clean_title(title):
    title = (title or '').strip()
    if not title:
        raise ValueError('Dê um título para a tarefa.')
    return title


def _destination(destination):
    try:
        return DESTINATIONS[destination]
    except KeyError:
        raise ValueError(f'Destino desconhecido: {destination!r}') from None


def _ensure_room_today(exclude_pk=None):
    pending = Task.objects.select_for_update().filter(status=Task.Status.TODAY)
    if exclude_pk is not None:
        pending = pending.exclude(pk=exclude_pk)
    if len(list(pending.values_list('pk', flat=True))) >= DAY_LIMIT:
        raise DayFullError


def create_task(title, energy, destination):
    title = _clean_title(title)
    status = _destination(destination)
    with transaction.atomic():
        if status == Task.Status.TODAY:
            _ensure_room_today()
        return Task.objects.create(title=title, energy=energy, status=status)


def move_task(task, to):
    status = _destination(to)
    with transaction.atomic():
        if status == Task.Status.TODAY:
            _ensure_room_today(exclude_pk=task.pk)
        _stop_focus(task)
        task.status = status
        task.save(update_fields=['status', 'focus_seconds', 'focus_started_at'])
    return task


def complete_task(task, new_title=None, new_energy=None):
    """Complete a task; optionally add a new one to the day in the same transaction."""
    new_task = None
    with transaction.atomic():
        if new_title is not None:
            new_title = _clean_title(new_title)
        _stop_focus(task)
        task.status = Task.Status.DONE
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at', 'focus_seconds', 'focus_started_at'])
        if new_title is not None:
            _ensure_room_today()
            new_task = Task.objects.create(
                title=new_title,
                energy=new_energy or Task.Energy.MEDIUM,
                status=Task.Status.TODAY,
            )
    return new_task


def update_task(task, title, energy):
    task.title = _clean_title(title)
    task.energy = energy
    task.save(update_fields=['title', 'energy'])
    return task


def delete_task(task):
    task.delete()


def start_focus(task):
    """Put a task in focus; any other task in focus is stopped first."""
    with transaction.atomic():
        others = Task.objects.filter(focus_started_at__isnull=False).exclude(pk=task.pk)
        for other in others:
            _stop_focus(other)
            other.save(update_fields=['focus_seconds', 'focus_started_at'])
        if task.focus_started_at is None:
            task.focus_started_at = timezone.now()
            task.save(update_fields=['focus_started_at'])
    return task


def leave_focus(task):
    _stop_focus(task)
    task.save(update_fields=['focus_seconds', 'focus_started_at'])
    return task


def elapsed_seconds(task):
    elapsed = task.focus_seconds
    if task.focus_started_at is not None:
        elapsed += max(0, int((timezone.now() - task.focus_started_at).total_seconds()))
    return elapsed


def next_task(only_light=False):
    """Oldest pending task of the day (optionally only light ones)."""
    return day_tasks(only_light=only_light).first()
