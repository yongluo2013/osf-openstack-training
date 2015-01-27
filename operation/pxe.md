# PXE OS自动安装

##环境准备

虚拟机准备

VM1：
	cpu：1 core
	memory： 1G
	disk：30G
	network：
	    eth0：VirtualBox Host-Only Ethernet Adapter #2,
	    eth1:NAT
VM2：
	cpu：1 core
	memory： 1G
	disk：8G
	network：
	    eth0：VirtualBox Host-Only Ethernet Adapter #2,
	    eth1:NAT

网络准备

	 VirtualBox Host-Only Ethernet Adapter #2  =>  10.0.0.0/24
vm1：
	10.0.0.2/24

	vi /etc/sysconfig/network-scripts/ifcfg-eth0 
	TYPE=Ethernet
	BOOTPROTO=static
	DEVICE=eth0
	ONBOOT=yes
	IPADDR=10.0.0.2
	NETMASK=255.255.255.0

	vi /etc/sysconfig/network-scripts/ifcfg-eth1
	TYPE=Ethernet
	BOOTPROTO=dhcp
	NAME=eth1
	ONBOOT=yes

vm2(裸机)：

	网络pxe 自动配置


centos7 iso 镜像文件准备

下载并导入vm 的光驱中，待后续使用。

文件名：

	CentOS-7.0-1406-x86_64-DVD.iso 

下载地址：

	http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7.0-1406-x86_64-DVD.iso 

## dhcp server 安装

安装dhcp serve 的软包

	yum install dhcp -y

	vi  /etc/dhcp/dhcpd.conf 

	default-lease-time 6000;
	max-lease-time 7200;

	subnet 10.0.0.0 netmask 255.255.255.0 {
	  range 10.0.0.200 10.0.0.210;
	  option routers 10.0.0.1;
	  next-server 10.0.0.2;
	  filename "pxelinux.0";
	}


启动一个裸机验证是否能获取ip地址。

## tftp server 安装

	yum install tftp-server tftp -y

安装TFTP服务,将/etc/xintetd.d/tftp文件中的disable改为no,接着启动xinetd服务

	service tftp
	{
	        socket_type             = dgram
	        protocol                = udp
	        wait                    = yes
	        user                    = root
	        server                  = /usr/sbin/in.tftpd
	        server_args             = -s /var/lib/tftpboot
	        disable                 = no
	        per_source              = 11
	        cps                     = 100 2
	        flags                   = IPv4
	}

	systemctl start xinetd
	systemctl enable xinetd	


安装syslinux 软件包，准备安装pex 引导文件

	yum install syslinux

	cp /usr/share/syslinux/pxelinux.0 /var/lib/tftpboot
	mount /dev/cdrom /mnt/
	cp /mnt/pxeboot/{initrd.img,vmlinuz} /var/lib/tftpboot/
	mkdir /var/lib/tftpboot/pxelinux.cfg
	cp /usr/share/syslinux/vesamenu.c32 /var/lib/tftpboot/	
	cp /usr/share/syslinux/pxelinux.0 /var/lib/tftpboot/
	cp /usr/share/syslinux/menu.c32 /var/lib/tftpboot/
	cp /usr/share/syslinux/memdisk /var/lib/tftpboot/
	cp /usr/share/syslinux/mboot.c32 /var/lib/tftpboot/
	cp /usr/share/syslinux/chain.c32 /var/lib/tftpboot/

创建 PXE 菜单文件

	vi /var/lib/tftpboot/pxelinux.cfg/default

	 default menu.c32
	 prompt 0
	 timeout 30
	 MENU TITLE unixme.com PXE Menu

	 LABEL centos7_x64
	 MENU LABEL CentOS 7 X64
	 KERNEL vmlinuz
	 APPEND initrd=initrd.img  inst.repo=http://10.0.0.2  ks=http://10.0.0.2/ks.cfg


重启vm2（裸机），验证boot 菜单是否能成功启动

## http media 和kickstart 文件准备

安装httpd

	yum install -y httpd

从已经mount的iso镜像文件内全拷贝到httpd 发布目录，准备安os装树

   cp -r /mnt /var/www/html

先准备root 加密密码

	openssl passwd -1 "000000"
    $1$XOtfN2Mg$Z4dNRpORuR6Lcj2FnEhnN0

准备kickstart 文件

	vi /var/www/html/ks.cfg

	#platform=x86, AMD64, or Intel EM64T
	#version=DEVEL
	# Firewall configuration
	firewall --disabled
	# Install OS instead of upgrade
	install
	# Use NFS installation media
	url --url="http://10.0.0.2"
	# Root password [i used here 000000]
	rootpw --iscrypted $1$XOtfN2Mg$Z4dNRpORuR6Lcj2FnEhnN0
	# System authorization information
	auth  useshadow  passalgo=sha512
	# Use graphical install
	graphical
	firstboot disable
	# System keyboard
	keyboard us
	# System language
	lang en_US
	# SELinux configuration
	selinux disabled
	# Installation logging level
	logging level=info
	# System timezone
	timezone Europe/Amsterdam
	# System bootloader configuration
	bootloader location=mbr
	clearpart --all --initlabel
	part swap --asprimary --fstype="swap" --size=1024
	part /boot --fstype xfs --size=200
	part pv.01 --size=1 --grow
	volgroup rootvg01 pv.01
	logvol / --fstype xfs --name=lv01 --vgname=rootvg01 --size=1 --grow
	%packages
	@core
	wget
	net-tools
	%end
	%post
	%end

另外，也可通过system-config-kickstart 工具，通过图形化方式生成kickstart 文件

	yum install -y system-config-kickstart 

	system-config-kickstart /var/www/html/ks.cfg


参考:

	http://www.unixmen.com/install-pxe-server-centos-7/ 

== kickstart 语法

	http://fedoraproject.org/wiki/Anaconda/Kickstart