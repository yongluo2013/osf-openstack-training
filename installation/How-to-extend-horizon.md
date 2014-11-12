## 创建新的 Dashboard


mkdir openstack_dashboard/dashboards/mydashboard

./run_tests.sh  -N -m startdash mydashboard --target openstack_dashboard/dashboards/mydashboard



mkdir openstack_dashboard/dashboards/admin/mypanel
./run_tests.sh -N  -m startpanel mypanel --dashboard=openstack_dashboard.dashboards.admin --target=openstack_dashboard/dashboards/admin/mypanel


mkdir /opt/stack/horizon/openstack_dashboard/dashboards/admin/documents
./run_tests.sh -N  -m startpanel documents --dashboard=openstack_dashboard.dashboards.admin --target=openstack_dashboard/dashboards/admin/documents