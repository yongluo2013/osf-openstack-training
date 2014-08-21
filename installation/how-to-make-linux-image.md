#如何自制OpenStack Linux 镜像

##基本概念

##基本制作步骤

* No hard-coded MAC address information
* SSH server running
* Disable firewall
* Disk partitions and resize root partition on boot (cloud-init)
* Access instance using ssh public key (cloud-init)
* Process user data and other metadata (cloud-init)

###OS安装


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

cloud-init/cloud-tools: One ext3/ext4partition (no LVM, no /boot, no swap)

You must configure these items for your image:

• The partition table for the image describes the original size of the image

• The file system for the image fills the original size of the image Then, during the boot process, you must Modify the partition table to make it aware of the additional space.

	• If you do not use LVM, you must modify the table to extend the existing root partition to encompass this additional space.
	• If you use LVM, you can add a new LVM entry to the partition table, create a new LVM physical volume, add it to the volume group, and extend the logical partition with the root volume.

• Resize the root volume file system.

The simplest way to support this in your image is to install the cloud-utils package (contains the growpart tool for extending partitions), the cloud-initramfs-growroot package (which supports resizing root partition on the first boot), and the cloud-init package into your
image. With these installed, the image performs the root partition resize on boot. For example, in the /etc/rc.local file. These packages are in the Ubuntu and Debianpackage repository, as well as the EPEL repository (for Fedora/RHEL/CentOS/Scientific
Linux guests).
If you cannot install cloud-initramfs-tools, Robert Plestenjak has a github project called linux-rootfs-resize that contains scripts that update a ramdisk by using growpart so that the image resizes properly on boot.
If you can install the cloud-utils and cloud-init packages, we recommend that when you create your images, you create a single ext3 or ext4 partition (not managed by LVM).

