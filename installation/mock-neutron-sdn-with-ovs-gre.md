
##安装架构介绍

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
		Name : network0
		vCPU:1
		Memory :1G
		Disk:30G
		Network:net1,net2,net3

	VM2：
		Name: compute0
		vCPU:1
		Memory :1G
		Disk:30G
		Networks:net1,net2,net3


###Linux interface设置

	network0
	     eth0:10.20.0.201   (management network)
	     eht1:172.16.0.201   (public/external network)
	     eht2:192.168.4.201  (private network，gre tunning)

	compute0
	     eth0:10.20.0.202   (management network)
	     eht1:(disabled)
	     eht2:192.168.4.202  (private network，gre tunning)


##模拟安装网络节点(Network0)

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

启动openvswitch

	service openvswitch start
	chkconfig openvswitch on


创建一个linux bridge

	brctl addbr qbr001
	ip link set qbr001 up

创建一个instance，并连接到qbr001 Bridge，网络接口部分配置如下

	<interface type='bridge'>
	      <source bridge='qbr001'/>
	      <target dev='tap001'/>
	      <model type='virtio'/>
	      <driver name='qemu'/>
	      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
	</interface>

可以参考附件instance1.xml创建

	cp ~/gre/ /var/tmp/
	cd /var/tmp/gre
	mv cirros-0.3.0-x86_64-disk.img instance1.img
	virsh define instance1.xml
	virsh start instance1
	virsh vncdesplay instance1
	vncviewer :0

启动console 以后,登录添加ip得知 192.168.1.11

	ip addr add 192.168.1.11/24 dev eth0


创建一个内部bridge br-int， 模拟 OpenStack integrated bridge

	ovs-vsctl add-br br-int
	ovs-vsctl add-port br-int gre0 -- set interface gre0 type=gre options:remote_ip=192.168.4.202

创建一个veth peer，连接Linux Bridge 'qbr001' 和  OpenvSwich Bridge 'br-ini'

	ip link add qvo001 type veth peer name qvb001
	brctl addif qbr001 qvb001
	ovs-vsctl add-port br-int qvo001
	ovs-vsctl set port qvo001 tag=100
	ip link set qvb001 up
	ip link set qvo001 up

查看现在network0 上的 br-int

	ovs-vsctl show

##模拟安装计算节点(compute0)

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

启动openvswitch

	service openvswitch start
	chkconfig openvswitch on


创建一个linux bridge

	brctl addbr qbr002
	ip link set qbr002 up

创建一个vm，并连接到qbr002

<interface type='bridge'>
      <source bridge='qbr002'/>
      <target dev='tap002'/>
      <model type='virtio'/>
      <driver name='qemu'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
</interface>

上gre目录到compute0 节点，可以参考附件instance2.xml创建

	cp ~/gre/ /var/tmp/
	cd /var/tmp/gre
	mv cirros-0.3.0-x86_64-disk.img instance2.img
	virsh define instance2.xml
	virsh start instance2
	virsh vncdesplay instance2
	vncviewer :0

启动console 以后,登录添加ip得知 192.168.1.12

	ip addr add 192.168.1.12/24 dev eth0


创建一个veth peer，连接qbr002和br-ini

	ip link add qvo002 type veth peer name qvb002
	brctl addif qbr002 qvb002
	ovs-vsctl add-port br-int qvo002
	ovs-vsctl set port qvo002 tag=100
	ip link set qvb002 up
	ip link set qvo002 up

创建一个内部bridge br-int， 模拟 OpenStack integrated bridge

	ovs-vsctl add-br br-int
	ovs-vsctl add-port br-int gre0 -- set interface gre0 type=gre options:remote_ip=192.168.4.201

查看现在network0 上的 br-int

	ovs-vsctl show


检查是否能连通instance1，在instance2的控制台

	ping 192.168.1.11


##实现基于namespace 实现租户私有网络互访

添加一个namespace，dhcp001用于隔离租户网络。

	ip netns add dhcp001

为私有网络192.168.1.0/24 ，在命名空间dhcp001 中 创建dhcp 服务

	ovs-vsctl add-port br-int tapdhcp001 -- set interface tapdhcp001 type=internal
	ovs-vsctl set port tapdhcp001 tag=100

	ip link set tapdhcp001 netns dhcp001
	ip netns exec dhcp001 ip addr add 192.168.1.2/24 dev tapdhcp001
	ip netns exec dhcp001 ip link set tapdhcp001 up

检查网络是否连通，在namespace 访问instance1 和 instance2

	ip netns exec dhcp001 ping 192.168.1.10
	ip netns exec dhcp001 ping 192.168.1.11


##实现基于namespace 和iptables 实现L3 router 功能，已经floating ip 访问instance1

添加一个新的bridge br-ex用于floating IP映射

	ovs-vsctl add-br br-ex

重新配置eth2 和 br-ex

	cat /etc/sysconfig/network-scripts/ifcfg-eth2

	DEVICE=eth2
	ONBOOT=yes
	BOOTPROTO=none
	PROMISC=yes
	MTU=1546

	cat /etc/sysconfig/network-scripts/ifcfg-br-ex

	DEVICE=br-ex
	TYPE=Bridge
	ONBOOT=yes
	BOOTPROTO=none
	IPADDR0=172.16.0.201
	PREFIX0=24

重启启动网络服务

	ovs-vsctl add-port br-ex eth2 && service network restart

检查网络，配置后是否连通

	ping 127.16.0.201
	ping 127.16.0.202


在br-int添加一个接口，作为私有网络192.168.1.0/24的网关

	ovs-vsctl add-port br-int qr001 -- set interface qr001 type=internal
	ovs-vsctl set port qr001 tag=100

	ip link set qr001 netns router001
	ip netns exec router001 ip addr add 192.168.1.1/24 dev qr001
	ip netns exec router001 ip link set qr001 up
	ip netns exec router001 ip link set lo up

添加一个namespace，router001 用于路由和floating ip 分配

	ip netns add router001

在br-ex中添加一个接口，用于私网192.168.1.0/24设置下一跳地址

	ovs-vsctl add-port br-ex qg001 -- set interface qg001  type=internal
	ip link set qg001  netns router001
	ip netns exec router001 ip addr add 172.16.0.100/24 dev qg001 
	ip netns exec router001 ip link set qg001 up
	ip netns exec router001 ip link set lo up

模拟为instance1 192.168.1.11 分配floating ip，172.16.0.101

	ip netns exec router001 ip addr add 172.16.0.101/32 dev qg001 

	ip netns exec router001 route add default gw 172.16.0.1 qg001

	ip netns exec router001  iptables -t nat -A OUTPUT -d 172.16.0.101/32  -j DNAT --to-destination 192.168.1.11
	ip netns exec router001  iptables -t nat -A PREROUTING -d 172.16.0.101/32 -j DNAT --to-destination 192.168.1.11
	ip netns exec router001  iptables -t nat -A POSTROUTING -s 192.168.1.11/32 -j SNAT --to-source 172.16.0.101
	ip netns exec router001  iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -j SNAT --to-source 172.16.0.100


测试floating ip

	ping 172.16.0.101

如果需要清除nat chain 

	iptables -t nat -F


