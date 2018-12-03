from django.db import migrations


def get_infrastructure(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    BaseInfra = apps.get_model('infrastructure', 'BaseInfrastructure')
    Infra = apps.get_model('infrastructure', 'Infrastructure')
    Signage = apps.get_model('infrastructure', 'Signage')
    for signage in BaseInfra.objects.filter(type__type='S').values():
        Signage.objects.create(**signage)
    for infra in BaseInfra.objects.exclude(type__type='S').values():
        Infra.objects.create(**infra)


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0005_auto_20181203_1101'),
    ]

    operations = [
        migrations.RunPython(get_infrastructure),
    ]
