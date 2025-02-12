from django.forms import DateField
from django.utils.translation import gettext_lazy as _
from hierarkey.forms import HierarkeyForm
from i18nfield.forms import I18nFormMixin
from pretalx.common.forms.widgets import HtmlDateInput


class HalfnarpSettingsForm(I18nFormMixin, HierarkeyForm):
    halfnarp_allow_voting_until = DateField(
        help_text=_(
            "Voting closes at midnight at the selected day. If unset, "
            "voting is allowed until a schedule is released."
        ),
        label=_("Allow votes until"),
        required=False,
        widget=HtmlDateInput,
    )
