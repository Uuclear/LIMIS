from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_sampler'),
        ('commissions', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commission',
            name='sampler',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='sampled_commissions',
                to='projects.sampler',
                verbose_name='取样人',
            ),
        ),
    ]

