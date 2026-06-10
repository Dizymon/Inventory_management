from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_name',
            field=models.CharField(default='', max_length=255, blank=True),
        ),
    ]
