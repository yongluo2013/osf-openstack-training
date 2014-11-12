from django.utils.translation import ugettext_lazy as _

from horizon import tables


class DocumentsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    size = tables.Column("size", verbose_name=_("Size"))

    class Meta:
        name = "documents"
        verbose_name = _("Documents")