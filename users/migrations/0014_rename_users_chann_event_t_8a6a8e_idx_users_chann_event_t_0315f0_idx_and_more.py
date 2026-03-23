from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_customuser_login_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channelevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
