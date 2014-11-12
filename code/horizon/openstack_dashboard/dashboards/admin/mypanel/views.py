# from horizon import views
# 
# 
# class IndexView(views.APIView):
#     # A very simple class-based view...
#     template_name = 'admin/mypanel/index.html'
# 
#     def get_data(self, request, context, *args, **kwargs):
#         # Add data to the context here...
#         return {"name":"hello jack"}

from horizon import tabs

from openstack_dashboard.dashboards.admin.mypanel import tabs as mydashboard_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = mydashboard_tabs.MypanelTabs
    template_name = 'admin/mypanel/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context
