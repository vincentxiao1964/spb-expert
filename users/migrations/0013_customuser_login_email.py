from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_channelevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='login_email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Login Email'),
        ),
    ]

