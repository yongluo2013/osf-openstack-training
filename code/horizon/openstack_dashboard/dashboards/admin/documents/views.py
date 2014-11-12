from horizon import views
from horizon import tables
from openstack_dashboard.dashboards.admin.documents import tables as project_tables
# class IndexView(views.APIView):
#     # A very simple class-based view...
#     template_name = 'admin/documents/index.html'
# 
#     def get_data(self, request, context, *args, **kwargs):
#         # Add data to the context here...
#         context = {"words":"hello jack!"}
#         return context

class Document:
    def __init__(self,id,name,size):
        self.id = id
        self.name = name
        self.size = size
class IndexView(tables.DataTableView):
    table_class = project_tables.DocumentsTable
    template_name = 'admin/documents/index.html'

    def get_data(self):

        return [Document("123123","doc1",123),Document("123124","doc2",55)]
