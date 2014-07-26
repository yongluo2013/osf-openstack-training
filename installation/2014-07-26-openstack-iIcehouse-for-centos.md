#网络设置

controller0 

     eth0:10.20.0.10   (data traffic network)
     eth1:172.16.0.10  (management network)

network0

     eth0:10.20.0.20    (data traffic network)
     eht1:172.16.0.20   (management network)
     eht1:192.168.4.20   (external network)

compute0

     eth0:10.20.0.30   (data traffic network)
     eht1:172.16.0.30  (management network)

compute1  (optional)

     eth0:10.20.0.31   (data traffic network)
     eht1:172.16.0.31   (management network)



##控制节点安装

###hostname 设置

vi /etc/sysconfig/network
HOSTNAME=controller0

###hosts 文件设置

vi /etc/hosts

127.0.0.1    localhost
::1          localhost 
172.16.0.10 controller0 
172.16.0.20 network0
172.16.0.30 compute0
172.16.0.31 compute1

###网卡配置

vi /etc/sysconfig/network-scripts/ifcfg-eth0

DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=10.20.0.10
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth1

DEVICE=eth1
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=172.16.0.10
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth2

DEVICE=eth2
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=dhcp

网络配置文件修改完后重启网络服务

serice network restart

###安装 ntp

yum install ntp -y
service ntpd start
chkconfig ntpd on

###安装mysql server

yum install mysql mysql-server MySQL-python -y

service mysqld start
chkconfig mysqld on

设置mysql 密码

mysql_secure_installation
mysql password "openstack"

###安装消息服务

本设置使qpid服务不需要认证

yum install qpid-cpp-server memcached -y

vi /etc/qpidd.conf
auth=no

重启消息服务
service qpidd start
chkconfig qpidd on

###安装openstack-utils

方便后续通过命令行直接修改配置文件
yum install openstack-utils -y


###安装keystone
yum install openstack-keystone python-keystoneclient -y

为keystone 设置admin 账户的 tokn

ADMIN_TOKEN=$(openssl rand -hex 10)
echo $ADMIN_TOKEN
openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token $ADMIN_TOKEN

配置数据连接
openstack-config --set /etc/keystone/keystone.conf sql connection mysql://keystone:openstack@controller0/keystone

设置Keystone 用 PKI tokens

keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

初始化数据库
openstack-db --init --service keystone --password openstack

启动keystone 服务
service openstack-keystone start
chkconfig openstack-keystone on

export OS_SERVICE_TOKEN=`echo $ADMIN_TOKEN`
export OS_SERVICE_ENDPOINT=http://controller0:35357/v2.0


创建管理员和系统服务使用的租户

keystone tenant-create --name=admin --description="Admin Tenant"

keystone tenant-create --name=service --description="Service Tenant"


创建管理员用户
keystone user-create --name=admin --pass=admin --email=admin@example.com


创建管理员角色
keystone role-create --name=admin


为管理员用户分配"管理员"角色

keystone user-role-add --user=admin --tenant=admin --role=admin


为keystone 服务 建立 endpoints

keystone service-create --name=keystone --type=identity --description="Keystone Identity Service"


为keystone 建立 endpoint 关联

keystone endpoint-create \
--service-id=$(keystone service-list | awk '/ identity / {print $2}') \
--publicurl=http://controller0:5000/v2.0 \
--internalurl=http://controller0:5000/v2.0 \
--adminurl=http://controller0:35357/v2.0

验证keystone 安装正确性

取消先前的认证变量
unset OS_SERVICE_TOKEN OS_SERVICE_ENDPOINT

先用命令行方式验证
keystone --os-username=admin --os-password=admin --os-auth-url=http://controller0:35357/v2.0 token-get
keystone --os-username=admin --os-password=admin --os-tenant-name=admin --os-auth-url=http://controller0:35357/v2.0 token-get

让后用设置环境变量认证
vi ~/keystonerc

export OS_USERNAME=admin
export OS_PASSWORD=admin
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://controller0:35357/v2.0

source keystonerc
keystone token-get

+++++++++++++++++++++++++Keystone 安装结束++++++++++++++++++++++++++++++++++++++++++++++++++

##安装glance 服务

yum install openstack-glance python-glanceclient -y

openstack-db --init --service glance --password openstack


创建glance 用户
keystone user-create --name=glance --pass=glance --email=glance@example.com

并分配service角色
keystone user-role-add --user=glance --tenant=service --role=admin

创建glance 服务
keystone service-create --name=glance --type=image --description="Glance Image Service"

创建keystone 的endpoint 

keystone endpoint-create \
--service-id=$(keystone service-list | awk '/ image / {print $2}')  \
--publicurl=http://controller0:9292 \
--internalurl=http://controller0:9292 \
--adminurl=http://controller0:9292

用openstack util 修改glance api 和 register 配置文件

openstack-config --set /etc/glance/glance-api.conf DEFAULT sql_connection mysql://glance:openstack@controller0/glance
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_uri http://controller0:5000
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_user glance
openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_password glance
openstack-config --set /etc/glance/glance-api.conf paste_deploy flavor keystone

openstack-config --set /etc/glance/glance-registry.conf DEFAULT sql_connection mysql://glance:openstack@controller0/glance
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_uri http://controller0:5000
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_user glance
openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_password glance
openstack-config --set /etc/glance/glance-registry.conf paste_deploy flavor keystone


启动glance 相关的两个服务
service openstack-glance-api start
service openstack-glance-registry start
chkconfig openstack-glance-api on
chkconfig openstack-glance-registry on

下载最小化镜像Cirros验证glance 安装是否成功

下载 image 文件
wget http://cdn.download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img

glance image-create --name="CirrOS 0.3.1" --disk-format=qcow2  --container-format=ovf --is-public=true < cirros-0.3.1-x86_64-disk.img

查看刚刚上传的image 是否成功

glance index

显示相应的image 信息说明安装成功

##安装nova controller 和 computer 节点

###安装nova

yum install openstack-nova-api openstack-nova-cert openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler python-novaclient

初始化数据库
openstack-db --init --service nova --password openstack

在keystone中创建nova相应的用户和服务

keystone user-create --name=nova --pass=nova --email=nova@example.com
keystone user-role-add --user=nova --tenant=service --role=admin

keystone 注册服务
keystone service-create --name=nova --type=compute --description="Nova Compute Service"

keystone 注册endpoint

keystone endpoint-create \
--service-id=$(keystone service-list | awk '/ compute / {print $2}')  \
--publicurl=http://controller0:8774/v2/%\(tenant_id\)s \
--internalurl=http://controller0:8774/v2/%\(tenant_id\)s \
--adminurl=http://controller0:8774/v2/%\(tenant_id\)s

配置nova.conf

openstack-config --set /etc/nova/nova.conf database connection mysql://nova:openstack@controller0/nova

openstack-config --set /etc/nova/nova.conf DEFAULT rpc_backend qpid
openstack-config --set /etc/nova/nova.conf DEFAULT qpid_hostname controller0

openstack-config --set /etc/nova/nova.conf DEFAULT my_ip 172.16.0.10
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_listen 172.16.0.10
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_proxyclient_address 172.16.0.10

openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_uri http://controller0:5000
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_user nova
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_password nova




启动服务

service openstack-nova-api start
service openstack-nova-cert start
service openstack-nova-consoleauth start
service openstack-nova-scheduler start
service openstack-nova-conductor start
service openstack-nova-novncproxy start
chkconfig openstack-nova-api on
chkconfig openstack-nova-cert on
chkconfig openstack-nova-consoleauth on
chkconfig openstack-nova-scheduler on
chkconfig openstack-nova-conductor on
chkconfig openstack-nova-novncproxy on

service openstack-nova-api restart
service openstack-nova-cert restart
service openstack-nova-consoleauth restart
service openstack-nova-scheduler restart
service openstack-nova-conductor restart
service openstack-nova-novncproxy restart
检查服务是否正常

nova-manage service list

root@controller0 ~]# nova-manage service list
Binary           Host                                 Zone             Status     State Updated_At
nova-consoleauth controller0                          internal         enabled    :-)   2013-11-12 11:14:56
nova-cert        controller0                          internal         enabled    :-)   2013-11-12 11:14:56
nova-scheduler   controller0                          internal         enabled    :-)   2013-11-12 11:14:56
nova-conductor   controller0                          internal         enabled    :-)   2013-11-12 11:14:56

检查进程
[root@controller0 ~]# ps -ef|grep nova
nova      7240     1  1 23:11 ?        00:00:02 /usr/bin/python /usr/bin/nova-api --logfile /var/log/nova/api.log
nova      7252     1  1 23:11 ?        00:00:01 /usr/bin/python /usr/bin/nova-cert --logfile /var/log/nova/cert.log
nova      7264     1  1 23:11 ?        00:00:01 /usr/bin/python /usr/bin/nova-consoleauth --logfile /var/log/nova/consoleauth.log
nova      7276     1  1 23:11 ?        00:00:01 /usr/bin/python /usr/bin/nova-scheduler --logfile /var/log/nova/scheduler.log
nova      7288     1  1 23:11 ?        00:00:01 /usr/bin/python /usr/bin/nova-conductor --logfile /var/log/nova/conductor.log
nova      7300     1  0 23:11 ?        00:00:00 /usr/bin/python /usr/bin/nova-novncproxy --web /usr/share/novnc/
nova      7336  7240  0 23:11 ?        00:00:00 /usr/bin/python /usr/bin/nova-api --logfile /var/log/nova/api.log
nova      7351  7240  0 23:11 ?        00:00:00 /usr/bin/python /usr/bin/nova-api --logfile /var/log/nova/api.log
nova      7352  7240  0 23:11 ?        00:00:00 /usr/bin/python /usr/bin/nova-api --logfile /var/log/nova/api.log

##配置支持neutron 

mysql -u root -p
mysql> CREATE DATABASE neutron;
mysql> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' \
IDENTIFIED BY 'NEUTRON_DBPASS';
mysql> GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' \
IDENTIFIED BY 'NEUTRON_DBPASS';


keystone user-create --name neutron --pass NEUTRON_PASS --email neutron@example.com

keystone user-role-add --user neutron --tenant service --role admin

keystone service-create --name neutron --type network --description "OpenStack Networking"

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ network / {print $2}') \
--publicurl http://controller0:9696 \
--adminurl http://controller0:9696 \
--internalurl http://controller0:9696


openstack-config --set /etc/neutron/neutron.conf database connection mysql://neutron:openstack@controller0/neutron

openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy keystone
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_uri http://controller0:5000
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user neutron
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password neutron


openstack-config --set /etc/neutron/neutron.conf DEFAULT rpc_backend neutron.openstack.common.rpc.impl_qpid
openstack-config --set /etc/neutron/neutron.conf DEFAULT qpid_hostname controller0
openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin ml2
openstack-config --set /etc/neutron/neutron.conf DEFAULT service_plugins router

openstack-config --set /etc/neutron/neutron.conf DEFAULT notify_nova_on_port_status_changes True
openstack-config --set /etc/neutron/neutron.conf DEFAULT notify_nova_on_port_data_changes True
openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_url http://controller0:8774/v2

openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_username nova
openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_tenant_id 3881e339d12b4e7f91a0843e5662167b
openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_password nova
openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_auth_url http://controller0:35357/v2.0


#ml2
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 type_drivers gre
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 tenant_network_types gre
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 mechanism_drivers openvswitch
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_gre tunnel_id_ranges 1:1000
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup firewall_driver neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_security_group True


#neutron for controller
openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class nova.network.neutronv2.api.API
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_url http://controller0:9696
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_auth_strategy keystone
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_username neutron
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_password neutron
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_auth_url http://controller0:35357/v2.0
openstack-config --set /etc/nova/nova.conf DEFAULT linuxnet_interface_driver nova.network.linux_net.LinuxOVSInterfaceDriver
openstack-config --set /etc/nova/nova.conf DEFAULT firewall_driver nova.virt.firewall.NoopFirewallDriver
openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api neutron


#neutron metadata support
openstack-config --set /etc/nova/nova.conf DEFAULT service_neutron_metadata_proxy true
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_metadata_proxy_shared_secret METADATA_SECRET

ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

service openstack-nova-api restart
service openstack-nova-scheduler restart
service openstack-nova-conductor restart
service neutron-server start
chkconfig neutron-server on

service openstack-nova-api restart
service openstack-nova-scheduler restart
service openstack-nova-conductor restart
service neutron-server restart

##安装compute 节点

网卡配置

vi /etc/sysconfig/network-scripts/ifcfg-eth0

DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=10.20.0.30
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth1

DEVICE=eth1
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=172.16.0.30
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth2

DEVICE=eth2
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=dhcp

网络配置文件修改完后重启网络服务

serice network restart

安装 ntp

yum install ntp -y
service ntpd start
chkconfig ntpd on

###配置从controller 时间同步

vi /etc/ntp.conf

server controller0
fudge  controller0 stratum 10  # LCL is unsynchronized

###检查时间同步

ntpdate -u controller0

service ntpd restart
ntpq -p

###显示如下内容表示时间同步正常
[root@compute2 ~]# ntpq -p 
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 controller0     LOCAL(0)         6 u    4   64    1    0.131    0.298   0.000
###安装mysql client

yum install mysql MySQL-python -y

###安装openstack-utils

方便后续通过命令行直接修改配置文件
yum install openstack-utils -y


##配置compute node

openstack-config --set /etc/nova/nova.conf database connection mysql://nova:openstack@controller0/nova
openstack-config --set /etc/nova/nova.conf DEFAULT rpc_backend qpid
openstack-config --set /etc/nova/nova.conf DEFAULT qpid_hostname controller0
openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone

openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_uri http://controller0:5000
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/nova/nova.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_user nova
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/nova/nova.conf keystone_authtoken admin_password nova

openstack-config --set /etc/nova/nova.conf DEFAULT my_ip 172.16.0.30
openstack-config --set /etc/nova/nova.conf DEFAULT vnc_enabled True
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_listen 0.0.0.0
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_proxyclient_address 172.16.0.30
openstack-config --set /etc/nova/nova.conf DEFAULT novncproxy_base_url http://controller0:6080/vnc_auto.html
openstack-config --set /etc/nova/nova.conf libvirt virt_type qemu


启动compute 节点服务

service libvirtd start
service messagebus start
service openstack-nova-compute start

chkconfig libvirtd on
chkconfig messagebus on
chkconfig openstack-nova-compute on

在controller 节点检查compute服务是否启动

nova-manage service list

多出计算节点服务

[root@controller0 ~]# nova-manage service list
Binary           Host                                 Zone             Status     State Updated_At
nova-consoleauth controller0                          internal         enabled    :-)   2014-07-19 09:04:18
nova-cert        controller0                          internal         enabled    :-)   2014-07-19 09:04:19
nova-conductor   controller0                          internal         enabled    :-)   2014-07-19 09:04:20
nova-scheduler   controller0                          internal         enabled    :-)   2014-07-19 09:04:20
nova-compute     compute0                             nova             enabled    :-)   2014-07-19 09:04:19


yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch



#安装网络控制节点


###hostname 设置

vi /etc/sysconfig/network
HOSTNAME=network0

###hosts 文件设置

vi /etc/hosts

127.0.0.1    localhost
::1          localhost 
172.16.0.10 controller0 
172.16.0.20 network0
172.16.0.30 compute0
172.16.0.31 compute1

###网卡配置

vi /etc/sysconfig/network-scripts/ifcfg-eth0

DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=10.20.0.20
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth1

DEVICE=eth1
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=172.16.0.20
NETMASK=255.255.255.0

vi /etc/sysconfig/network-scripts/ifcfg-eth2

DEVICE=eth2
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=dhcp

网络配置文件修改完后重启网络服务

serice network restart

###安装 ntp

yum install ntp -y
service ntpd start
chkconfig ntpd on

###配置从controller 时间同步

vi /etc/ntp.conf

server controller0
fudge  controller0 stratum 10  # LCL is unsynchronized

###检查时间同步

ntpdate -u controller0

service ntpd restart
ntpq -p

###显示如下内容表示时间同步正常
[root@compute2 ~]# ntpq -p 
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 controller0     LOCAL(0)         6 u    4   64    1    0.131    0.298   0.000
###安装mysql client

yum install mysql MySQL-python -y

###安装openstack-utils

方便后续通过命令行直接修改配置文件
yum install openstack-utils -y

###安装网络控制节点

yum install -y openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch

yum install -y openstack-neutron openstack-neutron-openvswitch dnsmasq neutron-dhcp-agent neutron-l3-agent

#开启linux 数据包转发和关闭数据包过滤功能

vi /etc/sysctl.conf
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0

#创建 neutron 数据库和分配对应权限

mysql -uroot -popenstack -e "CREATE DATABASE neutron;"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'openstack';"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'openstack';"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'controller0' IDENTIFIED BY 'openstack';"


#在keystone 中创建neutron 用户
keystone user-create --name=neutron --pass=neutron --email=neutron@example.com

#为neutron用户和租户管理
keystone user-role-add --user=neutron --tenant=service --role=admin


#添加在keystone中添加网络服务
keystone service-create --name=neutron --type=network --description="OpenStack Networking Service"


#为网络服务创建endpoint
keystone endpoint-create \
--service-id 677b07ca047a406a886db06f926bc0e0 \
--publicurl http://controller0:9696 \
--adminurl http://controller0:9696 \
--internalurl http://controller0:9696


把openvswiche plugin 配置文件link 到neutron 主目录

ln -s /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini /etc/neutron/plugin.ini

#congfiure neutron core 
openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy  keystone
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name  service
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user  neutron
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password  neutron

openstack-config --set /etc/neutron/neutron.conf database connection mysql://neutron:openstack@controller0/neutron
openstack-config --set /etc/neutron/neutron.conf AGENT root_helper "sudo neutron-rootwrap /etc/neutron/rootwrap.conf"
openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin  neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2


# configure api
openstack-config --set /etc/neutron/api-paste.ini filter:authtoken paste.filter_factory keystoneclient.middleware.auth_token:filter_factory
openstack-config --set /etc/neutron/api-paste.ini filter:authtoken auth_host controller0
openstack-config --set /etc/neutron/api-paste.ini filter:authtoken admin_user neutron
openstack-config --set /etc/neutron/api-paste.ini filter:authtoken admin_tenant_name service
openstack-config --set /etc/neutron/api-paste.ini filter:authtoken admin_password neutron

# configure openvswitch 
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini DATABASE connection  mysql://neutron:openstack@controller0/neutron
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS tenant_network_type  gre
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS tunnel_id_ranges  1:1000
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS enable_tunneling True
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS local_ip 192.168.0.10 
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini SECURITYGROUP firewall_driver neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver

# configure dhcp agent
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT interface_driver neutron.agent.linux.interface.OVSInterfaceDriver
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT dhcp_driver  neutron.agent.linux.dhcp.Dnsmasq
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT use_namespaces  True
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT root_helper "sudo neutron-rootwrap /etc/neutron/rootwrap.conf"
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT state_path /var/lib/neutron


# configure l3 agent
openstack-config --set /etc/neutron/l3_agent.ini DEFAULT interface_driver  neutron.agent.linux.interface.OVSInterfaceDriver
openstack-config --set /etc/neutron/l3_agent.ini DEFAULT use_namespaces True

# configure metadata agent 
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT auth_url  http://controller0:5000/v2.0
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT auth_region  regionOne
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_tenant_name  neutron
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_user  service
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_password  neutron
openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT nova_metadata_ip  controller0


# configure nova for neutron

openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class nova.network.neutronv2.api.API
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_username neutron
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_password neutron
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_auth_url http://controller0:35357/v2.0/
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_auth_strategy  keystone
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_url http://controller0:9696/
openstack-config --set /etc/nova/nova.conf DEFAULT libvirt_vif_driver nova.virt.libvirt.vif.LibvirtGenericVIFDriver



启动neuron 所有服务

service openvswitch start
service dnsmasq start
service neutron-server start
service neutron-l3-agent start
service neutron-metadata-agent start
service neutron-openvswitch-agent start
service neutron-ovs-cleanup start
service neutron-dhcp-agent start
service neutron-l3-agent start

#添加到系统服务
chkconfig openvswitch  on
chkconfig dnsmasq on
chkconfig neutron-server  on
chkconfig neutron-l3-agent  on
chkconfig neutron-metadata-agent on
chkconfig neutron-openvswitch-agent on
chkconfig neutron-ovs-cleanup on
chkconfig neutron-dhcp-agent on
chkconfig neutron-l3-agent on

#手动添加两个openvswitch bridge

ovs-vsctl add-br br-int
ovs-vsctl add-br br-ex


#另外修改对外的网卡配置，不能设置ip地址，一定要开启混杂模式

vi /etc/sysconfig/network-scripts/ifcfg-eth1
DEVICE=eth1
ONBOOT=yes
BOOTPROTO=none
PROMISC=yes 

vi /etc/sysconfig/network-scripts/ifcfg-br-ex

DEVICE=br-ex
TYPE=Bridge
ONBOOT=no
BOOTPROTO=none
IPADDR=10.170.65.200
NETMASK=255.255.255.0
GATEWAY=10.170.65.1

#这步要中断网络，务必要连续执行network 服务重启
ovs-vsctl add-port br-ex eth1&&service network restart





####添加一个计算节点

#内网访问外网
ssh -L3128:150.236.0.130:8080 -Nf -l eluoyng 10.170.21.4

#禁用 selinux 
vi /etc/selinux/config
SELINUX=disabled


#开启linux 数据包转发和关闭数据包过滤功能
vi /etc/sysctl.conf
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0


#删除默认的iptables 规则，允许所有包可进可出

vi /etc/sysconfig/iptables

# Firewall configuration written by system-config-firewall
# Manual customization of this file is not recommended.
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
COMMIT


service iptables restart


#安装 ntp
yum install ntp
service ntpd start
chkconfig ntpd on

# 配置从controller 时间同步

vi /etc/ntp.conf

server 192.168.0.10
fudge  192.168.0.10 stratum 10  # LCL is unsynchronized

#检查时间同步

ntpdate -u 192.168.0.10

service ntpd restart
ntpq -p
#显示如下内容表示时间同步正常
[root@compute2 ~]# ntpq -p 
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 controller0     LOCAL(0)         6 u    4   64    1    0.131    0.298   0.000

#安装mysql client

yum install -y mysql MySQL-python
yum install -y openstack-utils

#安装nova compute 软件包
yum install openstack-nova-compute


#或者一次性安装包
yum install -y ntp mysql MySQL-python openstack-utils openstack-nova-compute openstack-neutron-openvswitch


#解决版本兼容问题（可选）
yum remove openstack-nova-compute openstack-nova-common python-nova
yum install -y http://repos.fedorapeople.org/repos/openstack/openstack-havana/epel-6/python-nova-2013.2-5.el6.noarch.rpm
yum install -y http://repos.fedorapeople.org/repos/openstack/openstack-havana/epel-6/openstack-nova-common-2013.2-5.el6.noarch.rpm
yum install -y http://repos.fedorapeople.org/repos/openstack/openstack-havana/epel-6/openstack-nova-compute-2013.2-5.el6.noarch.rpm


#配置数据库
openstack-config --set /etc/nova/nova.conf database connection mysql://nova:openstack@controller0/nova

#配置keystone认证
openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone
openstack-config --set /etc/nova/nova.conf DEFAULT auth_host controller0
openstack-config --set /etc/nova/nova.conf DEFAULT admin_user nova
openstack-config --set /etc/nova/nova.conf DEFAULT admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT admin_password openstack

#配置消息服务
openstack-config --set /etc/nova/nova.conf DEFAULT rpc_backend nova.openstack.common.rpc.impl_qpid
openstack-config --set /etc/nova/nova.conf DEFAULT qpid_hostname controller0

openstack-config --set /etc/nova/nova.conf DEFAULT my_ip 192.168.0.11
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_listen 0.0.0.0
openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_proxyclient_address 192.168.0.11
openstack-config --set /etc/nova/nova.conf DEFAULT glance_host controller0

openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit True
openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api neutron
openstack-config --set /etc/nova/nova.conf DEFAULT libvirt_use_virtio_for_bridges True
openstack-config --set /etc/nova/nova.conf DEFAULT api_paste_config /etc/nova/api-paste.ini

openstack-config --set /etc/nova/nova.conf DEFAULT resume_guests_state_on_host_boot false

启动compute 节点服务

service libvirtd start
service messagebus start
service openstack-nova-compute start

chkconfig libvirtd on
chkconfig messagebus on
chkconfig openstack-nova-compute on

#到计算节点检查compute服务是否启动

nova-manage service list

#检查新增加计算节点服务

[root@controller0 ~]# nova-manage service list
Binary           Host                                 Zone             Status     State Updated_At
nova-consoleauth controller0                          internal         enabled    :-)   2013-11-17 13:28:18
nova-cert        controller0                          internal         enabled    :-)   2013-11-17 13:28:18
nova-conductor   controller0                          internal         enabled    :-)   2013-11-17 13:28:18
nova-scheduler   controller0                          internal         enabled    :-)   2013-11-17 13:28:18
nova-compute     controller0                          nova             enabled    :-)   2013-11-17 13:28:18
nova-compute     compute1                             nova             enabled    :-)   2013-11-17 13:28:20


为计算节点安装 openvswitche plugin 

yum install openstack-neutron-openvswitch

#启动openvswitch
service openvswitch start
chkconfig openvswitch on

ovs-vsctl add-br br-int

ln -s /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini /etc/neutron/plugin.ini

#congfiure neutron core 
openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy  keystone
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_port 35357
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name  service
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user  neutron
openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password  openstack

openstack-config --set /etc/neutron/neutron.conf database connection mysql://neutron:openstack@controller0/neutron
openstack-config --set /etc/neutron/neutron.conf AGENT root_helper "sudo neutron-rootwrap /etc/neutron/rootwrap.conf"
openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin  neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2

#配置消息服务
openstack-config --set /etc/neutron/neutron.conf DEFAULT qpid_hostname  controller0
openstack-config --set /etc/neutron/neutron.conf DEFAULT rpc_backend neutron.openstack.common.rpc.impl_qpid

#配置openvswitch 
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini DATABASE connection  mysql://neutron:openstack@controller0/neutron
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS tenant_network_type  gre
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS tunnel_id_ranges  1:1000
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS enable_tunneling True
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini OVS local_ip 192.168.0.11
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini SECURITYGROUP firewall_driver neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
openstack-config --set /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini SECURITYGROUP firewall_driver neutron.agent.firewall.NoopFirewallDriver

# 配置 neutron 配置nova
openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class nova.network.neutronv2.api.API
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_username neutron
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_password openstack
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_auth_url http://controller0:35357/v2.0/
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_auth_strategy  keystone
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_url http://controller0:9696/
openstack-config --set /etc/nova/nova.conf DEFAULT libvirt_vif_driver nova.virt.libvirt.vif.LibvirtGenericVIFDriver

#配置migration
openstack-config --set /etc/nova/nova.conf DEFAULT firewall_driver nova.virt.firewall.NoopFirewallDriver
openstack-config --set /etc/nova/nova.conf DEFAULT block_migration_flag VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_NON_SHARED_INC
openstack-config --set /etc/nova/nova.conf DEFAULT novncproxy_base_url http://10.170.65.200:6080/vnc_auto.html
openstack-config --set /etc/nova/nova.conf DEFAULT xvpvncproxy_base_url http://10.170.65.200:6081/console

openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit_period hour
openstack-config --set /etc/nova/nova.conf DEFAULT service_neutron_metadata_proxy True
openstack-config --set /etc/nova/nova.conf DEFAULT neutron_metadata_proxy_shared_secret ffa3b1c4d81e438f
openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit True

# configure dhcp agent
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT interface_driver neutron.agent.linux.interface.OVSInterfaceDriver
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT dhcp_driver  neutron.agent.linux.dhcp.Dnsmasq
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT use_namespaces  True
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT root_helper "sudo neutron-rootwrap /etc/neutron/rootwrap.conf"
openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT state_path /var/lib/neutron

#启动服务
service dnsmasq start
service neutron-dhcp-agent start
service neutron-openvswitch-agent start

chkconfig neutron-openvswitch-agent on
chkconfig dnsmasq on
chkconfig neutron-dhcp-agent on



#私有网络设置

keystone user-create --name UserA --pass password
keystone tenant-create --name TenantA
keystone role-create --name Member
keystone user-role-add --user UserA --role Member --tenant TenantA

外网设置网络
neutron net-create Ext-Net --provider:network_type local --router:external true
或者（未验证）
neutron net-create Ext-Net --provider:network_type gre --router:external true --provider:segmentation_id 2

Created a new network:
+---------------------------+--------------------------------------+
| Field                     | Value                                |
+---------------------------+--------------------------------------+
| admin_state_up            | True                                 |
| id                        | 304efe5b-db20-4f6b-b857-312c3a52d1a1 |
| name                      | Ext-Net                              |
| provider:network_type     | local                                |
| provider:physical_network |                                      |
| provider:segmentation_id  |                                      |
| router:external           | True                                 |
| shared                    | False                                |
| status                    | ACTIVE                               |
| subnets                   |                                      |
| tenant_id                 | 9262a90768c6474f85ff0852942a2933     |
+---------------------------+--------------------------------------+

neutron subnet-create Ext-Net 10.0.0.0/24 --disable-dhcp --allocation-pool start=10.0.0.30,end=10.0.0.100
或者
neutron subnet-create Ext-Net 10.170.65.0/24 --disable-dhcp --allocation-pool start=10.170.65.203,end=10.170.65.206

Created a new subnet:
+------------------+--------------------------------------------+
| Field            | Value                                      |
+------------------+--------------------------------------------+
| allocation_pools | {"start": "10.0.0.2", "end": "10.0.0.254"} |
| cidr             | 10.0.0.0/24                                |
| dns_nameservers  |                                            |
| enable_dhcp      | False                                      |
| gateway_ip       | 10.0.0.1                                   |
| host_routes      |                                            |
| id               | bf0e7386-7215-48dd-8178-90118dbf070a       |
| ip_version       | 4                                          |
| name             |                                            |
| network_id       | 304efe5b-db20-4f6b-b857-312c3a52d1a1       |
| tenant_id        | 9262a90768c6474f85ff0852942a2933           |
+------------------+--------------------------------------------+


#添加ip时务必要同时重启服务
sudo ip addr add 10.0.0.10/24 dev br-ex;service network restart
sudo ip link set br-ex up

#为 tenant A 创建一个网络
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://controller0:5000/v2.0 net-create TenantA-Net
Created a new network:
+----------------+--------------------------------------+
| Field          | Value                                |
+----------------+--------------------------------------+
| admin_state_up | True                                 |
| id             | 6de16c84-6dd9-45c4-bc63-04aae5b12836 |
| name           | TenantA-Net                          |
| shared         | False                                |
| status         | ACTIVE                               |
| subnets        |                                      |
| tenant_id      | dc4c32dedc6447e0a03a8aa47c0eff9a     |
+----------------+--------------------------------------+

#为tenant 创建一个ip块
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 subnet-create TenantA-Net 10.0.1.0/24

Created a new subnet:
+------------------+--------------------------------------------+
| Field            | Value                                      |
+------------------+--------------------------------------------+
| allocation_pools | {"start": "10.0.1.2", "end": "10.0.1.254"} |
| cidr             | 10.0.1.0/24                                |
| dns_nameservers  |                                            |
| enable_dhcp      | True                                       |
| gateway_ip       | 10.0.1.1                                   |
| host_routes      |                                            |
| id               | 7d75e960-0b23-45a3-a314-8cd2955c7fdc       |
| ip_version       | 4                                          |
| name             |                                            |
| network_id       | 6de16c84-6dd9-45c4-bc63-04aae5b12836       |
| tenant_id        | dc4c32dedc6447e0a03a8aa47c0eff9a           |
+------------------+--------------------------------------------+

#创建一个虚拟机
nova --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 boot --image 1db85e96-3923-4dce-933e-44b7e78fe453 --flavor 1 --nic net-id=6de16c84-6dd9-45c4-bc63-04aae5b12836  TenantA_VM1
+--------------------------------------+--------------------------------------+
| Property                             | Value                                |
+--------------------------------------+--------------------------------------+
| status                               | BUILD                                |
| updated                              | 2013-11-17T08:14:47Z                 |
| OS-EXT-STS:task_state                | scheduling                           |
| key_name                             | None                                 |
| image                                | CirrOS 0.3.0                         |
| hostId                               |                                      |
| OS-EXT-STS:vm_state                  | building                             |
| OS-SRV-USG:launched_at               | None                                 |
| flavor                               | m1.tiny                              |
| id                                   | f0e8367d-f145-417f-b7e2-1273ae01c73d |
| security_groups                      | [{u'name': u'default'}]              |
| OS-SRV-USG:terminated_at             | None                                 |
| user_id                              | 828bae9a521247cb80129ed39bcbcc3e     |
| name                                 | TenantA_VM1                          |
| adminPass                            | CdjdHyPsHM6E                         |
| tenant_id                            | dc4c32dedc6447e0a03a8aa47c0eff9a     |
| created                              | 2013-11-17T08:14:46Z                 |
| OS-DCF:diskConfig                    | MANUAL                               |
| metadata                             | {}                                   |
| os-extended-volumes:volumes_attached | []                                   |
| accessIPv4                           |                                      |
| accessIPv6                           |                                      |
| progress                             | 0                                    |
| OS-EXT-STS:power_state               | 0                                    |
| OS-EXT-AZ:availability_zone          | nova                                 |
| config_drive                         |                                      |
+--------------------------------------+--------------------------------------+

# 要连接到外网需要一个路由器
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 router-create TenantA-R1
Created a new router:
+-----------------------+--------------------------------------+
| Field                 | Value                                |
+-----------------------+--------------------------------------+
| admin_state_up        | True                                 |
| external_gateway_info |                                      |
| id                    | 757ddd2c-431a-4522-9baf-da005724cf76 |
| name                  | TenantA-R1                           |
| status                | ACTIVE                               |
| tenant_id             | dc4c32dedc6447e0a03a8aa47c0eff9a     |
+-----------------------+--------------------------------------+

#路由器连接到内网（用一个内网ip 对应路由器一个port）
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 router-interface-add TenantA-R1 7d75e960-0b23-45a3-a314-8cd2955c7fdc

Added interface 74308b3d-8c5d-42e7-b473-e7997c636d30 to router TenantA-R1.

为路由器设置网关（用一个外网ip 对应一个路由器一个port）
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 router-gateway-set TenantA-R1 Ext-Net
Set gateway for router TenantA-R1

#租户获TenantA 取一个外网ip
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 floatingip-create Ext-Net

+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| fixed_ip_address    |                                      |
| floating_ip_address | 10.0.0.3                             |
| floating_network_id | 304efe5b-db20-4f6b-b857-312c3a52d1a1 |
| id                  | fef6618e-d5e9-4739-9e66-511f6cdb4c1f |
| port_id             |                                      |
| router_id           |                                      |
| tenant_id           | dc4c32dedc6447e0a03a8aa47c0eff9a     |
+---------------------+--------------------------------------+

#获取虚拟机的vif 号,device_id 就是虚拟机的id

neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 port-list --device_id f0e8367d-f145-417f-b7e2-1273ae01c73d

+--------------------------------------+------+-------------------+---------------------------------------------------------------------------------+
| id                                   | name | mac_address       | fixed_ips                                                                       |
+--------------------------------------+------+-------------------+---------------------------------------------------------------------------------+
| 3ac25430-d2a9-408c-8c00-823e5637432f |      | fa:16:3e:44:84:f7 | {"subnet_id": "7d75e960-0b23-45a3-a314-8cd2955c7fdc", "ip_address": "10.0.1.2"} |
+--------------------------------------+------+-------------------+---------------------------------------------------------------------------------+

#将外网ip 绑定到vif
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 floatingip-associate {floating_ip_id} {port_id}
neutron --os-tenant-name TenantA --os-username UserA --os-password password --os-auth-url=http://localhost:5000/v2.0 floatingip-associate fef6618e-d5e9-4739-9e66-511f6cdb4c1f 3ac25430-d2a9-408c-8c00-823e5637432f
Associated floatingip fef6618e-d5e9-4739-9e66-511f6cdb4c1f

#验证floating ip 是否连通

在controller 机器上 ping 10.0.0.3 得到如下输出
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=63 time=5.97 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=63 time=0.910 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=63 time=0.826 ms



#安装dashboard

yum install -y memcached python-memcached mod_wsgi openstack-dashboard

修改配置文件 /etc/openstack-dashboard/local_settings 

vi /etc/openstack-dashboard/local_settings

CACHES = {
'default': {
'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
'LOCATION' : '127.0.0.1:11211'
}
}

ALLOWED_HOSTS = ['localhost','127.0.0.1']

OPENSTACK_HOST = "controller0"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "admin"

重启dashboard and cache server
 
service httpd start
service memcached start
chkconfig httpd on
chkconfig memcached on

检查是否正确配置
http://controller0/dashboard
是否正常登陆


机器重启问题,处理办法？

确保controller先启动如下服务
添加 br-ex ip
重启keystone
重启glance
重启nova 所以服务
重启neuron 所有服务


-I INPUT -p tcp --dport 80 -j ACCEPT
-I INPUT -p tcp --dport 5672 -j ACCEPT
-I INPUT -p tcp --dport 3306 -j ACCEPT
-I INPUT -p tcp --dport 5000 -j ACCEPT
-I INPUT -p tcp --dport 5672 -j ACCEPT
-I INPUT -p tcp --dport 8773 -j ACCEPT
-I INPUT -p tcp --dport 8774 -j ACCEPT
-I INPUT -p tcp --dport 8775 -j ACCEPT
-I INPUT -p tcp --dport 8776 -j ACCEPT
-I INPUT -p tcp --dport 9292 -j ACCEPT
-I INPUT -p tcp --dport 9696 -j ACCEPT
-I INPUT -p tcp --dport 15672 -j ACCEPT
-I INPUT -p tcp --dport 55672 -j ACCEPT
-I INPUT -p tcp --dport 35357 -j ACCEPT
-I INPUT -p tcp --dport 8080 -j ACCEPT
-A INPUT -p tcp --dport 9696 -j ACCEPT

对外网络不通，检查默认网关

route add default gw 10.170.65.200 br-ex



==安装heat

yum install openstack-heat-api openstack-heat-engine openstack-heat-api-cfn

openstack-config --set /etc/heat/heat.conf database connection mysql://heat:openstack@controller0/heat

mysql -uroot -popenstack -e "CREATE DATABASE heat;"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' IDENTIFIED BY 'openstack';"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'controller0' IDENTIFIED BY 'openstack';"
mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' IDENTIFIED BY 'openstack';"
heat-db-setup rpm

在keystone 创建对应的用户
keystone user-create --name=heat --pass=heat --email=heat@example.com
keystone user-role-add --user=heat --tenant=service --role=admin

vi /etc/heat/heat.conf

[filter:authtoken]
paste.filter_factory = heat.common.auth_token:filter_factory
auth_host = controller
auth_port = 35357
auth_protocol = http
admin_tenant_name = service
admin_user = heat
admin_password = HEAT_PASS


注册heat 服务

keystone service-create --name=heat --type=orchestration --description="Heat Orchestration API"

keystone endpoint-create \
--service-id=c674020083e94b4f9b3d923c71e39a18 \
--publicurl=http://controller0:8004/v1/%\(tenant_id\)s \
--internalurl=http://controller0:8004/v1/%\(tenant_id\)s \
--adminurl=http://controller0:8004/v1/%\(tenant_id\)s

keystone service-create --name=heat-cfn --type=cloudformation --description="Heat CloudFormation API"

keystone endpoint-create \
--service-id=0edb92c2190c46308280e45b985b9047 \
--publicurl=http://controller0:8000/v1 \
--internalurl=http://controller0:8000/v1 \
--adminurl=http://controller0:8000/v1

启动heat 对应服务

service openstack-heat-api start
service openstack-heat-api-cfn start
 service openstack-heat-engine start
chkconfig openstack-heat-api on
chkconfig openstack-heat-api-cfn on

使用第一个例子

wget https://raw.github.com/openstack/heat-templates/master/hot/hello_world.yaml

heat stack-create mystack --template-file=/PATH_TO_HEAT_TEMPLATES/WordPress_Single_Instance.template
--parameters="InstanceType=m1.large;DBUsername=USERNAME;DBPassword=PASSWORD;KeyName=HEAT_KEY;LinuxDistribution=F17"


安装ceilometer
安装

yum install openstack-ceilometer-api openstack-ceilometer-collector openstack-ceilometer-central python-ceilometerclient

安装mogodb
yum install mongodb-server mongodb



yum install mongodb-server mongodb
mongo --host controller0
> use ceilometer
> db.addUser( { user: "ceilometer",
pwd: "openstack",
roles: [ "readWrite", "dbAdmin" ]
} )

openstack-config --set /etc/ceilometer/ceilometer.conf database connection mongodb://ceilometer:openstack@controller0:27017/ceilometer
echo $ADMIN_TOKEN

openstack-config --set /etc/ceilometer/ceilometer.conf publisher_rpc metering_secret $ADMIN_TOKEN

keystone user-create --name=ceilometer --pass=ceilometer --email=ceilometer@example.com
keystone user-role-add --user=ceilometer --tenant=service --role=admin

openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_user ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_password ceilometer

openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_username ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_password ceilometer

keystone service-create --name=ceilometer --type=metering --description="Ceilometer Telemetry Service"

keystone endpoint-create \
--service-id=7811a1877fb744458e86bf47fe5840d2 \
--publicurl=http://controller0:8777 \
--internalurl=http://controller0:8777 \
--adminurl=http://controller0:8777

启动服务


service openstack-ceilometer-api start
service openstack-ceilometer-central start
service openstack-ceilometer-collector start
chkconfig openstack-ceilometer-api on
chkconfig openstack-ceilometer-central on
chkconfig openstack-ceilometer-collector on



安装agent

openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit True
openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit_period hour
openstack-config --set /etc/nova/nova.conf DEFAULT notify_on_state_change vm_and_task_state

# vi /etc/nova/nova.conf  

echo "notification_driver = nova.openstack.common.notifier.rpc_notifier" >> /etc/nova/nova.conf
echo "notification_driver = ceilometer.compute.nova_notifier" >> /etc/nova/nova.conf

#openstack-config --set /etc/ceilometer/ceilometer.conf publisher_rpc metering_secret $ADMIN_TOKEN
openstack-config --set /etc/ceilometer/ceilometer.conf publisher_rpc metering_secret 7884260a0a13e13fdcac
openstack-config --set /etc/ceilometer/ceilometer.conf DEFAULT qpid_hostname controller0

openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_host controller0
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_user ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_password ceilometer

openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_username ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_password ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_auth_url http://controller0:5000/v2.0

service openstack-ceilometer-compute start
chkconfig openstack-ceilometer-compute on




