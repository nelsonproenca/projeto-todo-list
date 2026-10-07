from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    energy = forms.ChoiceField(
        choices=Task.Energy.choices,
        required=False,
        initial=Task.Energy.MEDIUM,
        label='Energia',
    )

    class Meta:
        model = Task
        fields = ['title', 'energy']
        labels = {'title': 'Tarefa'}
        error_messages = {
            'title': {
                'required': 'Dê um título para a tarefa.',
                'max_length': 'O título pode ter no máximo 120 caracteres.',
            },
        }

    def clean_title(self):
        # Whitespace-only titles are already rejected as "required" by the CharField.
        return (self.cleaned_data.get('title') or '').strip()

    def clean_energy(self):
        return self.cleaned_data.get('energy') or Task.Energy.MEDIUM
