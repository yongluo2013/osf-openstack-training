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

首先安装 openstack 开发环境依赖包

	sudo yum install python-devel openssl-devel python-pip git gcc libxslt-devel mysql-devel postgresql-devel libffi-devel libvirt-devel graphviz sqlite-devel

用pip 安装tox工具

	sudo pip install tox

检出nova 源代码

	git clone https://git.openstack.org/openstack/nova
	cd nova

运行nova unit tests，第一次运行这里比较慢大概需要30分钟

	tox -e py26

运行nova 的代码样式检查

	tox -e pep8

如果需要多环境一起运行，用逗号隔开

	tox -e py26,pep8

运行特定的测试套件

	tox -e py26 nova.tests.scheduler

###运行集成测试

集成测试，主要是针对 OpenStack 各个API的黑盒测试，通常用于功能测试，同时也是CI 的基本保护网之一，在新的代码变化merge 到master之前每个有效的case必须都是pass。

前提，必须先用devstack 安装好openstack，相应服务启动正常。

检查tempest 配置文件

su - stack
cd /opt/stack/tempest
vi etc/tempest.conf

安装devstack 的时候已经自动配置好tempest 配置文件


运行单独一个测试用例

	./run_tempest.sh -N tempest.api.compute.servers.test_servers_negative.ServersNegativeTestJSON.test_reboot_non_existent_server


运行一个包下的case

 	./run_tempest.sh -N -- tempest.api.compute.flavors



###Keystone 远程调试

Eclipse 配置端配置

1. 添加 /opt/eclipse/plugins/org.python.pydev_3.8.0.201409251235/pysrc 被调试项目Python pach 中（可选）

2. 运行pydev debug 


远程Keystone 服务器配置

3. 拷贝Eclipse Dydev 插件下 pysrc 目录到 Keystone 机器上，并添加该目录到Python pach

	export PYTHONPATH=$PYTHONPATH:/opt/eclipse/plugins/org.python.pydev_3.8.0.201409251235/pysrc

4. 在需要打断点的地方添加如下代码

	import pysrc.pydevd as pydevd;pydevd.settrace('10.20.0.210',stdoutToServer=True, stderrToServer=True)

5.单步调试

参考文档

	http://pydev.org/manual_adv_remote_debugger.html
























