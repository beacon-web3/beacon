from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_password_auth_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="email_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="email_verification_code_hash",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="account",
            name="email_verification_code_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="email_verification_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
