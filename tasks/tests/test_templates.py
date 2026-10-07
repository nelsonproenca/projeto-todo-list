import pytest
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.template import engines
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse

from tasks.tests.factories import LaterTaskFactory, TaskFactory

pytestmark = pytest.mark.django_db

HOME_CANSADO = reverse('tasks:home') + '?cansado=1'


def _render(source, **context):
    return engines['django'].from_string(source).render(context)


class TestBase:
    def test_renders_nav_links(self):
        html = render_to_string('tasks/base.html')
        assert 'href="/"' in html
        assert 'href="/depois/"' in html

    def test_child_can_blank_the_nav(self):
        html = _render(
            '{% extends "tasks/base.html" %}{% block nav %}{% endblock %}'
            '{% block content %}conteudo{% endblock %}'
        )
        assert 'conteudo' in html
        assert 'Para depois' not in html

    def test_shows_framework_messages(self):
        request = RequestFactory().get('/')
        request.session = {}
        request._messages = FallbackStorage(request)
        messages.info(request, 'Tudo certo!')
        html = render_to_string('tasks/base.html', request=request)
        assert 'Tudo certo!' in html


class TestHomeTemplate:
    def test_shows_tasks_form_and_actions(self, client):
        task = TaskFactory(title='Estudar Django')
        html = client.get(reverse('tasks:home')).content.decode()
        assert 'Estudar Django' in html
        assert 'name="title"' in html
        assert 'name="energy"' in html
        for name in ('task_complete', 'task_move', 'task_delete', 'edit'):
            assert reverse(f'tasks:{name}', args=[task.pk]) in html
        assert 'csrfmiddlewaretoken' in html

    def test_empty_state(self, client):
        html = client.get(reverse('tasks:home')).content.decode()
        assert 'Nada para hoje' in html

    def test_full_day_panel(self, client):
        tasks = [TaskFactory() for _ in range(3)]
        html = client.post(
            reverse('tasks:task_create'), {'title': 'Quarta', 'energy': 'heavy'}
        ).content.decode()
        assert 'Seu dia está cheio' in html
        assert 'Guardar para depois' in html
        assert html.count('Concluir e adicionar') == 3
        assert 'name="novo_title" value="Quarta"' in html
        assert 'name="novo_energy" value="heavy"' in html
        assert reverse('tasks:task_complete', args=[tasks[0].pk]) in html


class TestLaterTemplate:
    def test_lists_tasks_with_bring_back_action(self, client):
        task = LaterTaskFactory(title='Algum dia')
        html = client.get(reverse('tasks:later')).content.decode()
        assert 'Algum dia' in html
        assert 'Trazer para o dia' in html
        assert reverse('tasks:task_move', args=[task.pk]) in html
        assert 'csrfmiddlewaretoken' in html

    def test_empty_state(self, client):
        assert 'Nada guardado' in client.get(reverse('tasks:later')).content.decode()


class TestFocusTemplate:
    def test_only_task_timer_and_controls(self, client, clock):
        task = TaskFactory(title='Escrever capítulo', focus_seconds=65)
        html = client.get(reverse('tasks:focus', args=[task.pk])).content.decode()
        assert 'Escrever capítulo' in html
        assert 'data-elapsed="65"' in html
        assert 'Concluir' in html
        assert 'Sair do foco' in html
        assert reverse('tasks:focus_complete', args=[task.pk]) in html
        assert reverse('tasks:focus_leave', args=[task.pk]) in html
        assert 'csrfmiddlewaretoken' in html

    def test_has_no_navigation_or_new_task_form(self, client, clock):
        task = TaskFactory()
        html = client.get(reverse('tasks:focus', args=[task.pk])).content.decode()
        assert 'Para depois' not in html
        assert 'href="/depois/"' not in html
        assert 'name="title"' not in html

    def test_home_shows_focus_button_per_task(self, client):
        task = TaskFactory()
        html = client.get(reverse('tasks:home')).content.decode()
        assert 'Fazer agora' in html
        assert reverse('tasks:focus', args=[task.pk]) in html


class TestEnergyTemplate:
    @pytest.mark.parametrize(
        'energy,label', [('light', 'Leve'), ('medium', 'Média'), ('heavy', 'Pesada')]
    )
    def test_task_shows_badge_with_text_label(self, client, energy, label):
        TaskFactory(energy=energy)
        html = client.get(reverse('tasks:home')).content.decode()
        assert f'class="badge energy-{energy}"' in html
        assert f'>{label}</span>' in html

    def test_later_tasks_show_badge(self, client):
        LaterTaskFactory(energy='heavy')
        html = client.get(reverse('tasks:later')).content.decode()
        assert 'class="badge energy-heavy"' in html

    def test_toggle_off_links_to_filter_on(self, client):
        html = client.get(reverse('tasks:home')).content.decode()
        assert 'Estou cansado' in html
        assert 'aria-pressed="false"' in html
        assert 'href="/?cansado=1"' in html

    def test_toggle_on_links_back_to_plain_home(self, client):
        html = client.get(HOME_CANSADO).content.decode()
        assert 'aria-pressed="true" href="/"' in html

    def test_notice_when_no_light_tasks(self, client):
        TaskFactory(energy='heavy')
        html = client.get(HOME_CANSADO).content.decode()
        assert 'Não há tarefas leves' in html
        assert 'Desativar o filtro' in html

    def test_no_notice_when_light_tasks_exist(self, client):
        TaskFactory(energy='light')
        assert 'Não há tarefas leves' not in client.get(HOME_CANSADO).content.decode()

    def test_forms_carry_hidden_filter_field_only_when_active(self, client):
        TaskFactory(energy='light')
        on = client.get(HOME_CANSADO).content.decode()
        off = client.get(reverse('tasks:home')).content.decode()
        assert 'name="cansado" value="1"' in on
        assert 'name="cansado"' not in off

    def test_focus_page_forms_and_links_carry_filter(self, client, clock):
        task = TaskFactory(energy='light')
        html = client.get(reverse('tasks:focus', args=[task.pk]) + '?cansado=1').content.decode()
        assert html.count('name="cansado" value="1"') == 2

    def test_focus_button_link_carries_filter(self, client):
        task = TaskFactory(energy='light')
        html = client.get(HOME_CANSADO).content.decode()
        assert reverse('tasks:focus', args=[task.pk]) + '?cansado=1' in html


class TestEditTemplate:
    def test_shows_form_and_portuguese_errors(self, client):
        task = TaskFactory(title='Velha')
        html = client.get(reverse('tasks:edit', args=[task.pk])).content.decode()
        assert 'value="Velha"' in html
        html = client.post(
            reverse('tasks:task_update', args=[task.pk]), {'title': ' ', 'energy': 'light'}
        ).content.decode()
        assert 'Dê um título' in html
