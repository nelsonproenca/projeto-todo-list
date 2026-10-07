import factory
from django.utils import timezone

from tasks.models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f'Tarefa {n}')
    energy = Task.Energy.MEDIUM
    status = Task.Status.TODAY


class LaterTaskFactory(TaskFactory):
    status = Task.Status.LATER


class DoneTaskFactory(TaskFactory):
    status = Task.Status.DONE
    completed_at = factory.LazyFunction(timezone.now)
