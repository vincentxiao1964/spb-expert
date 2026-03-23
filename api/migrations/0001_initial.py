from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MediaCheckTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trace_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PASS', 'Pass'), ('REVIEW', 'Review'), ('RISKY', 'Risky'), ('ERROR', 'Error')], db_index=True, default='PENDING', max_length=10)),
                ('appid', models.CharField(blank=True, max_length=64, null=True)),
                ('openid', models.CharField(blank=True, max_length=128, null=True)),
                ('scene', models.IntegerField(blank=True, null=True)),
                ('media_type', models.IntegerField(blank=True, null=True)),
                ('media_url', models.URLField(blank=True, max_length=1000, null=True)),
                ('object_type', models.CharField(max_length=32)),
                ('object_id', models.IntegerField()),
                ('object_field', models.CharField(blank=True, max_length=64, null=True)),
                ('suggest', models.CharField(blank=True, max_length=16, null=True)),
                ('label', models.IntegerField(blank=True, null=True)),
                ('raw_result', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['object_type', 'object_id'], name='api_mediam_object__16ca75_idx'), models.Index(fields=['status', 'created_at'], name='api_mediam_status_17ca5f_idx')],
            },
        ),
    ]

