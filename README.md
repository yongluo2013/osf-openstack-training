
##项目说明

本项目主要用于开源力量《OpenStack应用实战解析及开发入门》 在线培训同步课程使用，请勿私自用于商业用途，欢迎个人随意转载，但是请保留源作者版权信息。

##目录说明

code/ 上课用到的演示代码

installation/ 手动安装文档等

##教学内容

###初识OpenStack

* OpensSack 现场演示
* 详细介绍OpenStack涉及到的概念，并结合实际应用场景介绍相关概念的应用。
* 基本概念：Tenant、User和Role
* 高级概念：Region、AZ、Cell、Host Aggregate
* 如何结合实际应用场景来对应OpenStack中的概念

###手动OpenStack安装配置

* Openstack部署架构讲解（3个VM）
* Keystone搭建
* Glance搭建
* Neutron搭建
* Nova搭建
* Dashboard 搭建
* Swift搭建
* Cinder搭建

##OpenStack 自动部署

* Openstack 自动化部署方式比较
* DevStack自动化部署原理，并演示单节点和多节点自动化安装部署 
* Fuel OpenStack多节点自动化部署介绍
* PackStack多节点自动化部署介绍
* Puppet 方式部署介绍

###OpenStack认证组件Keystone 

* Keystone介绍和基本概念
* Keystone架构
* Keystone处理流程
* Keystone实验

###OpenStack镜像组件Glance

* Glance介绍和基本概念
* Glance架构
* Glance实验
* 镜像的制作、修改、转换

###OpenStack对象存储Swift和块存储Cinder

* Swift的架构和原理
* Swift的企业部署方案
* Cinder架构
* 基于Cinder的解决方案

###OpenStack网络组件Neutron

* 网络基础知识
* 网络方案选择
* Neutron组件架构
* OpenStack&SDN网络现状

###OpenStack计算组件Nova

* 虚拟化技术KVM,VMWARE,XEN介绍
* Nova介绍及框架
* Nova运行流程
* Nova部署模式
* 虚拟机监控
* Live migrate
* Backup

###OpenStack HA方案的选择及日志

* 各组件HA方案
* 日志分析与排除

###性能瓶颈

* OpenStack平台性能瓶颈
* 虚拟机性能瓶颈

###性能调优

* OpenStack平台性能调优
* KVM性能调优
* Host OS性能调优

###OpenStack使用

* 命令行操作

###Dashboard操作

###nova源码架构介绍

* 源码的获取
* 开发环境的搭建
* nova模块调用介绍
* nova源码模块功能介绍

###添加Nova-api自定义模块

###数据库表结构的扩展

* nova表结构的扩展
* keystone表结构的扩展
* resetful接口服务的扩展

###nova数据库调用接口服务的扩展

* compute接口的扩展
* keystone接口服务的扩展
* 基于openstack服务、配置架构自定义服务模块

###Django快速入门

* Demo for a "Hello World"
* Django ORM 介绍
* Django Template介绍
* Django View 介绍

###Dashboard源码介绍

* horizon代码模块介绍
* 中文化的功能实现
* 页面按钮的添加
* 列表中下拉菜单的添加
* 列表中文字链接的添加

###OpenStack大规模部署碰到的常见问题及其优化方法

###OpenStack大规模部署案例及经验介绍

* 公有云经验分享
* 私有云经验分享

###OpenStack云平台与其它几种云平台的比较

* 几种主流的开源云平台技术比较
* 几种主流云平台的生态系统比较

###国内外OpenStack云计算的案例和现状
