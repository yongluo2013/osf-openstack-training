from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Documents(horizon.Panel):
    name = _("Documents")
    slug = "documents"


dashboard.Admin.register(Documents)
