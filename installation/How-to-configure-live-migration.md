##配置nova 动态迁移

###配置计算节点配置

修改 libvirtd 配置文件

	vi /etc/libvirt/libvirtd.conf
	listen_tls = 0
	listen_tcp = 1
	auth_tcp = "none"

	vi /etc/sysconfig/libvirtd
	LIBVIRTD_ARGS="--listen"

重启libvirtd 

	service libvirtd restart


修改nova 配置文件

	/etc/nova/nova.conf

	live_migration_flag=VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE

重启nova compute 

	service openstack-nova-compute restart


把instance 启动到指定的host 上

	nova boot --flavor m1.tiny --image $(nova image-list|awk '/ CirrOS / { print $2 }') --nic net-id=$(neutron net-list|awk '/ demo-net / { print $2 }') --security-group default --availability-zone nova:compute0 demo-instance1

查看需要迁移的instance

	nova list
	+————————————–+——————-+——–+———————+
	| ID | Name | Status | Networks |
	+————————————–+——————-+——–+———————+
	| 5374577e-7417-4add-b23f-06de3b42c410 | demo-instance1 | ACTIVE | ncep-net=10.20.20.3 |
	+————————————–+——————-+——–+———————+

查看已经存在的compute 节点

	nova host-list
	+————–+————-+———-+
	| host_name | service | zone |
	+————–+————-+———-+
	| compute0 | compute | nova |
	| compute1 | compute | nova |

执行迁移命令

	nova live-migration  –block-migrate demo-instance1 compute1


查看哪些instance 正在迁移

	nova show demo-instance1

自由选择迁移节点

	nova live-migration  --block-migrate demo-instance1



 







