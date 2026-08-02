from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings


def _sync_user_staff_status(user):
    protected = getattr(settings, 'PROTECTED_ADMIN_USERNAMES', set())
    if user.is_superuser or user.username in protected or user.role == 'admin':
        return

    has_groups = user.groups.exists()
    if has_groups and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])
    elif not has_groups and user.is_staff:
        user.is_staff = False
        user.save(update_fields=['is_staff'])


@receiver(m2m_changed)
def handle_user_group_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if sender == instance.groups.through:
            _sync_user_staff_status(instance)
        elif model == instance.__class__:
            from accounts.models import User
            for user in User.objects.filter(pk__in=pk_set or []):
                _sync_user_staff_status(user)


@receiver(post_delete, sender=Group)
def handle_group_deleted(sender, instance, **kwargs):
    from accounts.models import User
    for user in User.objects.filter(is_superuser=False):
        _sync_user_staff_status(user)
