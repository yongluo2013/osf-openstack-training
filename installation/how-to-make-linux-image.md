#如何自制OpenStack Linux 镜像

声明：本博客欢迎转发，但请保留原作者信息!      
作者：[罗勇] 云计算工程师、敏捷开发实践者    
博客：[http://yongluo2013.github.io/](http://yongluo2013.github.io/)    
微博：[http://weibo.com/u/1704250760/](http://weibo.com/u/1704250760/)  

##基本概念

略

##基本制作步骤

* VM's OS installation
* No hard-coded MAC address information
* SSH server running
* Disable firewall
* Disk partitions and resize root partition on boot (cloud-init)
* Access instance using ssh public key (cloud-init)
* Process user data and other metadata (cloud-init)

###KVM 以及libvirt 安装

安装操作系统的时候选择virtualization server 这个package group 进行安装。kvm 已经默认包含在linux kernel中了。



检查kvm是否正确安装

	/usr/libexec/qemu-kvm -version

检查libvirt 是否启动

	/etc/init.d/libvirtd status

安装tigervnc 和 xauth，用于vnc 显示vm console

	sudo yum install tigervnc xauth -y

可以直接使用默认的“default” 网络，不过为了清楚起见，创建自己的虚拟网络 “my-net”
	
	vi my-net.xml

	<network>
	  <name>my-net</name>
	  <uuid>6f801f5d-f9b6-480f-81a7-f177e3555b99</uuid>
	  <forward mode='nat'/>
	  <bridge name='my_net' stp='on' delay='0' />
	  <mac address='52:54:00:0F:ED:99'/>
	  <ip address='192.168.10.1' netmask='255.255.255.0'>
	    <dhcp>
	      <range start='192.168.10.2' end='192.168.10.254' />
	    </dhcp>
	  </ip>
	</network>

	virsh net-define my-net.xml
	virsh net-list --all
	virsh net-start my-net

查看libvirt 生成的Network 描述文件。

	vi /etc/libvirt/qemu/networks/my-net.xml

####创建磁盘

	qemu-img create -f qcow2 rhel-test.img 10G

####创建虚拟机

	virt-install --name rhel-test --hvm  --ram 2048  --vcpus 2  --disk path=/var/tmp/rhel-test.img,size=10,bus=virtio,format=qcow2 --network network:my-net --accelerate --vnc --vncport=5908  --cdrom /var/tmp/CentOS-6.5-x86_64-bin-DVD1.iso  --boot cdrom


查看创建的vm，在libvirt 中被称作domain

	virsh list --all

查看vm 启动在哪个vnc port

	virsh vncdisplay rhel-test

启动vncviewer 

	vncviewer :8

查看virt 生成的vm 描述文件

	vi /etc/libvirt/qemu/rhel-test.xml

如果想关闭vm 

	virsh destroy rhel-test

彻底删除vm

	virsh undefine rhel-test

###删除硬编码网卡信息

登录guest 系统，删除网卡持久化信息，避免第二次启动网络不通

	 rm -f /etc/udev/rules.d/70-persistent-net.rules 

###删除所有防火墙规则

清除iptables 规则，运行所有数据包可进可出

	vi /etc/sysconfig/iptables

	*filter
	:INPUT ACCEPT [0:0]
	:FORWARD ACCEPT [0:0]
	:OUTPUT ACCEPT [0:0]
	COMMIT

重启iptables 

	service iptables restart


###安装cloud-ini 工具包

略

###默认启动SSH服务

略

###开机自动resize 跟分区

略

###设置用SSH 秘钥对访问实例

略


