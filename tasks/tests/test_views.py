import pytest
from django.urls import reverse

from tasks.models import Task
from tasks.tests.factories import DoneTaskFactory, LaterTaskFactory, TaskFactory

pytestmark = pytest.mark.django_db


def fill_day(n=3):
    return [TaskFactory() for _ in range(n)]


class TestHome:
    def test_ok_and_lists_day_tasks(self, client):
        task = TaskFactory(title='Estudar')
        response = client.get(reverse('tasks:home'))
        assert response.status_code == 200
        assert list(response.context['tasks']) == [task]

    def test_does_not_list_later_or_done(self, client):
        LaterTaskFactory()
        DoneTaskFactory()
        assert list(client.get(reverse('tasks:home')).context['tasks']) == []


class TestCreate:
    def test_creates_and_redirects(self, client):
        response = client.post(reverse('tasks:task_create'), {'title': 'A', 'energy': 'light'})
        assert response.status_code == 302
        assert response.url == reverse('tasks:home')
        assert Task.objects.get().title == 'A'

    def test_energy_defaults_to_medium(self, client):
        client.post(reverse('tasks:task_create'), {'title': 'A'})
        assert Task.objects.get().energy == Task.Energy.MEDIUM

    def test_fourth_task_shows_full_day_panel_and_creates_nothing(self, client):
        fill_day()
        response = client.post(reverse('tasks:task_create'), {'title': 'Quarta', 'energy': 'heavy'})
        assert response.status_code == 200
        assert response.context['overflow'] == {'title': 'Quarta', 'energy': 'heavy'}
        assert Task.objects.count() == 3

    def test_save_for_later_creates_in_later(self, client):
        fill_day()
        client.post(
            reverse('tasks:task_create'),
            {'title': 'Quarta', 'energy': 'heavy', 'destino': 'depois'},
        )
        assert Task.objects.get(title='Quarta').status == Task.Status.LATER

    def test_blank_title_shows_form_error(self, client):
        response = client.post(reverse('tasks:task_create'), {'title': '   ', 'energy': 'light'})
        assert response.status_code == 200
        assert 'title' in response.context['form'].errors
        assert Task.objects.count() == 0

    def test_get_not_allowed(self, client):
        assert client.get(reverse('tasks:task_create')).status_code == 405


class TestComplete:
    def test_completes_and_redirects(self, client):
        task = TaskFactory()
        response = client.post(reverse('tasks:task_complete', args=[task.pk]))
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == Task.Status.DONE

    def test_complete_and_add(self, client):
        tasks = fill_day()
        client.post(
            reverse('tasks:task_complete', args=[tasks[0].pk]),
            {'novo_title': 'Quarta', 'novo_energy': 'light'},
        )
        assert Task.objects.get(title='Quarta').status == Task.Status.TODAY
        assert Task.objects.filter(status=Task.Status.TODAY).count() == 3

    def test_unknown_id_404(self, client):
        assert client.post(reverse('tasks:task_complete', args=[999])).status_code == 404


class TestMove:
    def test_move_to_later(self, client):
        task = TaskFactory()
        client.post(reverse('tasks:task_move', args=[task.pk]), {'para': 'depois'})
        task.refresh_from_db()
        assert task.status == Task.Status.LATER

    def test_move_to_today_with_full_day_shows_friendly_message(self, client):
        fill_day()
        later = LaterTaskFactory()
        response = client.post(
            reverse('tasks:task_move', args=[later.pk]), {'para': 'hoje'}, follow=True
        )
        later.refresh_from_db()
        assert later.status == Task.Status.LATER
        messages = [str(m) for m in response.context['messages']]
        assert any('cheio' in m.lower() for m in messages)

    def test_move_with_unknown_destination_changes_nothing(self, client):
        task = TaskFactory()
        response = client.post(reverse('tasks:task_move', args=[task.pk]), {'para': 'lua'})
        assert response.url == reverse('tasks:home')
        task.refresh_from_db()
        assert task.status == Task.Status.TODAY

    def test_move_to_today_with_room(self, client):
        later = LaterTaskFactory()
        client.post(reverse('tasks:task_move', args=[later.pk]), {'para': 'hoje'})
        later.refresh_from_db()
        assert later.status == Task.Status.TODAY


class TestLater:
    def test_lists_later_tasks(self, client):
        task = LaterTaskFactory()
        response = client.get(reverse('tasks:later'))
        assert response.status_code == 200
        assert list(response.context['tasks']) == [task]


class TestEditDelete:
    def test_edit_get(self, client):
        task = TaskFactory()
        assert client.get(reverse('tasks:edit', args=[task.pk])).status_code == 200

    def test_edit_post_updates_and_redirects(self, client):
        task = TaskFactory()
        response = client.post(
            reverse('tasks:task_update', args=[task.pk]), {'title': 'Novo', 'energy': 'heavy'}
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert (task.title, task.energy) == ('Novo', 'heavy')

    def test_edit_post_invalid_shows_error(self, client):
        task = TaskFactory()
        response = client.post(
            reverse('tasks:task_update', args=[task.pk]), {'title': ' ', 'energy': 'heavy'}
        )
        assert response.status_code == 200
        assert 'title' in response.context['form'].errors

    def test_delete(self, client):
        task = TaskFactory()
        response = client.post(reverse('tasks:task_delete', args=[task.pk]))
        assert response.status_code == 302
        assert not Task.objects.exists()

    def test_write_routes_reject_get(self, client):
        task = TaskFactory()
        for name in ('task_complete', 'task_move', 'task_delete'):
            assert client.get(reverse(f'tasks:{name}', args=[task.pk])).status_code == 405


class TestFocus:
    def test_focus_page_ok_and_starts_focus(self, client, clock):
        task = TaskFactory()
        response = client.get(reverse('tasks:focus', args=[task.pk]))
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.focus_started_at is not None

    def test_focus_404_when_not_today(self, client):
        for factory in (LaterTaskFactory, DoneTaskFactory):
            task = factory()
            assert client.get(reverse('tasks:focus', args=[task.pk])).status_code == 404

    def test_reopening_focus_keeps_elapsed_time(self, client, clock):
        task = TaskFactory()
        client.get(reverse('tasks:focus', args=[task.pk]))
        clock.advance(120)
        response = client.get(reverse('tasks:focus', args=[task.pk]))
        assert response.context['elapsed'] == 120

    def test_complete_redirects_to_next_task_focus(self, client, clock):
        first, second = TaskFactory(), TaskFactory()
        client.get(reverse('tasks:focus', args=[first.pk]))
        clock.advance(10)
        response = client.post(reverse('tasks:focus_complete', args=[first.pk]))
        assert response.status_code == 302
        assert response.url == reverse('tasks:focus', args=[second.pk])
        first.refresh_from_db()
        assert first.status == Task.Status.DONE
        assert first.focus_seconds == 10

    def test_complete_last_goes_home_with_day_done_message(self, client):
        task = TaskFactory()
        response = client.post(reverse('tasks:focus_complete', args=[task.pk]), follow=True)
        assert response.redirect_chain[-1][0] == reverse('tasks:home')
        messages = [str(m) for m in response.context['messages']]
        assert any('dia concluído' in m.lower() for m in messages)

    def test_leave_keeps_task_pending_and_goes_home(self, client, clock):
        task = TaskFactory()
        client.get(reverse('tasks:focus', args=[task.pk]))
        clock.advance(33)
        response = client.post(reverse('tasks:focus_leave', args=[task.pk]))
        assert response.url == reverse('tasks:home')
        task.refresh_from_db()
        assert task.status == Task.Status.TODAY
        assert task.focus_seconds == 33
        assert task.focus_started_at is None

    def test_write_routes_reject_get(self, client):
        task = TaskFactory()
        for name in ('focus_complete', 'focus_leave'):
            assert client.get(reverse(f'tasks:{name}', args=[task.pk])).status_code == 405


HOME_CANSADO = reverse('tasks:home') + '?cansado=1'


class TestTiredFilter:
    def test_home_lists_only_light_tasks(self, client):
        light = TaskFactory(energy='light')
        TaskFactory(energy='medium')
        TaskFactory(energy='heavy')
        response = client.get(HOME_CANSADO)
        assert response.context['cansado'] is True
        assert list(response.context['tasks']) == [light]

    def test_home_without_filter_lists_everything(self, client):
        for energy in ('light', 'medium', 'heavy'):
            TaskFactory(energy=energy)
        response = client.get(reverse('tasks:home'))
        assert response.context['cansado'] is False
        assert len(response.context['tasks']) == 3

    def test_no_light_tasks_sets_notice(self, client):
        TaskFactory(energy='heavy')
        response = client.get(HOME_CANSADO)
        assert response.context['no_light_tasks'] is True

    def test_later_is_filtered_too(self, client):
        light = LaterTaskFactory(energy='light')
        LaterTaskFactory(energy='heavy')
        response = client.get(reverse('tasks:later') + '?cansado=1')
        assert list(response.context['tasks']) == [light]

    def test_full_day_panel_still_lists_all_three_tasks(self, client):
        for energy in ('light', 'medium', 'heavy'):
            TaskFactory(energy=energy)
        response = client.post(
            reverse('tasks:task_create'),
            {'title': 'Quarta', 'energy': 'light', 'cansado': '1'},
        )
        assert response.context['overflow'] is not None
        assert len(response.context['tasks']) == 3

    def test_focus_complete_goes_to_next_light_task(self, client):
        first = TaskFactory(energy='light')
        TaskFactory(energy='medium')
        second = TaskFactory(energy='light')
        response = client.post(
            reverse('tasks:focus_complete', args=[first.pk]), {'cansado': '1'}
        )
        assert response.url == reverse('tasks:focus', args=[second.pk]) + '?cansado=1'

    def test_last_light_with_others_pending_shows_light_done_message(self, client):
        light = TaskFactory(energy='light')
        TaskFactory(energy='heavy')
        response = client.post(
            reverse('tasks:focus_complete', args=[light.pk]), {'cansado': '1'}, follow=True
        )
        assert response.redirect_chain[-1][0] == HOME_CANSADO
        messages = [str(m) for m in response.context['messages']]
        assert any('Acabaram as tarefas leves' in m for m in messages)
        assert not any('dia concluído' in m.lower() for m in messages)

    def test_nothing_pending_shows_day_done_even_with_filter(self, client):
        light = TaskFactory(energy='light')
        response = client.post(
            reverse('tasks:focus_complete', args=[light.pk]), {'cansado': '1'}, follow=True
        )
        messages = [str(m) for m in response.context['messages']]
        assert any('dia concluído' in m.lower() for m in messages)

    def test_focus_leave_preserves_filter(self, client):
        task = TaskFactory(energy='light')
        response = client.post(reverse('tasks:focus_leave', args=[task.pk]), {'cansado': '1'})
        assert response.url == HOME_CANSADO

    @pytest.mark.parametrize('name', ['task_complete', 'task_delete'])
    def test_post_actions_preserve_filter(self, client, name):
        task = TaskFactory(energy='light')
        response = client.post(reverse(f'tasks:{name}', args=[task.pk]), {'cansado': '1'})
        assert response.url == HOME_CANSADO

    def test_move_preserves_filter(self, client):
        task = TaskFactory(energy='light')
        response = client.post(
            reverse('tasks:task_move', args=[task.pk]), {'para': 'depois', 'cansado': '1'}
        )
        assert response.url == HOME_CANSADO

    def test_create_and_edit_preserve_filter(self, client):
        response = client.post(
            reverse('tasks:task_create'), {'title': 'A', 'energy': 'light', 'cansado': '1'}
        )
        assert response.url == HOME_CANSADO
        task = Task.objects.get()
        response = client.post(
            reverse('tasks:task_update', args=[task.pk]),
            {'title': 'B', 'energy': 'light', 'cansado': '1'},
        )
        assert response.url == HOME_CANSADO

    def test_without_filter_redirects_stay_plain(self, client):
        task = TaskFactory()
        response = client.post(reverse('tasks:task_complete', args=[task.pk]))
        assert response.url == reverse('tasks:home')
