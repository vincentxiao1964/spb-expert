from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_moderationrule'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='mediachecktask',
            new_name='api_mediach_object__ac2527_idx',
            old_name='api_mediam_object__16ca75_idx',
        ),
        migrations.RenameIndex(
            model_name='mediachecktask',
            new_name='api_mediach_status_c3d3f1_idx',
            old_name='api_mediam_status_17ca5f_idx',
        ),
        migrations.RenameIndex(
            model_name='moderationrule',
            new_name='api_moderat_enabled_a08d6f_idx',
            old_name='api_moder_enabled_0e9c8c_idx',
        ),
    ]
