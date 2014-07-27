#OpenStack 手动安装手册（Icehouse）

##部署架构

为了更好的展现OpenStack各组件分布式部署的特点，以及逻辑网络配置的区别，本实验不采用All in One 的部署模式，而是采用多节点分开部署的方式，方便后续学习研究。

![architecture](/installation/images/architecture.png)

##网络拓扑

![networking](/installation/images/networking.png)

##环境准备

本实验采用Virtualbox Windows 版作为虚拟化平台，模拟相应的物理网络和物理服务器，如果需要部署到真实的物理环境，此步骤可以直接替换为在物理机上相应的配置，其原理相同。

Virtualbox 下载地址：https://www.virtualbox.org/wiki/Downloads

###虚拟网络

需要新建3个虚拟网络Net0、Net1和Net2，其在virtual box 中对应配置如下。

	Net0:
		Network name: VirtualBox  host-only Ethernet Adapter#2
		Purpose: administrator / management network
		IP block: 10.20.0.0/24
		DHCP: disable
		Linux device: eth0

	Net1:
		Network name: VirtualBox  host-only Ethernet Adapter#3
		Purpose: public network
		DHCP: disable
		IP block: 172.16.0.0/24
		Linux device: eth1

	Net2：
		Network name: VirtualBox  host-only Ethernet Adapter#4
		Purpose: Storage/private network
		DHCP: disable
		IP block: 192.168.4.0/24
		Linux device: eth2

###虚拟机

需要新建3个虚拟机VM0、VM1和VM2，其对应配置如下。

	VM0：
		Name: controller0
		vCPU:1
		Memory :1G
		Disk:30G
		Networks: net1

	VM1：
		Name : network0
		vCPU:1
		Memory :1G
		Disk:30G
		Network:net1,net2,net3

	VM2：
		Name: compute0
		vCPU:2
		Memory :2G
		Disk:30G
		Networks:net1,net3


###网络设置

	controller0 
	     eth0:10.20.0.10   (management network)
	     eht1:(disabled)
	     eht2:(disabled)

	network0
	     eth0:10.20.0.20    (management network)
	     eht1:172.16.0.20   (public/external network)
	     eht2:192.168.4.20  (private network)

	compute0
	     eth0:10.20.0.30   (management network)
	     eht1:(disabled)
	     eht2:192.168.4.30  (private network)

	compute1  (optional)
	     eth0:10.20.0.31   (management network)
	     eht1:(disabled)
	     eht2:192.168.4.31  (private network)

###操作系统准备

本实验使用Linux 发行版 CentOS 6.5 x86_64，在安装操作系统过程中，选择的初始安装包为“基本”安装包，安装完成系统以后还需要额外配置如下YUM 仓库。

ISO文件下载：http://mirrors.163.com/centos/6.5/isos/x86_64/CentOS-6.5-x86_64-bin-DVD1.iso 

EPEL源: http://dl.fedoraproject.org/pub/epel/6/x86_64/

RDO源:  http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/

自动配置执行如此命令即可，源安装完成后更新所有RPM包，由于升级了kernel 需要重新启动操作系统。

	yum install -y http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/rdo-release-icehouse-4.noarch.rpm
	yum install -y http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
	yum update -y
	reboot -h 0

接下来可以开始安装配置啦！

###公共配置（all nodes）

以下命令需要在每一个节点都执行。

修改hosts 文件

	vi /etc/hosts

	127.0.0.1    localhost
	::1          localhost 
	10.20.0.10   controller0 
	10.20.0.20   network0
	10.20.0.30   compute0


禁用 selinux 

	vi /etc/selinux/config
	SELINUX=disabled


安装NTP 服务

	yum install ntp -y
	service ntpd start
	chkconfig ntpd on

修改NTP配置文件，配置从controller0时间同步


	vi /etc/ntp.conf

	server 10.20.0.10
	fudge  192.168.0.10 stratum 10  # LCL is unsynchronized


立即同步并检查时间同步配置是否正确

	ntpdate -u 10.20.0.10
	service ntpd restart
	ntpq -p


安装openstack-utils,方便后续直接可以通过命令行方式修改配置文件


	yum install -y openstack-utils


###基本服务安装与配置（controller0 node）

基本服务包括数据库服务和AMQP服务，本实例采用MySQL 和Qpid 作为这两个服务的实现。

MySQL 服务安装

	yum install -y mysql mysql-server MySQL-python
	service mysqld start
	chkconfig mysqld on

交互式配置MySQL root 密码，设置密码为“openstack”

	mysql_secure_installation


Qpid 安装消息服务，设置客户端不需要验证使用服务

	yum install -y qpid-cpp-server

	vi /etc/qpidd.conf
	auth=no


配置修改后，重启Qpid后台服务

	service qpidd start
	chkconfig qpidd on


##控制节点安装（controller0）

主机名设置

	vi /etc/sysconfig/network
	HOSTNAME=controller0

网卡配置

	vi /etc/sysconfig/network-scripts/ifcfg-eth0

	DEVICE=eth0
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=10.20.0.10
	NETMASK=255.255.255.0


网络配置文件修改完后重启网络服务

	serice network restart

###Keyston 安装与配置

安装keystone 包

	yum install openstack-keystone python-keystoneclient -y

为keystone 设置admin 账户的 tokn


	ADMIN_TOKEN=$(openssl rand -hex 10)
	echo $ADMIN_TOKEN
	openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token $ADMIN_TOKEN


配置数据连接


	openstack-config --set /etc/keystone/keystone.conf sql connection mysql://keystone:openstack@controller0/keystone


设置Keystone 用 PKI tokens 


	keystone-manage pki_setup --keystone-user keystone --keystone-group keystone
	chown -R keystone:keystone /etc/keystone/ssl
	chmod -R o-rwx /etc/keystone/ssl


初始化Keystone数据库

	openstack-db --init --service keystone --password openstack


启动keystone 服务


	service openstack-keystone start
	chkconfig openstack-keystone on

设置认证信息

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


为keystone 服务建立 endpoints


	keystone service-create --name=keystone --type=identity --description="Keystone Identity Service"


为keystone 建立 servie 和 endpoint 关联


	keystone endpoint-create \
	--service-id=$(keystone service-list | awk '/ identity / {print $2}') \
	--publicurl=http://controller0:5000/v2.0 \
	--internalurl=http://controller0:5000/v2.0 \
	--adminurl=http://controller0:35357/v2.0


验证keystone 安装的正确性

取消先前的Token变量，不然会干扰新建用户的验证。

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


Keystone 安装结束。

###Glance 安装与配置 

安装Glance 的包

	yum install openstack-glance python-glanceclient -y


初始化Glance数据库

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


下载最Cirros镜像验证glance 安装是否成功

	wget http://cdn.download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img
	glance image-create --name="CirrOS 0.3.1" --disk-format=qcow2  --container-format=ovf --is-public=true < cirros-0.3.1-x86_64-disk.img



查看刚刚上传的image 

	glance index

如果显示相应的image 信息说明安装成功。


yum install -y http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

其他服务安装步骤，待续...

