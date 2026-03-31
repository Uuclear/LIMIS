# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='witness',
            name='id_type',
            field=models.CharField(
                choices=[
                    ('id_card', '居民身份证'),
                    ('passport', '护照'),
                    ('hk_macao', '港澳居民来往内地通行证'),
                    ('taiwan', '台湾居民来往大陆通行证'),
                    ('other', '其他'),
                ],
                default='id_card',
                max_length=20,
                verbose_name='证件类型',
            ),
        ),
    ]
