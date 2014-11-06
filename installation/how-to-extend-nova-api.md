#如何扩展扩展 Nova REST API

声明：本博客欢迎转发，但请保留原作者信息!      
作者：[罗勇] 云计算工程师、敏捷开发实践者    
博客：[http://yongluo2013.github.io/](http://yongluo2013.github.io/)    
微博：[http://weibo.com/u/1704250760/](http://weibo.com/u/1704250760/) 


按照以下步骤来扩展 Nova REST API:

使用类nova.api.openstack.compute.contrib.floating_ips.floating_ips 作为例子。
 
1)  创建一个新的extension 子类. Extension子类应该派生于“nova.api.openstack.extensions:ExtensionDescriptor” ， 以 Floating_ips 类为例。


![nova-api-extension](/installation/images/extension.jpg )

2)    在 Nova API 中 添加一个新的资源类型

在Floating_ips 类中, 覆写父类中的方法 “get_resources()”
在方法 “get_resources()” 中,, 返回 ResourceExtensions 列表, 来注册你的新的 资源类型 / URL路径 / Controller 等等

![nova-api-controller](/installation/images/controller.jpg)

例如, 以下代码会创建一个新的资源类型 “os-floating-ips”.

    def get_resources(self):
        	resources = [] 
        	res =extensions.ResourceExtension('os-floating-ips',
                        FloatingIPController(),
                        member_actions={})
        	resources.append(res)
 
        return resources
 
新资源 “os-floating-ips” 会和以下URL匹配.

![nova-api0](/installation/images/api0.jpg)

3)    为Nova API中已有的资源类型, 添加新的 controller 方法

在Floating_ips 类中,覆写父类中的方法 “get_controller_extensions”, 在函数 “get_controller_extensions”,中 返回一系列controller列表

![exist_controller](/installation/images/exist_controller.jpg)

例如, 以下代码会创建一个新的资源类型 “os-floating-ips”.
    def get_resources(self):
        resources = []
 
        res =extensions.ResourceExtension('os-floating-ips',
                        FloatingIPController(),
                        member_actions={})
       resources.append(res)
 
        return resources
 
新资源 “os-floating-ips” 会和以下URL匹配.

![nova-api1](/installation/images/api1.jpg)


