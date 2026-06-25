import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    def validate(self, password, user=None):
        missing_requirements = []

        if len(password) <= 8:
            missing_requirements.append(_("be longer than 8 characters"))
        if not re.search(r"[a-z]", password):
            missing_requirements.append(_("include a lowercase letter"))
        if not re.search(r"[A-Z]", password):
            missing_requirements.append(_("include an uppercase letter"))
        if not re.search(r"\d", password):
            missing_requirements.append(_("include a number"))
        if not re.search(r"[^A-Za-z0-9]", password):
            missing_requirements.append(_("include a special character"))

        if missing_requirements:
            raise ValidationError(
                _("Password must %(requirements)s."),
                code="password_no_complexity",
                params={"requirements": ", ".join(missing_requirements)},
            )

    def get_help_text(self):
        return _(
            "Your password must be longer than 8 characters and include a "
            "lowercase letter, uppercase letter, number, and special character."
        )
