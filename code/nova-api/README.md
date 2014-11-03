## WSGI示例

###.simplejson：最简单的wsgi示例。

在simplejson目录下，运行simplejson.py便可启动API服务。

	python simplejson.py

在另一个窗口使用如下命令访问：

	curl http://127.0.0.1:8080

### wsgi_paste：功能和simplejson一样，只是通过paste deploy加载app。
	在wsgi_paste目录下，运行 wsgi_paste.py便可启动API服务。

	python wsgi_paste.py

	然后在另一个窗口使用如下命令访问：

	curl http://127.0.0.1:8080

###wsgi_middlware:在wsgi_paste的基础上添加了一个filter来认证用户的身份。

在wsgi_middleware目录下，运行wsgi_middlware.py便可启动API服务。

	python wsgi_middlware.py

当使用如下命令访问时

	curl http://127.0.0.1:8080

会出现禁止访问的错误。当使用如下命令访问时，可得到正常结果。

	curl -H “X-Auth-Token: open-sesame” http://127.0.0.1:8080

###wsgi_class:使用class来创建wsgi服务。其中：

	* service.py用来启动WSGI服务；

	* wsgi.py用来加载app和创建线程;

	* filter.py定义了filter类;

	* app.py定义了app类。

在wsgi_class目录下，运行service.py便可启动API服务

	python service.py


当使用如下命令访问时

	curl http://127.0.0.1:8080

会出现禁止访问的错误。
当使用如下命令访问时

	curl -H “X-Auth-Token: open-sesame” http://127.0.0.1:8080

可得到正常结果。

##二次开发：

###步骤

1. 服务器端代码在myapi目录，须放在nova/目录下；

2. 客户端代码为myapi.py，须放在novaclient/v1_1/contrib目录下；

3. 测试代码为test_myapi.py

4. 运行时须在nova.conf中添加如下配置：

	osapi_compute_extension=nova.myapi.controller.MyAPI

5. 然后重启nova-api。
