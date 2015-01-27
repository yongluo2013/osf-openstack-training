##主机名配置

需要在所有节点先配置主机名

	vi /etc/hosts

	10.0.0.10 controller0
	10.0.0.20 network0
	10.0.0.30 compute0

并依此修改主机名

	echo "controller0" >  /ect/sysconfig/hostname
	echo "network0" >  /ect/sysconfig/hostname
	echo "compute0" >  /ect/sysconfig/hostname


##网络配置

###网络拓扑设计

management network
	
	10.0.0.0/24

tunnel network

	10.0.0.1/24

external network

	203.0.113.0/24

storage network

	10.0.0.2/24

controller0 节点网络配置如下

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	DEVICE=eth0
	BOOTPROTO=static
	IPADDR=10.0.0.10
	NETMASK=255.255.255.0
	GATEWAY=10.20.0.1
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	DEVICE=eth1
	BOOTPROTO=static
	IPADDR=10.0.1.10
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	TYPE=Ethernet
	DEVICE=eth2
	BOOTPROTO=static
	IPADDR=203.0.113.10
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth3
	TYPE=Ethernet
	DEVICE=eth3
	BOOTPROTO=static
	IPADDR=10.0.3.10
	NETMASK=255.255.255.0
	ONBOOT=yes


network0 节点网络配置如下

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	DEVICE=eth0
	BOOTPROTO=static
	IPADDR=10.0.0.20
	NETMASK=255.255.255.0
	GATEWAY=10.20.0.1
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	DEVICE=eth1
	BOOTPROTO=static
	IPADDR=10.0.1.20
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	TYPE=Ethernet
	DEVICE=eth2
	BOOTPROTO=static
	IPADDR=203.0.113.20
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth3
	TYPE=Ethernet
	DEVICE=eth3
	BOOTPROTO=static
	IPADDR=10.0.3.20
	NETMASK=255.255.255.0
	ONBOOT=yes

compute0 节点网络配置如下

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	DEVICE=eth0
	BOOTPROTO=static
	IPADDR=10.0.0.30
	NETMASK=255.255.255.0
	GATEWAY=10.20.0.1
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	DEVICE=eth1
	BOOTPROTO=static
	IPADDR=10.0.1.30
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	TYPE=Ethernet
	DEVICE=eth2
	BOOTPROTO=static
	IPADDR=203.0.113.30
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth3
	TYPE=Ethernet
	DEVICE=eth3
	BOOTPROTO=static
	IPADDR=10.0.3.30
	NETMASK=255.255.255.0
	ONBOOT=yes


## 基本配置

如果是centos7 需要先配置epel 和rdo repo ，Fedora 20 不需要了

	yum install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
	yum install http://rdo.fedorapeople.org/openstack-juno/rdo-release-juno.rpm

禁用默认防火墙

	systemctl stop firewalld.service
	systemctl disable firewalld.service

时间同步

	yum install  -y ntp

vi /etc/ntp.conf

	server NTP_SERVER iburst
	restrict -4 default kod notrap nomodify
	restrict -6 default kod notrap nomodify


启用ntp 时间同步服务

	systemctl enable ntpd.service
	systemctl start ntpd.service


##控制节点配置

安装mariadb

	yum install mariadb mariadb-server MySQL-python

配置MySQL 

	vi /etc/my.cnf
	bind-address = 10.0.0.10
	default-storage-engine = innodb
	innodb_file_per_table
	collation-server = utf8_general_ci
	init-connect = 'SET NAMES utf8'
	character-set-server = utf8

启用mariadb系统服务并启动

	systemctl enable mariadb.service
	systemctl start mariadb.service

设置root 初始密码为openstack

	mysql_secure_installation

安装消息服务

安装 rabbitmq

	yum install -y rabbitmq-server

启用rabbitmq 系统服务并启动rabbitmq 进程

	systemctl enable rabbitmq-server.service
	systemctl start rabbitmq-server.service

修改初始用户guest 的密码

	rabbitmqctl change_password guest openstack

安装keystone 

keystone 数据库创建

	mysql -uroot -popenstack -e "CREATE DATABASE keystone;"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'openstack';"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'openstack';"

keystone 包安装

	yum install -y openstack-keystone python-keystoneclient

为keystone 设置admin 账户的 token

	ADMIN_TOKEN=$(openssl rand -hex 10)
	echo $ADMIN_TOKEN
	openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token $ADMIN_TOKEN


配置数据连接

	openstack-config --set /etc/keystone/keystone.conf sql connection mysql://keystone:openstack@controller0/keystone

配置token 方式为uuid

	openstack-config --set /etc/keystone/keystone.conf token provider keystone.token.providers.uuid.Provider
	openstack-config --set /etc/keystone/keystone.conf token driver keystone.token.persistence.backends.sql.Token

启用debug 
	openstack-config --set /etc/keystone/keystone.conf DEFAULT debug True
	openstack-config --set /etc/keystone/keystone.conf DEFAULT verbose True

Create generic certificates and keys and restrict access to the associated files:

	keystone-manage pki_setup --keystone-user keystone --keystone-group keystone
	chown -R keystone:keystone /var/log/keystone
	chown -R keystone:keystone /etc/keystone/ssl
	chmod -R o-rwx /etc/keystone/ssl

初始化keystone数据库

	su -s /bin/sh -c "keystone-manage db_sync" keystone

启用keystone 系统服务

	systemctl enable openstack-keystone.service
	systemctl start openstack-keystone.service

创建建admin 用户

	export OS_SERVICE_TOKEN=`echo $ADMIN_TOKEN`
	export OS_SERVICE_ENDPOINT=http://controller0:35357/v2.0

创建管理员租户

	keystone tenant-create --name admin --description "Admin Tenant"

创建管理员用户

	keystone user-create --name=admin --pass=admin --email=admin@example.com

创建管理员角色

	keystone role-create --name=admin


为管理员用户 "admin" 在admin 租户中分配 "admin"角色

	keystone user-role-add --user=admin --tenant=admin --role=admin

创建demo 租户

	keystone tenant-create --name demo --description "Demo Tenant"

创建demo 用户

	keystone user-create --name demo --tenant demo --pass=demo --email=demo@example.com

创建服务租户

	keystone tenant-create --name service --description "Service Tenant"

为keystone 服务建立 endpoints

	keystone service-create --name keystone --type identity --description "OpenStack Identity"

为keystone 建立 servie 和 endpoint 关联

	keystone endpoint-create \
	--service-id $(keystone service-list | awk '/ identity / {print $2}') \
	--publicurl http://controller0:5000/v2.0 \
	--internalurl http://controller0:5000/v2.0 \
	--adminurl http://controller0:35357/v2.0 \
	--region regionOne

验证keystone 安装的正确性

先取消先前的Token变量，不然会干扰新建用户的验证。

	unset OS_SERVICE_TOKEN OS_SERVICE_ENDPOINT

先用命令行方式验证

	keystone --os-username=admin --os-password=admin --os-auth-url=http://controller0:35357/v2.0 token-get
	keystone --os-username=admin --os-password=admin --os-tenant-name=admin --os-auth-url=http://controller0:35357/v2.0 token-get


让后用设置环境变量认证,保存认证信息

	vi ~/keystonerc

	export OS_USERNAME=admin
	export OS_PASSWORD=admin
	export OS_TENANT_NAME=admin
	export OS_AUTH_URL=http://controller0:35357/v2.0


source 该文件使其生效

	source keystonerc
	keystone token-get

到此Keystone 安装结束。


###glance 安装

	mysql -uroot -popenstack -e "CREATE DATABASE glance;"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY 'openstack';"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'openstack';"


创建glance 用户

	keystone user-create --name=glance --pass=glance --email=glance@example.com

并分配service角色

	keystone user-role-add --user=glance --tenant=service --role=admin

创建glance 服务

	keystone service-create --name=glance --type=image --description="OpenStack Image Service"


创建keystone 的endpoint 

	keystone endpoint-create \
	--service-id $(keystone service-list | awk '/ image / {print $2}') \
	--publicurl http://controller0:9292 \
	--internalurl http://controller0:9292 \
	--adminurl http://controller0:9292 \
	--region regionOne

安装Glance 的包

	yum install openstack-glance python-glanceclient -y

配置Glance 连接数据库


	openstack-config --set /etc/glance/glance-api.conf DEFAULT sql_connection mysql://glance:openstack@controller0/glance
	openstack-config --set /etc/glance/glance-registry.conf DEFAULT sql_connection mysql://glance:openstack@controller0/glance

用openstack util 修改glance api 和 register 配置文件

	openstack-config --set /etc/glance/glance-api.conf DEFAULT debug True
	openstack-config --set /etc/glance/glance-api.conf DEFAULT verbose True
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_uri http://controller0:5000
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_host controller0
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_port 35357
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken auth_protocol http
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_tenant_name service
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_user glance
	openstack-config --set /etc/glance/glance-api.conf keystone_authtoken admin_password glance
	openstack-config --set /etc/glance/glance-api.conf paste_deploy flavor keystone

	openstack-config --set /etc/glance/glance-registry.conf DEFAULT debug True
	openstack-config --set /etc/glance/glance-registry.conf DEFAULT verbose True
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_uri http://controller0:5000
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_host controller0
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_port 35357
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken auth_protocol http
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_tenant_name service
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_user glance
	openstack-config --set /etc/glance/glance-registry.conf keystone_authtoken admin_password glance
	openstack-config --set /etc/glance/glance-registry.conf paste_deploy flavor keystone

初始化glance 数据库

	su -s /bin/sh -c "glance-manage db_sync" glance

启动glance 相关的两个服务

	systemctl enable openstack-glance-api.service openstack-glance-registry.service
	systemctl start openstack-glance-api.service openstack-glance-registry.service

上传test image 到glance

	wget http://cdn.download.cirros-cloud.net/0.3.3/cirros-0.3.3-x86_64-disk.img
	glance image-create --name "cirros-0.3.3-x86_64" --file cirros-0.3.3-x86_64-disk.img --disk-format qcow2 --container-format bare --is-public True --progress

检查镜像是否上传成功

	glance image-list

### Nova controller 安装

	mysql -uroot -popenstack -e "CREATE DATABASE nova;"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY 'openstack';"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'openstack';"


在keystone中创建nova相应的用户和服务

	keystone user-create --name=nova --pass=nova --email=nova@example.com
	keystone user-role-add --user=nova --tenant=service --role=admin

keystone 注册服务

	keystone service-create --name=nova --type=compute --description="OpenStack Compute Service"

keystone 注册endpoint

	keystone endpoint-create \
	--service-id $(keystone service-list | awk '/ compute / {print $2}') \
	--publicurl http://controller0:8774/v2/%\(tenant_id\)s \
	--internalurl http://controller0:8774/v2/%\(tenant_id\)s \
	--adminurl http://controller0:8774/v2/%\(tenant_id\)s \
	--region regionOne

安装nova controller 相关软件包

yum install -y openstack-nova-api openstack-nova-cert openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler
python-novaclient

配置nova MySQL 连接

	openstack-config --set /etc/nova/nova.conf database connection mysql://nova:openstack@controller0/nova

	openstack-config --set /etc/nova/nova.conf DEFAULT rpc_backend rabbit
	openstack-config --set /etc/nova/nova.conf DEFAULT rabbit_host  controller0
	openstack-config --set /etc/nova/nova.conf DEFAULT rabbit_password  openstack

	openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone
	openstack-config --set /etc/nova/nova.conf DEFAULT my_ip  10.0.0.10


	openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_listen 10.0.0.10
	openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_proxyclient_address 10.0.0.10

	openstack-config --set /etc/nova/nova.conf DEFAULT verbose  True
	openstack-config --set /etc/nova/nova.conf DEFAULT debug  True

	openstack-config --set /etc/nova/nova.conf  keystone_authtoken auth_uri  http://controller0:5000/v2.0
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken identity_uri  http://controller0:35357
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_tenant_name  service
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_user  nova
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_password  nova

	openstack-config --set /etc/nova/nova.conf glance host controller0

初始化nova 数据库

	su -s /bin/sh -c "nova-manage db sync" nova

	systemctl enable openstack-nova-api.service openstack-nova-cert.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service
	systemctl start openstack-nova-api.service openstack-nova-cert.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service

##安装nova compute 节点

	yum install openstack-nova-compute sysfsutils


配置nova compute 

	openstack-config --set /etc/nova/nova.conf DEFAULT rpc_backend rabbit
	openstack-config --set /etc/nova/nova.conf DEFAULT rabbit_host  controller0
	openstack-config --set /etc/nova/nova.conf DEFAULT rabbit_password  openstack

	openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone
	openstack-config --set /etc/nova/nova.conf DEFAULT my_ip  10.0.0.30


	openstack-config --set /etc/nova/nova.conf DEFAULT vnc_enabled True
	openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_listen 0.0.0.0
	openstack-config --set /etc/nova/nova.conf DEFAULT vncserver_proxyclient_address 10.0.0.30
	openstack-config --set /etc/nova/nova.conf DEFAULT novncproxy_base_url http://controller0:6080/vnc_auto.html

	openstack-config --set /etc/nova/nova.conf DEFAULT verbose  True
	openstack-config --set /etc/nova/nova.conf DEFAULT debug  True

	openstack-config --set /etc/nova/nova.conf  keystone_authtoken auth_uri  http://controller0:5000/v2.0
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken identity_uri  http://controller0:35357
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_tenant_name  service
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_user  nova
	openstack-config --set /etc/nova/nova.conf  keystone_authtoken admin_password  nova

	openstack-config --set /etc/nova/nova.conf glance host controller0

	openstack-config --set /etc/nova/nova.conf libvirt virt_type qemu

	systemctl enable libvirtd.service openstack-nova-compute.service
	systemctl start libvirtd.service openstack-nova-compute.service

检查nova 安装是否正确

	nova service-list

##Neutron API 安装（controller上安装）

创建Neutron 数据库

	mysql -uroot -popenstack -e "CREATE DATABASE neutron;"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'openstack';"
	mysql -uroot -popenstack -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'openstack';"

在keystone 中创建Neutron 用户

	keystone user-create --name neutron --pass neutron --email neutron@example.com

	keystone user-role-add --user neutron --tenant service --role admin

	keystone service-create --name neutron --type network --description "OpenStack Networking"

	keystone endpoint-create \
	--service-id $(keystone service-list | awk '/ network / {print $2}') \
	--publicurl http://controller0:9696 \
	--adminurl http://controller0:9696 \
	--internalurl http://controller0:9696 \
	--region regionOne

	yum install -y openstack-neutron openstack-neutron-ml2 python-neutronclientwhich -y


配置Neutron Controller

	openstack-config --set /etc/neutron/neutron.conf database connection mysql://neutron:openstack@controller0/neutron

	openstack-config --set /etc/neutron/neutron.conf DEFAULT rpc_backend  rabbit
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_host  controller0
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_password  openstack

	openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy keystone

	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_uri  http://controller0:5000/v2.0
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken identity_uri  http://controller0:35357
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name  service
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user  neutron
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password  neutron

	openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin  ml2
	openstack-config --set /etc/neutron/neutron.conf DEFAULT service_plugins  router
	openstack-config --set /etc/neutron/neutron.conf DEFAULT allow_overlapping_ips  True

	openstack-config --set /etc/neutron/neutron.conf DEFAULT notify_nova_on_port_status_changes  True
	openstack-config --set /etc/neutron/neutron.conf DEFAULT notify_nova_on_port_data_changes  True
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_url  http://controller0:8774/v2
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_auth_url  http://controller0:35357/v2.0
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_region_name  regionOne
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_username  nova
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_tenant_id  f153e43878fb4f848527c54a4d139a0f
	openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_password  nova

	openstack-config --set /etc/neutron/neutron.conf DEFAULT verbose True

Configure ml2

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 type_drivers  flat,gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 tenant_network_types  gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 mechanism_drivers  openvswitch

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_gre tunnel_id_ranges  1:1000

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_security_group  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_ipset  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup firewall_driver  neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver

配置Nova 使用Neutron 

	openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class  nova.network.neutronv2.api.API
	openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api  neutron
	openstack-config --set /etc/nova/nova.conf DEFAULT linuxnet_interface_driver  nova.network.linux_net.LinuxOVSInterfaceDriver
	openstack-config --set /etc/nova/nova.conf DEFAULT firewall_driver  nova.virt.firewall.NoopFirewallDriver

	openstack-config --set /etc/nova/nova.conf neutron url  http://controller0:9696
	openstack-config --set /etc/nova/nova.conf neutron auth_strategy  keystone
	openstack-config --set /etc/nova/nova.conf neutron admin_auth_url  http://controller0:35357/v2.0
	openstack-config --set /etc/nova/nova.conf neutron admin_tenant_name  service
	openstack-config --set /etc/nova/nova.conf neutron admin_username  neutron
	openstack-config --set /etc/nova/nova.conf neutron admin_password  neutron

	ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini 

	su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade juno" neutron

	systemctl restart openstack-nova-api.service openstack-nova-scheduler.service openstack-nova-conductor.service

	systemctl enable neutron-server.service 
	systemctl start neutron-server.service


安装网络节点network0

	vi /etc/sysctl.conf

	net.ipv4.ip_forward=1
	net.ipv4.conf.all.rp_filter=0
	net.ipv4.conf.default.rp_filter=0

安装网络节点Neutron相关软件包

	yum install -y openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch

配置Neutron server

	openstack-config --set /etc/neutron/neutron.conf DEFAULT rpc_backend  rabbit
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_host  controller0
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_password  openstack

	openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy keystone

	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_uri  http://controller0:5000/v2.0
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken identity_uri  http://controller0:35357
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name  service
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user  neutron
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password  neutron

	openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin  ml2
	openstack-config --set /etc/neutron/neutron.conf DEFAULT service_plugins  router
	openstack-config --set /etc/neutron/neutron.conf DEFAULT allow_overlapping_ips  True

	openstack-config --set /etc/neutron/neutron.conf DEFAULT verbose True


	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 type_drivers  flat,gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 tenant_network_types  gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 mechanism_drivers  openvswitch

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_flat flat_networks external

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_gre tunnel_id_ranges  1:1000

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_security_group  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_ipset  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup firewall_driver  neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ovs local_ip  10.0.1.20
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ovs enable_tunneling  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ovs bridge_mappings  external:br-ex

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini agent tunnel_types  gre

配置l3 agent

	openstack-config --set /etc/neutron/l3_agent.ini DEFAULT interface_driver neutron.agent.linux.interface.OVSInterfaceDriver
	openstack-config --set /etc/neutron/l3_agent.ini DEFAULT use_namespaces  True
	openstack-config --set /etc/neutron/l3_agent.ini DEFAULT external_network_bridge br-ex
	openstack-config --set /etc/neutron/l3_agent.ini DEFAULT verbose True

配置dhcp agent

	openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT interface_driver  neutron.agent.linux.interface.OVSInterfaceDriver
	openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT dhcp_driver  neutron.agent.linux.dhcp.Dnsmasq
	openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT use_namespaces  True	
	openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT verbose True

设置MTU默认值

	openstack-config --set /etc/neutron/dhcp_agent.ini DEFAULT dnsmasq_config_file  /etc/neutron/dnsmasq-neutron.conf
	echo "dhcp-option-force=26,1454" > /etc/neutron/dnsmasq-neutron.conf

重启dnsmq

    pkill dnsmasq

配置metadata agent

	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT auth_url  http://controller0:5000/v2.0
	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT auth_region  regionOne
	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_tenant_name  service
	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_user  neutron
	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT admin_password  neutron

	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT nova_metadata_ip  10.0.0.10

	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT metadata_proxy_shared_secret  ce07f66e3245389a15c2

	openstack-config --set /etc/neutron/metadata_agent.ini DEFAULT verbose  True


在controller 节点需要如下配置

	openstack-config --set /etc/nova/nova.conf neutron service_metadata_proxy  True
	openstack-config --set /etc/nova/nova.conf neutron metadata_proxy_shared_secret  ce07f66e3245389a15c2

	systemctl restart openstack-nova-api.service

配置 openvswitch

	yum install -y openvswitch ethtool

	systemctl enable openvswitch.service
	systemctl start openvswitch.service
	ovs-vsctl add-br br-ex
	ovs-vsctl add-port br-ex eth2
	ethtool -K eth2 gro off 

	ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

	cp /usr/lib/systemd/system/neutron-openvswitch-agent.service /usr/lib/systemd/system/neutron-openvswitch-agent.service.orig
	sed -i 's,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g' /usr/lib/systemd/system/neutron-openvswitch-agent.service

	systemctl enable neutron-openvswitch-agent.service neutron-l3-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-ovs-cleanup.service
	systemctl start neutron-openvswitch-agent.service neutron-l3-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service


配置计算节点的Neutron部分

	vi /etc/sysctl.conf

	net.ipv4.conf.all.rp_filter=0
	net.ipv4.conf.default.rp_filter=0

	sysctl -p

配置Neutron 


	openstack-config --set /etc/neutron/neutron.conf DEFAULT rpc_backend  rabbit
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_host  controller0
	openstack-config --set /etc/neutron/neutron.conf DEFAULT rabbit_password  openstack

	openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy keystone

	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken auth_uri  http://controller0:5000/v2.0
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken identity_uri  http://controller0:35357
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name  service
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_user  neutron
	openstack-config --set /etc/neutron/neutron.conf keystone_authtoken admin_password  neutron

	openstack-config --set /etc/neutron/neutron.conf DEFAULT core_plugin  ml2
	openstack-config --set /etc/neutron/neutron.conf DEFAULT service_plugins  router
	openstack-config --set /etc/neutron/neutron.conf DEFAULT allow_overlapping_ips  True

	openstack-config --set /etc/neutron/neutron.conf DEFAULT verbose True


	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 type_drivers  flat,gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 tenant_network_types  gre
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 mechanism_drivers  openvswitch

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_gre tunnel_id_ranges  1:1000

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_security_group  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_ipset  True
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup firewall_driver  neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ovs local_ip 10.0.1.30
	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini ovs enable_tunneling  True

	openstack-config --set /etc/neutron/plugins/ml2/ml2_conf.ini agent tunnel_types  gre

	systemctl enable openvswitch.service
	systemctl start openvswitch.service

配置nova 启用Neutron 的网络组件

	openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class  nova.network.neutronv2.api.API
	openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api  neutron
	openstack-config --set /etc/nova/nova.conf DEFAULT linuxnet_interface_driver  nova.network.linux_net.LinuxOVSInterfaceDriver
	openstack-config --set /etc/nova/nova.conf DEFAULT firewall_driver  nova.virt.firewall.NoopFirewallDriver

	openstack-config --set /etc/nova/nova.conf neutron url  http://controller0:9696
	openstack-config --set /etc/nova/nova.conf neutron auth_strategy  keystone
	openstack-config --set /etc/nova/nova.conf neutron admin_auth_url  http://controller0:35357/v2.0
	openstack-config --set /etc/nova/nova.conf neutron admin_tenant_name  service
	openstack-config --set /etc/nova/nova.conf neutron admin_username  neutron
	openstack-config --set /etc/nova/nova.conf neutron admin_password  neutron

	ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini 
	cp /usr/lib/systemd/system/neutron-openvswitch-agent.service /usr/lib/systemd/system/neutron-openvswitch-agent.service.orig
	sed -i 's,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g' /usr/lib/systemd/system/neutron-openvswitch-agent.service

	systemctl restart openstack-nova-compute.service
	systemctl enable neutron-openvswitch-agent.service
	systemctl start neutron-openvswitch-agent.service

计算节点和网络节点安装完毕。

初始化网络

在Neutron 中创建外部网络

	neutron net-create ext-net --shared --router:external True --provider:physical_network external --provider:network_type flat

	neutron subnet-create ext-net --name ext-subnet --allocation-pool start=203.0.113.101,end=203.0.113.200 --disable-dhcp --gateway 203.0.113.1 203.0.113.0/24

在demo 租户中重建demo-net 网络

	vi ~/demo-openrc.sh

	export OS_USERNAME=demo
	export OS_PASSWORD=demo
	export OS_TENANT_NAME=demo
	export OS_AUTH_URL=http://controller0:35357/v2.0

	source demo-openrc.sh

	neutron net-create demo-net

	neutron subnet-create demo-net --name demo-subnet --gateway 192.168.1.1 192.168.1.0/24

	neutron router-create demo-router

	neutron router-interface-add demo-router demo-subnet

	neutron router-gateway-set demo-router ext-net

安装dashboard

	yum install -y openstack-dashboard httpd mod_wsgi memcached pythonmemcached

	vi /etc/openstack-dashboard/local_settings

	OPENSTACK_HOST = "controller"
	ALLOWED_HOSTS = ['*']
	CACHES = {
		'default': {
		'BACKEND': 'django.core.cache.backends.memcached.
		MemcachedCache',
		'LOCATION': '127.0.0.1:11211',
		}
	}

	TIME_ZONE = "Asia/Shanghai"

	setsebool -P httpd_can_network_connect on
	chown -R apache:apache /usr/share/openstack-dashboard/static

	systemctl enable httpd.service memcached.service
	systemctl start httpd.service memcached.service

安装dashboard安装正确性

登录http://10.0.0.10/dashboard ,用admin/admin 登录web dashboard


其他微调

	openstack-config --set /etc/nova/nova.conf rdp enabled   true
	openstack-config --set /etc/nova/nova.conf rdp html5_proxy_base_url  http://127.0.0.1:6083/































