from django.db import models
from django.db.models import Q


class Task(models.Model):
    class Energy(models.TextChoices):
        LIGHT = 'light', 'Leve'
        MEDIUM = 'medium', 'Média'
        HEAVY = 'heavy', 'Pesada'

    class Status(models.TextChoices):
        TODAY = 'today', 'Hoje'
        LATER = 'later', 'Para depois'
        DONE = 'done', 'Concluída'

    title = models.CharField(max_length=120)
    energy = models.CharField(max_length=6, choices=Energy.choices, default=Energy.MEDIUM)
    status = models.CharField(max_length=5, choices=Status.choices, default=Status.TODAY)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    focus_seconds = models.PositiveIntegerField(default=0)
    focus_started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at', 'pk']
        constraints = [
            models.CheckConstraint(
                condition=Q(focus_seconds__gte=0),
                name='task_focus_seconds_non_negative',
            ),
            models.CheckConstraint(
                condition=(
                    Q(status='done', completed_at__isnull=False)
                    | (~Q(status='done') & Q(completed_at__isnull=True))
                ),
                name='task_completed_at_iff_done',
            ),
        ]

    def __str__(self):
        return self.title
