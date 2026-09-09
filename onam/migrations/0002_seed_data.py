from django.db import migrations


DEPARTMENTS = [
    'BCOM', 'BSW', 'BCA', 'BBA A', 'BBA B', 'BACE',
    'Economics', 'Mathematics', 'Physics UG', 'Physics PG',
    'MBA', 'MSW', 'MCOM', 'MCA', 'MHTM', 'MCMS', 'Psychology',
]

GAMES = [
    {'name': 'Obstacle Race',             'is_mavelikoppam': False, 'order': 1},
    {'name': 'Ishtika Pidutham',          'is_mavelikoppam': False, 'order': 2},
    {'name': 'Chakkil Ottam Relay',       'is_mavelikoppam': False, 'order': 3},
    {'name': 'Saree Draping',             'is_mavelikoppam': False, 'order': 4},
    {'name': 'Theeta Malsaram',           'is_mavelikoppam': False, 'order': 5},
    {'name': 'Sundhariku Pottu Thodal',   'is_mavelikoppam': False, 'order': 6},
    {'name': 'Mavelikoppam',              'is_mavelikoppam': True,  'order': 7},
]


def seed_data(apps, schema_editor):
    Department = apps.get_model('onam', 'Department')
    OnamGame = apps.get_model('onam', 'OnamGame')

    for dept_name in DEPARTMENTS:
        Department.objects.get_or_create(name=dept_name)

    for game in GAMES:
        OnamGame.objects.get_or_create(
            name=game['name'],
            defaults={
                'is_mavelikoppam': game['is_mavelikoppam'],
                'order': game['order'],
            }
        )


def unseed_data(apps, schema_editor):
    Department = apps.get_model('onam', 'Department')
    OnamGame = apps.get_model('onam', 'OnamGame')
    Department.objects.filter(name__in=DEPARTMENTS).delete()
    OnamGame.objects.filter(name__in=[g['name'] for g in GAMES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('onam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
