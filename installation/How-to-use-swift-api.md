##如何使用Swift API

### 用户认证与建权

To authenticate with Tempauth

Supply your user name and API access key in headers, as follows:

X-Auth-User header. Specify your Object Storage user name.

X-Auth-Key header. Specify your access key.

The following example shows a sample request:

	curl -i http://controller0/v1/auth?format=json  -H "X-Auth-User: admin" -H "X-Auth-Key: admin"





