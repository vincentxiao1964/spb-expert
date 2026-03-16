from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_customuser_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='oa_openid',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='WeChat OA OpenID'),
        ),
    ]

