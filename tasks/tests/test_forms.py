from tasks.forms import TaskForm
from tasks.models import Task


def test_title_is_required():
    form = TaskForm(data={'energy': 'light'})
    assert not form.is_valid()
    assert 'title' in form.errors


def test_whitespace_only_title_rejected_with_portuguese_message():
    form = TaskForm(data={'title': '   ', 'energy': 'light'})
    assert not form.is_valid()
    assert 'Dê um título' in form.errors['title'][0]


def test_title_is_stripped():
    form = TaskForm(data={'title': '  Pagar conta  ', 'energy': 'light'})
    assert form.is_valid()
    assert form.cleaned_data['title'] == 'Pagar conta'


def test_title_longer_than_120_rejected():
    form = TaskForm(data={'title': 'a' * 121, 'energy': 'light'})
    assert not form.is_valid()
    assert 'title' in form.errors


def test_title_of_120_accepted():
    assert TaskForm(data={'title': 'a' * 120, 'energy': 'light'}).is_valid()


def test_missing_energy_defaults_to_medium():
    form = TaskForm(data={'title': 'Ler'})
    assert form.is_valid()
    assert form.cleaned_data['energy'] == Task.Energy.MEDIUM


def test_invalid_energy_rejected():
    form = TaskForm(data={'title': 'Ler', 'energy': 'enorme'})
    assert not form.is_valid()
    assert 'energy' in form.errors
