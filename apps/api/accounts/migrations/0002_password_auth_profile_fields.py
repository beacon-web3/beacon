import django.contrib.auth.validators
import django.utils.timezone
from django.contrib.auth.hashers import make_password
from django.db import migrations, models


def backfill_auth_fields(apps, schema_editor):
    account_model = apps.get_model("accounts", "Account")

    for account in account_model.objects.all():
        local_part = account.email.split("@", 1)[0] if account.email else "user"
        username = f"{local_part}-{account.pk}"
        account.username = username[:150]
        account.display_name = local_part[:150]
        account.last_login = account.last_login_at
        account.password = make_password(None)
        account.save(
            update_fields=["username", "display_name", "last_login", "password"]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="password",
            field=models.CharField(max_length=128, verbose_name="password", default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="account",
            name="last_login",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="last login"
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="is_superuser",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Designates that this user has all permissions without "
                    "explicitly assigning them."
                ),
                verbose_name="superuser status",
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="username",
            field=models.CharField(
                blank=True,
                error_messages={
                    "unique": "A user with that username already exists.",
                },
                help_text=(
                    "Required. 150 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."
                ),
                max_length=150,
                null=True,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="last name"
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="is_staff",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the user can log into this admin site.",
                verbose_name="staff status",
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Designates whether this user should be treated as active. "
                    "Unselect this instead of deleting accounts."
                ),
                verbose_name="active",
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="date_joined",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="date joined"
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="display_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="account",
            name="wallet_address",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="reputation_score",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="account",
            name="account_credit",
            field=models.DecimalField(decimal_places=9, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name="account",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "The groups this user belongs to. A user will get all "
                    "permissions granted to each of their groups."
                ),
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="account",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.RunPython(backfill_auth_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="account",
            name="username",
            field=models.CharField(
                error_messages={
                    "unique": "A user with that username already exists.",
                },
                help_text=(
                    "Required. 150 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."
                ),
                max_length=150,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
        migrations.AlterField(
            model_name="account",
            name="display_name",
            field=models.CharField(max_length=150),
        ),
        migrations.RemoveField(model_name="account", name="last_login_at"),
    ]
