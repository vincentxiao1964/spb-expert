from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_merge_0009_customuser_oa_openid_0009_merge_20260310'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='source_channel',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, verbose_name='Source Channel'),
        ),
    ]

