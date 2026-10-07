import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from tasks.models import Task
from tasks.tests.factories import TaskFactory

pytestmark = pytest.mark.django_db


def test_defaults():
    task = Task.objects.create(title='Lavar louça')
    assert task.energy == Task.Energy.MEDIUM
    assert task.status == Task.Status.TODAY
    assert task.focus_seconds == 0
    assert task.completed_at is None
    assert task.focus_started_at is None
    assert task.created_at is not None


def test_title_max_length_is_120():
    assert Task._meta.get_field('title').max_length == 120


def test_energy_choices_and_labels():
    assert dict(Task.Energy.choices) == {
        'light': 'Leve',
        'medium': 'Média',
        'heavy': 'Pesada',
    }


def test_status_choices():
    assert set(dict(Task.Status.choices)) == {'today', 'later', 'done'}


def test_str_is_title():
    assert str(TaskFactory(title='Escrever relatório')) == 'Escrever relatório'


def test_ordering_by_created_at():
    first = TaskFactory()
    second = TaskFactory()
    assert list(Task.objects.all()) == [first, second]


def test_negative_focus_seconds_rejected():
    with pytest.raises(IntegrityError), transaction.atomic():
        Task.objects.create(title='x', focus_seconds=-1)


def test_completed_at_requires_done_status():
    with pytest.raises(IntegrityError), transaction.atomic():
        Task.objects.create(title='x', status=Task.Status.TODAY, completed_at=timezone.now())


def test_done_requires_completed_at():
    with pytest.raises(IntegrityError), transaction.atomic():
        Task.objects.create(title='x', status=Task.Status.DONE)


def test_done_with_completed_at_is_valid():
    task = Task.objects.create(title='x', status=Task.Status.DONE, completed_at=timezone.now())
    assert task.pk
