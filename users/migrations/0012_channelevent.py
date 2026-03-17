from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_customuser_source_channel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_channel', models.CharField(blank=True, db_index=True, max_length=32, null=True, verbose_name='Source Channel')),
                ('event_type', models.CharField(choices=[('LISTING_CREATE', 'Listing Create'), ('PRIVATE_MESSAGE_SENT', 'Private Message Sent'), ('FAVORITE_ADD', 'Favorite Add')], max_length=40, verbose_name='Event Type')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_events', to='users.CustomUser')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='channelevent',
            index=models.Index(fields=['event_type', 'created_at'], name='users_chann_event_t_8a6a8e_idx'),
        ),
    ]

