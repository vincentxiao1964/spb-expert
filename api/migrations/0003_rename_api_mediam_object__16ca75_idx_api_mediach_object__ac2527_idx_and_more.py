from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_moderationrule'),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
