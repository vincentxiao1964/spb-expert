from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(choices=[('ANY', 'Any'), ('FORUM', 'Forum'), ('PRIVATE_MESSAGE', 'Private Message'), ('LISTING', 'Listing'), ('NEWS', 'News'), ('AD', 'Ad'), ('CREW', 'Crew')], db_index=True, default='ANY', max_length=20)),
                ('rule_type', models.CharField(choices=[('WORD', 'Word'), ('REGEX', 'Regex')], default='WORD', max_length=10)),
                ('pattern', models.CharField(max_length=500)),
                ('action', models.CharField(choices=[('BLOCK', 'Block')], default='BLOCK', max_length=10)),
                ('enabled', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['enabled', 'scope'], name='api_moder_enabled_0e9c8c_idx')],
            },
        ),
    ]

