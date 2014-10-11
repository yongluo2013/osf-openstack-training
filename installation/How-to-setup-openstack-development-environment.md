##开发环境搭建

###基本需求

通常说搭建好开发环境，我们要完成如下内容。

*　安装一个好用的IDE，起码应该支持语法检查、高显示

*　可以单步调试 OpenStack 源码，最好支持远程调试

*　可以跑通单元测试

*　可以跑通接口测试

###Centos 桌面版安装 （可选）

	yum groupinstall -y "X Window System"
	yum groupinstall -y "KDE Desktop"
	startkde

###也可以直接使用X11 + Xmanager 远程显示

具体如何使用请参见视频

###配置Eclipse


下载安装Eclipse

	https://www.eclipse.org/downloads/download.php?file=/technology/epp/downloads/release/luna/SR1/eclipse-java-luna-SR1-linux-gtk-x86_64.tar.gz

安装pydev 和egit 插件

	http://pydev.org/updates
	http://download.eclipse.org/egit/updates

安装完毕以后重启Eclipse

参考资料

	http://debugopenstack.blogspot.com/
	https://wiki.openstack.org/wiki/Setup_keystone_in_Eclipse
	http://pydev.org/manual_adv_remote_debugger.html

### 运行单元测试

安装 openstack 开发环境依赖包

	sudo yum install python-devel openssl-devel python-pip git gcc libxslt-devel mysql-devel postgresql-devel libffi-devel libvirt-devel graphviz sqlite-devel

	sudo pip install tox

检出nova 源代码

	git clone https://git.openstack.org/openstack/nova
	cd nova

运行nova unit tests，第一次运行这里比较慢大概需要30分钟

	tox -e py26

运行nova 的代码样式检查

	tox -e pep8

一起运行，用逗号隔开

	tox -e py26,pep8


运行测试套件

	tox -e py26 nova.tests.scheduler

pip 方式安装 Python  package


###运行集成测试

devstack 安装openstack


devstack 的安装不能直接用root 用户，新建一个用户stack

	adduser -m stack
	su - stack
	git clone  https://github.com/openstack-dev/devstack.git

如果需要设置代理，请添加proxy

	export http_proxy=http://www-proxy.exu.ericsson.se:8080
	export https_proxy=http://www-proxy.exu.ericsson.se:8080

排除不需要代理的IP地址

	export no_proxy="127.0.0.1,192.168.1.205"


为了加速下载设置国内的pip 源，这里设置豆瓣的源

	mkdir ~/.pip
	cat > ~/.pip/pip.conf <<EOF
	[global]
	index-url = https://pypi.douban.com/simple/
	EOF

还要为pypi.douban.com 添加ip 映射 125.78.248.73 

	vi  /etc/hosts
	125.78.248.73 pypi.python.org

根据环境修改devstack 安装配置文件（安装大概需要一个小时）

	vi local.conf

	[[local|localrc]]
	HOST_IP=192.168.1.205
	LOGDAYS=1
	LOGFILE=$DEST/logs/stack.sh.log
	SCREEN_LOGDIR=$DEST/logs/screen
	ADMIN_PASSWORD=quiet
	DATABASE_PASSWORD=$ADMIN_PASSWORD
	RABBIT_PASSWORD=$ADMIN_PASSWORD
	SERVICE_PASSWORD=$ADMIN_PASSWORD
	SERVICE_TOKEN=$ADMIN_PASSWORD
	GIT_BASE=https://github.com
	DIB_BRANCH=stable/icehouse


可能存在的问题


[[local|localrc]]

HOST_IP=192.168.1.205
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



或者


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



遇到的问题

1.git clone 失败问题


2.安装过程中检查q-dhcp 服务没有启动，查看/var/log/neutron/dhcp-agent.log，确认是否有以下错误出现：

2013-11-15 17:18:07.785 9808 WARNING neutron.agent.linux.dhcp [-] FAILED VERSION REQUIREMENT FOR DNSMASQ. DHCP AGENT MAY NOT RUN CORRECTLY! Please ensure that its version is 2.59 or above!
RuntimeError:
2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Command: ['sudo', 'neutron-rootwrap', '/etc/neutron/rootwrap.conf', 'ip', 'netns', 'add', 'qdhcp-85c85884-3d8f-4f2a-8f81-97f1aa686837']
2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Exit code: 255
2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Stdout: ''
2013-11-15 18:02:39.974 9808 TRACE neutron.agent.dhcp_agent Stderr: 'Bind /proc/self/ns/net -> /var/run/netns/qdhcp-85c85884-3d8f-4f2a-8f81-97f1aa686837 failed: No such file or directory\n'

解决办法：下载并安装新版本的dnsmasq

wget http://pkgs.repoforge.org/dnsmasq/dnsmasq-2.65-1.el6.rfx.x86_64.rpm
rpm -Uvh dnsmasq-2.65-1.el6.rfx.x86_64.rpm




