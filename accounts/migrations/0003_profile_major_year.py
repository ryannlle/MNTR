# Generated migration to add major and year fields to Profile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_mentor_class_codes"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="major",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="profile",
            name="year",
            field=models.CharField(blank=True, default="", max_length=20, choices=[('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior'), ('Master', 'Master'), ('PhD', 'PhD'), ('Other', 'Other')]),
        ),
    ]
