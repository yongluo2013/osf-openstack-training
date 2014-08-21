#网络知识盘点实例

声明：本博客欢迎转发，但请保留原作者信息!      
作者：[罗勇] 云计算工程师、敏捷开发实践者    
博客：[http://yongluo2013.github.io/](http://yongluo2013.github.io/)    
微博：[http://weibo.com/u/1704250760/](http://weibo.com/u/1704250760/)  

##练习介绍

熟悉Neutron 部分需要用到的几个基本的网络知识点，通过练习体会原理及方法。

##环境配置

网络接口

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
	BOOTPROTO=static
	IPADDR=192.168.4.10
	NETMASK=255.255.255.0

重启网络服务

	service network restart

##练习1

创建一个network namespace foo

	ip netns add foo

查看network namespace

	ip netns

创建一个vethp 

	ip link add tap-foo type veth peer name tap-root

将tap-foo分配到foo namespace中

	ip link set tap-foo  netns foo

为tap-foo 添加一个ip地址

	ip netns exec foo ip addr add 192.168.10.2/24 dev tap-foo 
	ip netns exec foo ip link set tap-foo up

查看foo 空间中的网卡信息

	ip netns exec foo ip a

为root namespace 中的tap-root添加ip

	 ip addr add 192.168.10.1/24 dev tap-root
	 ip netns exec foo ip link set tap-root up


查看 root 空间中的网卡信息

 	ip a

 检查是否网络连通

	 ping 192.168.10.2

	 ip netns exec foo ping 192.168.10.1


 ##练习2

 安装需要用到的包

	yum install libvirt openvswitch python-virtinst xauth tigervnc -y

移除默认的libvirt 网络，方便清晰分析网络情况

	virsh net-destroy default
	virsh net-autostart --disable default
	virsh net-undefine default

启动openvswitch

	service openvswitch start
	chkconfig openvswitch on

创建一个openvswitch bridge 名字叫br-int

	ovs-vsctl add-br br-int

利用openvswitch 的 br-int，定义一个libvirt 网络

	vi libvirt-vlans.xml
	<network>
	  <name>ovs-network</name>
	  <forward mode='bridge'/>
	  <bridge name='br-int'/>
	  <virtualport type='openvswitch'/>
	  <portgroup name='no-vlan' default='yes'>
	  </portgroup>
	  <portgroup name='vlan-100'>
	    <vlan>
	      <tag id='100'/>
	    </vlan>
	  </portgroup>
	  <portgroup name='vlan-200'>
	    <vlan>
	      <tag id='200'/>
	    </vlan>
	  </portgroup>
	</network>

启动libvirt 网络

	virsh net-define libvirt-vlans.xml
	virsh net-autostart ovs-network
	virsh net-start ovs-network

创建一个instance，并连接到ovs-network，网络接口部分配置如下

	<interface type='network'>
	  <source network='ovs-network' portgroup='vlan-100'/>
	  <model type='virtio'/>
	</interface>

可以参考附件instance1.xml创建

	cp ~/gre/ /var/tmp/
	cd /var/tmp/gre
	mv cirros-0.3.0-x86_64-disk.img instance1.img
	virsh define instance1.xml
	virsh start instance1
	virsh vncdesplay instance1
	vncviewer :0

启动console 以后,登录添加ip得知 192.168.1.20

	ip addr add 192.168.1.20/24 dev eth0

添加一个openvswitch port 

	ip link add br-int-tap100 type veth peer name tap100
	ovs-vsctl add-port br-int br-int-tap100
	ovs-vsctl set port br-int-tap100 tag=100
	ip addr add 192.168.1.21/24 dev tap100
	ip link set tap100 up
	ip link set br-int-tap100 up











