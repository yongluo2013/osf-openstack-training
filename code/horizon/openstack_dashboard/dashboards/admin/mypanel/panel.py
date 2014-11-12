from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Mypanel(horizon.Panel):
    name = _("My Panel")
    slug = "mypanel"


dashboard.Admin.register(Mypanel)
