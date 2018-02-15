Title: SELinux - Practical Intro to Audit2Why and Audit2Allow
Date: 2018-02-14 20:30
Category: Linux
Tags: selinux, centos
Authors: Admiralspark
Summary: Or, how to stop fearing selinux without the boring intro text

# Intro

SELinux is a powerful security framework built into every RHEL/CentOS box out there. Originally, it was an overly-complicated tool that sysadmins around the world reacted to negatively as the documentation was poor (in the understandable sense) and the helper tools we have today weren't around. However, Red Hat has spent a bunch of time fleshing out the docuemntation, building classes and educational materials for it, and most importantly building tools to help diagnose issues and deploy applications faster.

By default, all applications installed from one of the core repositories will have the SELinux rules they need to function, and so if you run into a core app throwing SELinux errors you should probably open a bug report for it. However, doing anything custom (every php application ever, for example) will need some custom rules set.

## Prerequisites

Install the one package that will make your life eternally easier:

`yum install policycoreutils-python`

This is a set of python scripts which parse the /var/log/audit/audit.log file and produce information on any errors found inside. If it's not a part of your base image, make it so, now!

## Audit2Why and Audit2Allow

These are the most useful and commonly used utilities, so we'll start here. Audit2why parses the aforementioned audit.log and will return one-line commands for fixes on every denied entry, or point you to other utilities if it's more complicated (for example, base selinux assignments missing entirely).

For instance, let's say you have a full LAMP stack and it's having issues. To use audit2why to view problems with the httpd server, type:

`grep http /var/log/audit/audit.log | audit2why`

This will tell you what went wrong, and what type of policy is needed to fix the problem.

### Network Access

Here's some sample output:

```bash
grep 1415714880.156:29 /var/log/audit/audit.log | audit2why
type=AVC msg=audit(1415714880.156:29): avc: denied { name_connect } for pid=1349 \
  comm="nginx" dest=8080 scontext=unconfined_u:system_r:httpd_t:s0 \
  tcontext=system_u:object_r:http_cache_port_t:s0 tclass=tcp_socket

  Was caused by:
  One of the following booleans was set incorrectly.
  Description:
  Allow httpd to act as a relay

  Allow access by executing:
  # setsebool -P httpd_can_network_relay 1
  Description:
  Allow HTTPD scripts and modules to connect to the network using TCP.

  Allow access by executing:
  # setsebool -P httpd_can_network_connect 1
```

First, let's pick this apart. I just used grep to pick out a specific line that had an issue, I could have easily grep'd 'denied' and gotten the same one.

`avc: denied { name_connect }`

This means selinux has denied a connection. Furthermore, `pid=1349 comm="nginx" dest=8080` tells us that nginx was trying to reach out on port 8080. The rest of the message shows the context it hit against.

Now, Audit2Why recommends two potential options, both of which will give you potential fixes. You're welcome to google them, but as I knew this was nginx serving content on 8080 to a web browser, just run `setsebool -P httpd_can_network_connect 1` and you'll suddenly have it working if that's the only error you had.

### File Access

Another common issue: you try to have nginx serve content from somewhere not normal (very common in the custom php app world). Here's an example error:

```bash
type=AVC msg=audit(1715415270.768:35): avc: denied { getattr } for pid=1440 \
  comm="nginx" path="/var/www/bookstack.html" dev=vda1 ino=1084 \
  scontext=unconfined_u:system_r:httpd_t:s0 \
  tcontext=unconfined_u:object_r:default_t:s0 tclass=file
```

Now we run audit2why against it, like so:

```bash
# grep 1715415270.768:35 /var/log/audit/audit.log | audit2why
type=AVC msg=audit(1715415270.768:35): avc: denied { getattr } for pid=1440 \
  comm="nginx" path="/var/www/bookstack.html" dev=vda1 ino=1084 \
  scontext=unconfined_u:system_r:httpd_t:s0 \
  tcontext=unconfined_u:object_r:default_t:s0 tclass=file

  Was caused by:
  Missing type enforcement (TE) allow rule.
```

This is a major source of pain, so let's cover the manual way to deal with it first.

#### Modify the file label

Modify the file label so that the httpd_t domain can access the file:

`chcon -v --type=httpd_sys_content_t /var/www/bookstack.html`

By default, this modification is deleted when the file system is relabelled. To make the change permanent, run:

`semanage fcontext -a -t httpd_sys_content_t /var/www/bookstack.html`

`restorecon -v /var/www/bookstack.html`

To modify file labels for groups of files, run:

`semanage fcontext -a -t httpd_sys_content_t /var/www(/.*)?`

`restorecon -Rv /var/www`

#### Alternative choice, extending the httpd_t 'Domain' permissions with Audit2Allow

First, check what the file would read like (just to see, not functional):

`grep nginx /var/log/audit/audit.log | audit2allow -W -a`

That generated file will be used to modify the selinux domain for this context and allow the new areas. This creates a Type Enforcement (.te) policy:

`grep nginx /var/log/audit/audit.log | audit2allow -m nginx > nginx.te`

`cat nginx.te`

```bash
module nginx 1.0;

require {
  type httpd_t;
  type default_t;
  type http_cache_port_t;
  class tcp_socket name_connect;
  class file { read getattr open };
}

#============= httpd_t ==============
allow httpd_t default_t:file { read getattr open };

#!!!! This avc can be allowed using one of the these booleans:
# httpd_can_network_relay, httpd_can_network_connect
allow httpd_t http_cache_port_t:tcp_socket name_connect;
```

Now, we use the -M option to create a *compiled* policy:

`grep nginx /var/log/audit/audit.log | audit2allow -M nginx`

And then we import the Policy Package (.pp), and verify it's working:

```bash
semodule -i nginx.pp
semodule -l | grep nginx

nginx 1.0
```

## SETools

Another utility that's handy to have. Install it using `yum install setools'.

So what if the issue you're facing is that you're using nginx to serve content on a nonstandard port? SELinux correctly knows that it shouldn't be serving content on 8082 by default (thanks to the selinux context built into the package), so we need to modify the system contexts to allow such a thing.

For example, I set up nginx as a reverse proxy, so I'd need to enable httpd_can_network_relay...but it's proxying a nonstandard port. So, I run the following:

```bash
sesearch -A -s httpd_t -b httpd_can_network_relay
Found 10 semantic av rules:
  allow httpd_t gopher_port_t : tcp_socket name_connect ;
  allow httpd_t http_cache_client_packet_t : packet { send recv } ;
  allow httpd_t ftp_port_t : tcp_socket name_connect ;
  allow httpd_t ftp_client_packet_t : packet { send recv } ;
  allow httpd_t http_client_packet_t : packet { send recv } ;
  allow httpd_t squid_port_t : tcp_socket name_connect ;
  allow httpd_t http_cache_port_t : tcp_socket name_connect ;
  allow httpd_t http_port_t : tcp_socket name_connect ;
  allow httpd_t gopher_client_packet_t : packet { send recv } ;
  allow httpd_t memcache_port_t : tcp_socket name_connect ;
```

Interesting...the application I'm using most closely matches http_port_t (a normal tcp socket) so let's check what that does support:

```bash
semanage port -l | grep http_port_t
http_port_t tcp 80, 81, 443, 488, 8008, 8009, 8443, 9000
```

Ahh, see, 8082 is not here, so we now just need to quickly add it:

`semanage port -a -t http_port_t -p tcp 8082`

And bam! It's working. You might get a message that it's already defined--if so, don't reassign it as you could potentially bork other things, instead consider using the corresponding ruleset it points you to. Example:

```bash
# semanage port -a -t http_port_t -p tcp 8080
/usr/sbin/semanage: Port tcp/8080 already defined
# semanage port -l | grep 8080
http_cache_port_t tcp 3128, 8080, 8118, 8123, 10001-10010
```
