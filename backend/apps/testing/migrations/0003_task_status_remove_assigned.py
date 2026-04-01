from django.db import migrations


def forwards(apps, schema_editor):
    TestTask = apps.get_model('testing', 'TestTask')
    TestTask.objects.filter(status='assigned').update(status='in_progress')


def backwards(apps, schema_editor):
    TestTask = apps.get_model('testing', 'TestTask')
    TestTask.objects.filter(status='in_progress').update(status='assigned')


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0002_recordtemplate_test_parameter'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

