from django.db import migrations, models


def forwards(apps, schema_editor):
    UserProfile = apps.get_model('inventory', 'UserProfile')
    UserProfile.objects.filter(role='supplier').update(role='editor')
    UserProfile.objects.filter(role='user').update(role='viewer')


def backwards(apps, schema_editor):
    UserProfile = apps.get_model('inventory', 'UserProfile')
    UserProfile.objects.filter(role='editor').update(role='supplier')
    UserProfile.objects.filter(role='viewer').update(role='user')


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_add_item_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('editor', 'Editor'),
                    ('viewer', 'Viewer'),
                ],
                default='viewer',
                max_length=20,
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
