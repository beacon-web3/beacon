from django.contrib.admin.sites import AdminSite

from accounts.admin import AccountAdmin
from accounts.models import Account


def test_account_admin_create_form_includes_required_profile_fields():
    admin = AccountAdmin(Account, AdminSite())
    add_fieldsets = dict(admin.add_fieldsets)

    assert add_fieldsets["Beacon profile"]["fields"] == ("email", "display_name")
