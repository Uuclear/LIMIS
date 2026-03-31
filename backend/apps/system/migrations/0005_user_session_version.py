from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_idempotencyrecord_auditlog_idempotency_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='session_version',
            field=models.PositiveIntegerField(default=0, verbose_name='会话版本'),
        ),
    ]
