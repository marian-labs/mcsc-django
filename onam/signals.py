from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GameResult, Department, NORMAL_POINTS, MAVELIKOPPAM_POINTS


def recompute_all_department_points():
    """
    Recompute points for every department from scratch by iterating over
    all GameResult rows. This approach is safe against edits and deletes —
    the total is always consistent with the current results in the DB.
    """
    # Reset everyone to 0
    Department.objects.all().update(points=0)

    # Walk every result that has a department assigned
    results = (
        GameResult.objects
        .filter(department__isnull=False)
        .select_related('game', 'department')
    )

    dept_totals = {}
    for result in results:
        pts = MAVELIKOPPAM_POINTS.get(result.position, 0) if result.game.is_mavelikoppam \
              else NORMAL_POINTS.get(result.position, 0)
        dept_totals[result.department_id] = dept_totals.get(result.department_id, 0) + pts

    for dept_id, total in dept_totals.items():
        Department.objects.filter(pk=dept_id).update(points=total)


@receiver(post_save, sender=GameResult)
def on_result_save(sender, instance, **kwargs):
    recompute_all_department_points()


@receiver(post_delete, sender=GameResult)
def on_result_delete(sender, instance, **kwargs):
    recompute_all_department_points()
