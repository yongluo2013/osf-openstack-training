
#Neutron SDN 手动实现手册

声明：本博客欢迎转发，但请保留原作者信息!      
作者：[罗勇] 云计算工程师、敏捷开发实践者    
博客：[http://yongluo2013.github.io/](http://yongluo2013.github.io/)    
微博：[http://weibo.com/u/1704250760/](http://weibo.com/u/1704250760/)  

##安装架构介绍

本文旨在通过自己搭建类似neutron （openvswitch + gre） 实现SDN 的环境，学习了解其工作原理，模拟核心原理，比如：同一租户自定义网络 instance 互通，手动为instance 分配 floating ip 等相关内容。


![mock neutron architecture](/installation/images/mock-neutron-arch.png)


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

需要新建2个虚拟机VM1和VM2，其对应配置如下。

	VM1：
		Name : network1
		vCPU:1
		Memory :1G
		Disk:30G
		Network:net1,net2,net3

	VM2：
		Name: compute1
		vCPU:1
		Memory :1G
		Disk:30G
		Networks:net1,net2,net3


###Linux interface设置

	network1
	     eth0:10.20.0.201   (management network)
	     eht1:172.16.0.201   (public/external network)
	     eht2:192.168.4.201  (private network，gre tunning)

	compute1
	     eth0:10.20.0.202   (management network)
	     eht1:(disabled)
	     eht2:192.168.4.202  (private network，gre tunning)


##模拟安装网络节点(Network1)

模拟Network 节点相关实现，比如L3、dhcp-agent实现，为了模拟多节点网络情况，这里Network同时也模拟一个计算节点，模拟M2 openvswitch 实现，上面运行instance1。

网络接口配置

	vi /etc/sysconfig/network-scripts/ifcfg-eth0
	DEVICE=eth0
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=10.20.0.201
	NETMASK=255.255.255.0

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	DEVICE=eth1
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=172.16.0.201
	NETMASK=255.255.255.0

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	DEVICE=eth2
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=192.168.4.201
	NETMASK=255.255.255.0

重启网络服务

	service network restart

安装需要用到的包

	yum install libvirt openvswitch python-virtinst xauth tigervnc -y

移除默认的libvirt 网络，方便清晰分析网络情况

	virsh net-destroy default
	virsh net-autostart --disable default
	virsh net-undefine default

设置允许ipforwarding

	vi /etc/sysctl.conf 
	net.ipv4.ip_forward=1
	net.ipv4.conf.all.rp_filter=0
	net.ipv4.conf.default.rp_filter=0

立即生效

	sysctl -p

启动openvswitch

	service openvswitch start
	chkconfig openvswitch on


创建一个linux bridge

	brctl addbr qbr01
	ip link set qbr01 up

创建一个instance，并连接到qbr01 Bridge，网络接口部分配置如下

	<interface type='bridge'>
	      <source bridge='qbr01'/>
	      <target dev='tap01'/>
	      <model type='virtio'/>
	      <driver name='qemu'/>
	      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
	</interface>

可以参考附件./gre/instance1.xml创建

	cp ~/gre/ /var/tmp/
	cd /var/tmp/gre
	mv cirros-0.3.0-x86_64-disk.img instance1.img
	virsh define instance1.xml
	virsh start instance1
	virsh vncdisplay instance1
	vncviewer :0

启动console 以后,登录添加ip 地址 192.168.1.11

	ip addr add 192.168.1.11/24 dev eth0
	route add default gw 192.168.1.1


创建一个内部bridge br-int， 模拟 OpenStack integrated bridge

	ovs-vsctl add-br br-int
	ovs-vsctl add-port br-int gre0 -- set interface gre0 type=gre options:remote_ip=192.168.4.202

创建一个veth peer，连接Linux Bridge 'qbr01' 和  OpenvSwich Bridge 'br-ini'

	ip link add qvo01 type veth peer name qvb01
	brctl addif qbr01 qvb01
	ovs-vsctl add-port br-int qvo01
	ovs-vsctl set port qvo01 tag=100
	ip link set qvb01 up
	ip link set qvo01 up

查看现在network1上的 br-int

	ovs-vsctl show

##模拟安装计算节点(compute1)

##网络接口配置

	vi /etc/sysconfig/network-scripts/ifcfg-eth0
	DEVICE=eth0
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=10.20.0.202
	NETMASK=255.255.255.0

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	DEVICE=eth1
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=172.16.0.202
	NETMASK=255.255.255.0

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	DEVICE=eth2
	TYPE=Ethernet
	ONBOOT=yes
	NM_CONTROLLED=yes
	BOOTPROTO=static
	IPADDR=192.168.4.202
	NETMASK=255.255.255.0

重启网络服务

	service network restart

安装需要用到的包

	yum install libvirt openvswitch python-virtinst xauth tigervnc

移除libvirt 默认的网络

	virsh net-destroy default
	virsh net-autostart --disable default
	virsh net-undefine default

设置允许ipforwarding

	vi /etc/sysctl.conf 
	net.ipv4.ip_forward=1
	net.ipv4.conf.all.rp_filter=0
	net.ipv4.conf.default.rp_filter=0

立即生效

	sysctl -p

启动openvswitch

	service openvswitch start
	chkconfig openvswitch on


创建一个linux bridge

	brctl addbr qbr02
	ip link set qbr02 up

创建一个vm，并连接到qbr02

<interface type='bridge'>
      <source bridge='qbr02'/>
      <target dev='tap02'/>
      <model type='virtio'/>
      <driver name='qemu'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
</interface>

上gre目录到compute1 节点，可以参考附件./gre/instance2.xml创建

	cp ~/gre/ /var/tmp/
	cd /var/tmp/gre
	mv cirros-0.3.0-x86_64-disk.img instance2.img
	virsh define instance2.xml
	virsh start instance2
	virsh vncdesplay instance2
	vncviewer :0

启动console 以后,登录添加ip得知 192.168.1.12

	ip addr add 192.168.1.12/24 dev eth0
	route add default gw 192.168.1.1 


创建一个内部bridge br-int， 模拟 OpenStack integrated bridge

	ovs-vsctl add-br br-int
	ovs-vsctl add-port br-int gre0 -- set interface gre0 type=gre options:remote_ip=192.168.4.201

创建一个veth peer，连接Linux Bridge 'qbr02' 和  OpenvSwich Bridge 'br-ini'

	ip link add qvo02 type veth peer name qvb02
	brctl addif qbr02 qvb02
	ovs-vsctl add-port br-int qvo02
	ovs-vsctl set port qvo02 tag=100
	ip link set qvb02 up
	ip link set qvo02 up


查看现在network1 上的 br-int

	ovs-vsctl show


检查是否能连通instance1，在instance2的控制台

	ping 192.168.1.11


##通过 Network Namespace 实现租户私有网络互访

添加一个namespace，dhcp01用于隔离租户网络。

	ip netns add dhcp01

为私有网络192.168.1.0/24 ，在命名空间dhcp01 中 创建dhcp 服务

	ovs-vsctl add-port br-int tapdhcp01 -- set interface tapdhcp01 type=internal
	ovs-vsctl set port tapdhcp01 tag=100

	ip link set tapdhcp01 netns dhcp01
	ip netns exec dhcp01 ip addr add 192.168.1.2/24 dev tapdhcp01
	ip netns exec dhcp01 ip link set tapdhcp01 up

检查网络是否连通，在namespace 访问instance1 和 instance2

	ip netns exec dhcp01 ping 192.168.1.12
	ip netns exec dhcp01 ping 192.168.1.11


##通过 Network Namespace 和Iptables 实现L3 router

ovs-vsctl add-br br-ex

重新配置eth1 和 br-ex

	vi /etc/sysconfig/network-scripts/ifcfg-eth1

	DEVICE=eth1
	ONBOOT=yes
	BOOTPROTO=none
	PROMISC=yes
	MTU=1546

	vi /etc/sysconfig/network-scripts/ifcfg-br-ex

	DEVICE=br-ex
	TYPE=Bridge
	ONBOOT=yes
	BOOTPROTO=none
	IPADDR0=172.16.0.201
	PREFIX0=24

重启启动网络服务

	ovs-vsctl add-port br-ex eth1 && service network restart

检查网络，配置后是否连通

	ping 172.16.0.201
	

添加一个namespace，router01 用于路由和floating ip 分配

	ip netns add router01

在br-int添加一个接口，作为私有网络192.168.1.0/24的网关

	ovs-vsctl add-port br-int qr01 -- set interface qr01 type=internal
	ovs-vsctl set port qr01 tag=100

	ip link set qr01 netns router01
	ip netns exec router01 ip addr add 192.168.1.1/24 dev qr01
	ip netns exec router01 ip link set qr01 up
	ip netns exec router01 ip link set lo up

在br-ex中添加一个接口，用于私网192.168.1.0/24设置下一跳地址

	ovs-vsctl add-port br-ex qg01 -- set interface qg01  type=internal
	ip link set qg01  netns router01
	ip netns exec router01 ip addr add 172.16.0.100/24 dev qg01 
	ip netns exec router01 ip link set qg01 up
	ip netns exec router01 ip link set lo up

## 模拟分配floating ip 访问instance1

为instance1 192.168.1.11 分配floating ip，172.16.0.101

	ip netns exec router01 ip addr add 172.16.0.101/32 dev qg01 

	ip netns exec router01  iptables -t nat -A OUTPUT -d 172.16.0.101/32  -j DNAT --to-destination 192.168.1.11
	ip netns exec router01  iptables -t nat -A PREROUTING -d 172.16.0.101/32 -j DNAT --to-destination 192.168.1.11
	ip netns exec router01  iptables -t nat -A POSTROUTING -s 192.168.1.11/32 -j SNAT --to-source 172.16.0.101
	ip netns exec router01  iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -j SNAT --to-source 172.16.0.100

测试floating ip

	ping 172.16.0.101

如果需要清除nat chain 

	iptables -t nat -F


