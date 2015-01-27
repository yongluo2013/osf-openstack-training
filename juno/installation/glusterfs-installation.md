##glusterFS installation

##环境准备

storage0

	vi /etc/hosts
	10.0.0.40 storage0
	10.0.0.41 storage1

storage1

	vi /etc/hosts
	10.0.0.40 storage0
	10.0.0.41 storage1

###网络拓扑设计

management network
	
	10.0.0.0/24

tunnel network

	10.0.0.1/24

external network

	203.0.113.0/24

storage network

	10.0.0.2/24

storage0 网络配置如下

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	DEVICE=eth0
	BOOTPROTO=static
	IPADDR=10.0.0.40
	NETMASK=255.255.255.0
	GATEWAY=10.20.0.1
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	DEVICE=eth1
	BOOTPROTO=static
	IPADDR=10.0.1.40
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	TYPE=Ethernet
	DEVICE=eth2
	BOOTPROTO=static
	IPADDR=203.0.113.40
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth3
	TYPE=Ethernet
	DEVICE=eth3
	BOOTPROTO=static
	IPADDR=10.0.3.40
	NETMASK=255.255.255.0
	ONBOOT=yes


storage1 网络配置如下

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	DEVICE=eth0
	BOOTPROTO=static
	IPADDR=10.0.0.41
	NETMASK=255.255.255.0
	GATEWAY=10.20.0.1
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	DEVICE=eth1
	BOOTPROTO=static
	IPADDR=10.0.1.41
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth2
	TYPE=Ethernet
	DEVICE=eth2
	BOOTPROTO=static
	IPADDR=203.0.113.41
	NETMASK=255.255.255.0
	ONBOOT=yes

	vi /etc/sysconfig/network-scripts/ifcfg-eth3
	TYPE=Ethernet
	DEVICE=eth3
	BOOTPROTO=static
	IPADDR=10.0.3.41
	NETMASK=255.255.255.0
	ONBOOT=yes

##存储节点安装

新磁盘分区为/dev/vdb1

	sudo fdisk /dev/vdb

安装 mkfs.xfs 工具

	yum install kmod-xfs xfsdump xfsprogs dmapi
	
	sudo mkfs.xfs -i size=512 /dev/vdb1

	sudo  mkdir -p /export/vdb1 && mount /dev/vdb1 /export/vdb1 && mkdir -p /export/vdb1/brick
    
	sudo echo "/dev/vdb1 /export/vdb1 xfs defaults 0 0"  >> /etc/fstab

安装glusterfs server

	curl http://download.gluster.org/pub/gluster/glusterfs/LATEST/CentOS/glusterfs-epel.repo -o /etc/yum.repos.d/glusterfs-epel.repo 
	sudo yum install glusterfs{,-server,-fuse,-geo-replication}
	systemctl start glusterd 
	systemctl enable glusterd 

登录storage0，执行

	gluster peer probe storage1
	gluster peer status 
    gluster volume create testvol rep 2 transport tcp storage0:/export/vdb1/brick storage1:/export/vdb1/brick
    gluster volume start testvol

##客户端安装

    yum install glusterfs-fuse
    sudo mkdir /mnt/gluster; 
    mount -t glusterfs storage0:/testvol /mnt/gluster; 
    cp -r /var/log /mnt/gluster
    mkdir /mnt/gluster/hello_world
	df -h