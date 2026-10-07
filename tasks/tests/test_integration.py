import pytest
from django.urls import reverse

from tasks.models import Task

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def add(client, title, energy='medium', **extra):
    return client.post(reverse('tasks:task_create'), {'title': title, 'energy': energy, **extra})


def test_three_task_limit_journey(client):
    for title in ('A', 'B', 'C'):
        assert add(client, title).status_code == 302

    blocked = add(client, 'D', 'heavy')
    assert blocked.status_code == 200
    assert 'Seu dia está cheio' in blocked.content.decode()
    assert Task.objects.count() == 3

    # Guardar para depois
    add(client, 'D', 'heavy', destino='depois')
    later = client.get(reverse('tasks:later'))
    assert [t.title for t in later.context['tasks']] == ['D']
    assert Task.objects.filter(status='today').count() == 3

    # Concluir e adicionar
    first = Task.objects.get(title='A')
    client.post(
        reverse('tasks:task_complete', args=[first.pk]),
        {'novo_title': 'E', 'novo_energy': 'light'},
    )
    home = client.get(reverse('tasks:home'))
    assert sorted(t.title for t in home.context['tasks']) == ['B', 'C', 'E']
    assert Task.objects.get(title='A').status == 'done'

    # Trazer de Para depois com o dia cheio
    d = Task.objects.get(title='D')
    response = client.post(reverse('tasks:task_move', args=[d.pk]), {'para': 'hoje'}, follow=True)
    assert Task.objects.get(title='D').status == 'later'
    assert any('cheio' in str(m).lower() for m in response.context['messages'])


def test_focus_journey(client, clock):
    add(client, 'A')
    add(client, 'B')
    a, b = Task.objects.get(title='A'), Task.objects.get(title='B')

    page = client.get(reverse('tasks:focus', args=[a.pk]))
    assert page.status_code == 200
    clock.advance(75)

    # Reload keeps the elapsed time
    page = client.get(reverse('tasks:focus', args=[a.pk]))
    assert page.context['elapsed'] == 75

    response = client.post(reverse('tasks:focus_complete', args=[a.pk]))
    assert response.url == reverse('tasks:focus', args=[b.pk])
    a.refresh_from_db()
    assert a.status == 'done' and a.focus_seconds == 75

    # Leaving focus keeps the task pending
    client.get(reverse('tasks:focus', args=[b.pk]))
    clock.advance(5)
    client.post(reverse('tasks:focus_leave', args=[b.pk]))
    b.refresh_from_db()
    assert b.status == 'today' and b.focus_seconds == 5

    # Completing the last one ends the day
    client.get(reverse('tasks:focus', args=[b.pk]))
    response = client.post(reverse('tasks:focus_complete', args=[b.pk]), follow=True)
    assert response.redirect_chain[-1][0] == reverse('tasks:home')
    assert any('dia concluído' in str(m).lower() for m in response.context['messages'])


def test_tired_filter_journey(client, clock):
    add(client, 'Leve', 'light')
    add(client, 'Pesada', 'heavy')
    add(client, 'Padrao')  # no energy chosen -> medium
    assert Task.objects.get(title='Padrao').energy == 'medium'

    home = client.get(reverse('tasks:home') + '?cansado=1')
    assert [t.title for t in home.context['tasks']] == ['Leve']

    light = Task.objects.get(title='Leve')
    client.get(reverse('tasks:focus', args=[light.pk]) + '?cansado=1')
    clock.advance(30)
    response = client.post(
        reverse('tasks:focus_complete', args=[light.pk]), {'cansado': '1'}, follow=True
    )
    assert any('Acabaram as tarefas leves' in str(m) for m in response.context['messages'])
    assert response.context['no_light_tasks'] is True

    home = client.get(reverse('tasks:home'))
    assert sorted(t.title for t in home.context['tasks']) == ['Padrao', 'Pesada']
