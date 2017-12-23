import re
from string import punctuation
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class UppercaseCharacterPasswortValidator(object):
    def __init__(self, min_occurrence=1):
        self.min_occurrence = min_occurrence

    def validate(self, password, user=None):
        count = 0
        for c in password:
            if c.isupper():
                count += 1
                if count >= self.min_occurrence:
                    return # Stop the look because our condition has been met!

        if self.min_occurrence == 1:
            raise ValidationError(_("Password must contain at least a single uppercase character."))
        else:
            raise ValidationError(_("Password must contain as least %(min_occurrence)s uppercase characters.") % {
                'min_occurrence': self.min_occurrence
            })

    def get_help_text(self):
        return "Validator enforces that the password contain uppercase character(s)."


class SpecialCharacterPasswortValidator(object):
    def __init__(self, min_occurrence=1):
        self.min_occurrence = min_occurrence

    def validate(self, password, user=None):
        # is_valid = re.match("^[a-zA-Z0-9_]*$", password)
        # if is_valid is not None:
        #     # If condition was not met then return validation failire.
        count = 0
        for c in password:
            if c in punctuation:
                count += 1
                if count >= self.min_occurrence:
                    return # Stop the look because our condition has been met!

        if self.min_occurrence == 1:
            raise ValidationError(_("Password must contain at least a single special character."))
        else:
            raise ValidationError(_("Password must contain as least %(min_occurrence)s special characters.") % {
                'min_occurrence': self.min_occurrence
            })

    def get_help_text(self):
        return "Validator enforces that the password character contains special character(s)."
