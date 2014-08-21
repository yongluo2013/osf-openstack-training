#如何自制OpenStack Linux 镜像

声明：本博客欢迎转发，但请保留原作者信息!      
作者：[罗勇] 云计算工程师、敏捷开发实践者    
博客：[http://yongluo2013.github.io/](http://yongluo2013.github.io/)    
微博：[http://weibo.com/u/1704250760/](http://weibo.com/u/1704250760/)  

##基本概念

##基本制作步骤

* No hard-coded MAC address information
* SSH server running
* Disable firewall
* Disk partitions and resize root partition on boot (cloud-init)
* Access instance using ssh public key (cloud-init)
* Process user data and other metadata (cloud-init)

###OS安装

略

###创建网络vnet4

	virtsh net-define vnet4.xml 

####创建磁盘

	qemu-img create -f qcow2 image-test.img 10G

####创建虚拟机

	virt-install --name image-test  --hvm  --ram 2048  --vcpus 2  --disk path=/var/tmp/image-test.img,size=10,bus=virtio,format=qcow2 --network network:default --accelerate --vnc --vncport=5908  --cdrom /var/tmp/CentOS-6.5-x86_64-bin-DVD1.iso  --boot cdrom

###VNC viewer 访问console
	vncviewer 5922

###删除硬编码网卡信息
###删除所有防火墙规则
###默认启动SSH服务
###开机自动resize 跟分区
###设置用SSH 秘钥对访问实例


