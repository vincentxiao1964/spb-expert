from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_customuser_login_email'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='channelevent',
            new_name='users_chann_event_t_0315f0_idx',
            old_name='users_chann_event_t_8a6a8e_idx',
        ),
        migrations.AlterField(
            model_name='channelevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
