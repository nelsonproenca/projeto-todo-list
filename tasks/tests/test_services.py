import pytest

from tasks import services
from tasks.models import Task
from tasks.tests.factories import DoneTaskFactory, LaterTaskFactory, TaskFactory

pytestmark = pytest.mark.django_db


def fill_day(n=3):
    return [TaskFactory() for _ in range(n)]


class TestDayLimit:
    def test_three_tasks_can_be_created_today(self):
        for i in range(3):
            services.create_task(f't{i}', 'light', 'today')
        assert services.day_tasks().count() == 3

    def test_fourth_task_raises_and_creates_nothing(self):
        fill_day()
        with pytest.raises(services.DayFullError):
            services.create_task('quarta', 'light', 'today')
        assert Task.objects.count() == 3
        assert not Task.objects.filter(title='quarta').exists()

    def test_create_later_works_with_full_day(self):
        fill_day()
        task = services.create_task('depois', 'heavy', 'later')
        assert task.status == Task.Status.LATER
        assert services.day_tasks().count() == 3

    def test_move_later_to_today_with_full_day_raises(self):
        fill_day()
        later = LaterTaskFactory()
        with pytest.raises(services.DayFullError):
            services.move_task(later, 'today')
        later.refresh_from_db()
        assert later.status == Task.Status.LATER

    def test_move_later_to_today_with_room_works(self):
        fill_day(2)
        later = LaterTaskFactory()
        services.move_task(later, 'today')
        later.refresh_from_db()
        assert later.status == Task.Status.TODAY

    def test_move_today_to_later_frees_a_slot(self):
        tasks = fill_day()
        services.move_task(tasks[0], 'later')
        services.create_task('nova', 'light', 'today')
        assert services.day_tasks().count() == 3

    def test_done_tasks_do_not_take_a_slot(self):
        DoneTaskFactory()
        DoneTaskFactory()
        fill_day(3)
        assert services.day_tasks().count() == 3


class TestCreate:
    def test_blank_title_rejected(self):
        with pytest.raises(ValueError):
            services.create_task('   ', 'light', 'today')

    def test_title_is_stripped(self):
        assert services.create_task('  ok  ', 'light', 'today').title == 'ok'

    def test_unknown_destination_rejected(self):
        with pytest.raises(ValueError):
            services.create_task('x', 'light', 'nowhere')


class TestComplete:
    def test_complete_sets_done_and_completed_at(self):
        task = TaskFactory()
        services.complete_task(task)
        task.refresh_from_db()
        assert task.status == Task.Status.DONE
        assert task.completed_at is not None

    def test_complete_frees_a_slot(self):
        tasks = fill_day()
        services.complete_task(tasks[0])
        services.create_task('nova', 'light', 'today')
        assert services.day_tasks().count() == 3

    def test_complete_and_add_creates_new_today_task(self):
        tasks = fill_day()
        new = services.complete_task(tasks[0], new_title='quarta', new_energy='heavy')
        assert new.title == 'quarta'
        assert new.energy == Task.Energy.HEAVY
        assert new.status == Task.Status.TODAY
        assert services.day_tasks().count() == 3

    def test_complete_and_add_is_atomic(self):
        tasks = fill_day()
        with pytest.raises(ValueError):
            services.complete_task(tasks[0], new_title='   ', new_energy='light')
        tasks[0].refresh_from_db()
        assert tasks[0].status == Task.Status.TODAY


class TestUpdateDelete:
    def test_update_changes_title_and_energy(self):
        task = TaskFactory()
        services.update_task(task, 'Novo', 'heavy')
        task.refresh_from_db()
        assert (task.title, task.energy) == ('Novo', Task.Energy.HEAVY)

    def test_update_blank_title_rejected(self):
        task = TaskFactory()
        with pytest.raises(ValueError):
            services.update_task(task, ' ', 'light')

    def test_delete_removes_task(self):
        task = TaskFactory()
        services.delete_task(task)
        assert not Task.objects.filter(pk=task.pk).exists()


class TestFocus:
    def test_start_focus_marks_start(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        task.refresh_from_db()
        assert task.focus_started_at == clock.now()

    def test_start_focus_again_does_not_restart_the_clock(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        clock.advance(30)
        services.start_focus(task)
        task.refresh_from_db()
        assert services.elapsed_seconds(task) == 30

    def test_starting_another_task_stops_the_previous_one(self, clock):
        first, second = TaskFactory(), TaskFactory()
        services.start_focus(first)
        clock.advance(45)
        services.start_focus(second)
        first.refresh_from_db()
        assert first.focus_started_at is None
        assert first.focus_seconds == 45
        second.refresh_from_db()
        assert second.focus_started_at is not None

    def test_leave_focus_accumulates_and_clears(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        clock.advance(90)
        services.leave_focus(task)
        task.refresh_from_db()
        assert task.focus_seconds == 90
        assert task.focus_started_at is None
        assert task.status == Task.Status.TODAY

    def test_elapsed_is_accumulated_plus_running(self, clock):
        task = TaskFactory(focus_seconds=100)
        services.start_focus(task)
        clock.advance(20)
        assert services.elapsed_seconds(task) == 120

    def test_elapsed_without_focus_is_accumulated_only(self):
        assert services.elapsed_seconds(TaskFactory(focus_seconds=7)) == 7

    def test_resuming_focus_keeps_accumulated_time(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        clock.advance(10)
        services.leave_focus(task)
        services.start_focus(task)
        clock.advance(5)
        assert services.elapsed_seconds(task) == 15

    def test_complete_in_focus_accumulates_time(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        clock.advance(60)
        services.complete_task(task)
        task.refresh_from_db()
        assert task.focus_seconds == 60
        assert task.focus_started_at is None
        assert task.status == Task.Status.DONE

    def test_moving_to_later_ends_focus(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        clock.advance(12)
        services.move_task(task, 'later')
        task.refresh_from_db()
        assert task.focus_started_at is None
        assert task.focus_seconds == 12

    def test_deleting_does_not_fail_in_focus(self, clock):
        task = TaskFactory()
        services.start_focus(task)
        services.delete_task(task)
        assert not Task.objects.exists()

    def test_next_task_is_oldest_pending_of_the_day(self):
        first, second = TaskFactory(), TaskFactory()
        assert services.next_task() == first
        services.complete_task(first)
        assert services.next_task() == second

    def test_next_task_ignores_later_and_done(self):
        LaterTaskFactory()
        DoneTaskFactory()
        assert services.next_task() is None


class TestEnergyFilter:
    def test_day_tasks_only_light(self):
        light = TaskFactory(energy='light')
        TaskFactory(energy='medium')
        TaskFactory(energy='heavy')
        assert list(services.day_tasks(only_light=True)) == [light]
        assert services.day_tasks().count() == 3

    def test_next_task_only_light_skips_other_levels(self):
        TaskFactory(energy='heavy')
        TaskFactory(energy='medium')
        light = TaskFactory(energy='light')
        assert services.next_task(only_light=True) == light

    def test_next_task_only_light_is_none_without_light_tasks(self):
        TaskFactory(energy='heavy')
        assert services.next_task(only_light=True) is None
        assert services.next_task() is not None

    def test_has_pending(self):
        assert not services.has_pending()
        TaskFactory(energy='heavy')
        assert services.has_pending()
        assert not services.has_pending(only_light=True)
