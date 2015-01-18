= Puppet quick starting =

== Puppet installation on centos == 

imprt yum repo

	sudo rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm 

Install Puppet on the Puppet Master Server

 	sudo yum install puppet-server

 	systemctl enable puppetmaster.service

Install Puppet on Agent Nodes

	sudo yum install puppet


Configure a Puppet Master Server

setup hostname 
	vi /etc/hostname
	puppet.test.com

	vi /etc/sysconfig/network
	puppet.test.com

	vi /etc/hosts
	<local_ip_address>  puppet.test.com

set puppet master

	vi /etc/puppet.conf 
	dns_alt_names = puppet.test.com

For CA Masters
If this is the only puppet master in your deployment, or if it will be acting as the CA server for a multi-master site, you should now run:

	puppet master --verbose --no-daemonize

This will create the CA certificate and the puppet master certificate, with the appropriate DNS names included. Once it says Notice: Starting Puppet master version <VERSION>, type ctrl-C to kill the process.




