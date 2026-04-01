from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_witness_id_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sampler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='删除时间')),
                ('name', models.CharField(max_length=50, verbose_name='取样人姓名')),
                ('id_type', models.CharField(choices=[('id_card', '居民身份证'), ('passport', '护照'), ('hk_macao', '港澳居民来往内地通行证'), ('taiwan', '台湾居民来往大陆通行证'), ('other', '其他')], default='id_card', max_length=20, verbose_name='证件类型')),
                ('id_number', models.CharField(blank=True, max_length=50, verbose_name='证件号')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='联系电话')),
                ('certificate_no', models.CharField(blank=True, max_length=100, verbose_name='取样员证书号')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否在岗')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to='system.user', verbose_name='创建人')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.organization', verbose_name='所属单位')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samplers', to='projects.project', verbose_name='所属项目')),
            ],
            options={
                'verbose_name': '取样人',
                'verbose_name_plural': '取样人',
                'ordering': ['-created_at'],
            },
        ),
    ]

