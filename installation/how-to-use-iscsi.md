## scsi-target-utils 涉及到的文件

/etc/tgt/targets.conf：主要配置文件，设定要分享的磁盘格式与哪几颗；
/usr/sbin/tgt-admin：在线查询、删除 target 等功能的设定工具；
/usr/sbin/tgt-setup-lun：建立 target 以及设定分享的磁盘与可使用的客户端等工具软件。
/usr/sbin/tgtadm：手动直接管理的管理员工具 (可使用配置文件取代)；
/usr/sbin/tgtd：主要提供 iSCSI target 服务的主程序；
/usr/sbin/tgtimg：建置预计分享的映像文件装置的工具 (以映像文件仿真磁盘)；

##设定 tgt 

配置文件 /etc/tgt/targets.conf

	<target iqn.2010-10.org.openstack:volume-26c9a2f1-41cc-4c2d-b9dc-933d387340a4>
	     backing-store /dev/cinder-volumes/volume-26c9a2f1-41cc-4c2d-b9dc-933d387340a4
	     IncomingUser tcJXg7MATfnDS3rc9Tq9 bLDmagv4DUsSvyybYtYc
	</target>


## iscsi-initiator-utils  涉及到的文件

/etc/iscsi/iscsid.conf：主要的配置文件，用来连结到 iSCSI target 的设定；
/sbin/iscsid：启动 iSCSI initiator 的主要服务程序；
/sbin/iscsiadm：用来管理 iSCSI initiator 的主要设定程序；
/etc/init.d/iscsid：让本机模拟成为 iSCSI initiater 的主要服务；
/etc/init.d/iscsi：在本机成为 iSCSI initiator 之后，启动此脚本，让我们可以登入 iSCSI target。

## 搜索可以用的target

	iscsiadm -m discovery -t sendtargets -p 192.168.100.254 

##利用 iscsiadm 侦测到的 target 结果

	ll -R /var/lib/iscsi/nodes/

## Login target

	iscsiadm -m node -T iqn.2011-08.vbird.centos:vbirddisk --login

## 检查已经识别的iscsi 盘

	fdisk -l

## logout target

	iscsiadm -m node -T iqn.2011-08.vbird.centos:vbirddisk  --logout

## delete target

	iscsiadm -m node -o delete -T iqn.2011-08.vbird.centos:vbirddisk

##再次发现需要重启

	/ect/init.d/iscsi restart

