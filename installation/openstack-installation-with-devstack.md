
##devstack 安装openstack

devstack 主要是用于openstack 演示以及开发过程中自动化安装，通常不能直接用于生产环境部署。

###环境准备

从之前实验中准备好的虚拟机克隆一个新的虚拟机，配置如下

	Devstack VM：
		Name: devstack
		vCPU:4
		Memory :4G
		Disk:30G
		Networks: net0，net1，net2

网络环境

	Net0:
		Network name: VirtualBox  host-only Ethernet Adapter#2
		Purpose: administrator / management network
		IP block: 10.20.0.210/24
		DHCP: disable
		Linux device: eth0

	Net1:
		Network name: VirtualBox  host-only Ethernet Adapter#3
		Purpose: public network
		DHCP: disable
		IP block: 172.16.0.210/24
		Linux device: eth1

	Net2：
		Network name: VirtualBox  host-only Ethernet Adapter#4
		Purpose: Storage/private network
		DHCP: disable
		IP block: 192.168.4.210/24
		Linux device: eth2

###安装步骤

devstack 的安装不能直接用root 用户，新建一个用户stack

	adduser -m stack
	passwd stack

从github上克隆devstack 的源码

	su - stack
	git clone  https://github.com/openstack-dev/devstack.git
	su - root
	cd /home/stack/devstack/tools/create-stack-user.sh 

如果你的环境需要设置代理，请添加http Proxy (可选)

	export http_proxy=http://<your_proxy_ip>:<port>
	export https_proxy=http://<your_proxy_ip>:<port>

排除不需要代理的IP地址(可选)

	export no_proxy="127.0.0.1,192.168.1.205"

为了加速下载设置国内的pip 源，这里设置豆瓣网公开的pip源

	mkdir ~/.pip
	cat > ~/.pip/pip.conf <<EOF
	[global]
	index-url = http://pypi.douban.com/simple/
	EOF


编辑local.conf 配置文件如下，只安装Keystone，Glance，Nova，Neutron

	vi local.conf

	[[local|localrc]]

	HOST_IP=10.20.0.210	
	GIT_BASE=https://github.com

	# Logging
	LOGFILE=$DEST/logs/stack.sh.log
	VERBOSE=True
	LOG_COLOR=False
	SCREEN_LOGDIR=$DEST/logs/screen

	# Credentials
	ADMIN_PASSWORD=openstack
	DATABASE_PASSWORD=$ADMIN_PASSWORD
	RABBIT_PASSWORD=$ADMIN_PASSWORD
	SERVICE_PASSWORD=$ADMIN_PASSWORD
	SERVICE_TOKEN=$ADMIN_PASSWORD

	# Github's Branch
	GLANCE_BRANCH=stable/icehouse
	HORIZON_BRANCH=stable/icehouse
	KEYSTONE_BRANCH=stable/icehouse
	NOVA_BRANCH=stable/icehouse
	NEUTRON_BRANCH=stable/icehouse
	HEAT_BRANCH=stable/icehouse
	CEILOMETER_BRANCH=stable/icehouse

	DISABLED_SERVICES=n-net,heat,swift,ceilometer
	ENABLED_SERVICES+=,q-svc,q-agt,q-dhcp,q-l3,q-meta,q-metering,neutron
	# Neutron - Load Balancing
	ENABLED_SERVICES+=,q-lbaas

运行stack.sh 安装openstack

	cd /home/stack/devstack
	./stack.sh

整个过程大概需要一个小时，具体时间视各地网络速度而定


最后出现类似如下输出，说明安装完成

	Horizon is now available at http://10.20.0.210/
	Keystone is serving at http://10.20.0.210:5000/v2.0/
	Examples on using novaclient command line is in exercise.sh
	The default users are: admin and demo
	The password: quiet
	This is your host ip: 10.20.0.210

打开浏览器输入http://10.20.0.210/ 登录Dashboard

###可能存在的问题

1. 如果遇到不能连接pypi.douban.com 

解决办法：还要为pypi.douban.com 添加ip 映射douban 的源 125.78.248.73，其实豆瓣也是官方给的pip源的镜像。

	vi  /etc/hosts
	125.78.248.73 pypi.python.org

2.git heat clone 失败或者超时问题

解决办法：可以手动克隆heat 到/opt/stack 让后再运行./stack.sh


3.安装过程中检查q-dhcp 服务没有启动，安装失败。

查看/var/log/neutron/dhcp-agent.log，确认是否有以下错误出现

	2013-11-15 17:18:07.785 9808 WARNING neutron.agent.linux.dhcp [-] FAILED VERSION REQUIREMENT FOR DNSMASQ. DHCP AGENT MAY NOT RUN CORRECTLY! Please ensure that its version is 2.59 or above!
	RuntimeError:
	2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Command: ['sudo', 'neutron-rootwrap', '/etc/neutron/rootwrap.conf', 'ip', 'netns', 'add', 'qdhcp-85c85884-3d8f-4f2a-8f81-97f1aa686837']
	2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Exit code: 255
	2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Stdout: ''
	2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Stderr: 'Bind /proc/self/ns/net -> /var/run/netns/qdhcp-85c85884-3d8f-4f2a-8f81-97f1aa686837 failed: No such file or directory\n'

解决办法：下载并安装新版本的dnsmasq，然后重新运行./stack.sh

	wget http://pkgs.repoforge.org/dnsmasq/dnsmasq-2.65-1.el6.rfx.x86_64.rpm
	rpm -Uvh dnsmasq-2.65-1.el6.rfx.x86_64.rpm


###几种常见的local.conf配置


icehouse 完全安装，网络用Neutron

	vi local.conf

	[[local|localrc]]

	HOST_IP=192.168.1.205
	GIT_BASE=https://github.com

	# Logging
	LOGFILE=$DEST/logs/stack.sh.log
	VERBOSE=True
	LOG_COLOR=False
	SCREEN_LOGDIR=$DEST/logs/screen

	# Credentials
	ADMIN_PASSWORD=openstack
	DATABASE_PASSWORD=$ADMIN_PASSWORD
	RABBIT_PASSWORD=$ADMIN_PASSWORD
	SERVICE_PASSWORD=$ADMIN_PASSWORD
	SERVICE_TOKEN=$ADMIN_PASSWORD

	# Github's Branch
	GLANCE_BRANCH=stable/icehouse
	HORIZON_BRANCH=stable/icehouse
	KEYSTONE_BRANCH=stable/icehouse
	NOVA_BRANCH=stable/icehouse
	NEUTRON_BRANCH=stable/icehouse
	HEAT_BRANCH=stable/icehouse
	CEILOMETER_BRANCH=stable/icehouse

	# Neutron - Networking Service
	DISABLED_SERVICES=n-net
	ENABLED_SERVICES+=,q-svc,q-agt,q-dhcp,q-l3,q-meta,q-metering,neutron

	# Neutron - Load Balancing
	ENABLED_SERVICES+=,q-lbaas

	# Heat - Orchestration Service
	ENABLED_SERVICES+=,heat,h-api,h-api-cfn,h-api-cw,h-eng
	HEAT_STANDALONE=True

	# Ceilometer - Metering Service (metering + alarming)
	ENABLED_SERVICES+=,ceilometer-acompute,ceilometer-acentral,ceilometer-collector,ceilometer-api
	ENABLED_SERVICES+=,ceilometer-alarm-notify,ceilometer-alarm-eval


icehouse完全安装，网络用nova-network

	vi local.conf

	[[local|localrc]]
	HOST_IP=192.168.1.205
	LOGDAYS=1
	LOGFILE=$DEST/logs/stack.sh.log
	SCREEN_LOGDIR=$DEST/logs/screen
	ADMIN_PASSWORD=openstack
	DATABASE_PASSWORD=$ADMIN_PASSWORD
	RABBIT_PASSWORD=$ADMIN_PASSWORD
	SERVICE_PASSWORD=$ADMIN_PASSWORD
	SERVICE_TOKEN=$ADMIN_PASSWORD
	GIT_BASE=https://github.com
	DIB_BRANCH=stable/icehouse


只安装Keystone，Glance，Nove，Horizon

	vi local.conf

	[[local|localrc]]

	HOST_IP=10.20.0.210
	GIT_BASE=https://github.com

	# Logging
	LOGFILE=$DEST/logs/stack.sh.log
	VERBOSE=True
	LOG_COLOR=False
	SCREEN_LOGDIR=$DEST/logs/screen

	# Credentials
	ADMIN_PASSWORD=quiet
	DATABASE_PASSWORD=$ADMIN_PASSWORD
	RABBIT_PASSWORD=$ADMIN_PASSWORD
	SERVICE_PASSWORD=$ADMIN_PASSWORD
	SERVICE_TOKEN=$ADMIN_PASSWORD

	# Github's Branch
	GLANCE_BRANCH=stable/icehouse
	HORIZON_BRANCH=stable/icehouse
	KEYSTONE_BRANCH=stable/icehouse
	NOVA_BRANCH=stable/icehouse
	NEUTRON_BRANCH=stable/icehouse
	HEAT_BRANCH=stable/icehouse
	CEILOMETER_BRANCH=stable/icehouse

	DISABLED_SERVICES=n-net,heat,swift,ceilometer
	ENABLED_SERVICES+=,q-svc,q-agt,q-dhcp,q-l3,q-meta,q-metering,neutron
	# Neutron - Load Balancing
	ENABLED_SERVICES+=,q-lbaas


### 启用Rabbitmq rabbitmq_management web 服务

执行如下命令启用rabbitmq web management 服务

	/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management

让后重启 rabbitmq

	service rabbitmq-server restart

访问页面管理界面

	http://10.20.0.210:15672

登录管理界面,查看rabbitmq 的队列使用情况

	guest/openstack

另外也可以用命令行方式查看

	rabbitmqctl list_queues




