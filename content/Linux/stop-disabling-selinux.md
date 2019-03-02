Title: How to stop being a Scrub and learn to use SELinux
Date: 2018-09-20 5:35
Category: Other
Tags: selinux, centos, scrubs
Authors: Admiralspark
Summary: Holy shit guys, it's 2018. Stahp.

## It's 2018, stop disabling SELinux

I know you probably grew up in the hellish days of SELinux having no documentation and no supporting tools. I know you want to live up to the expectations of your BOFH and keep the good fight going. Or hell, maybe you're just a lazy SOB who doesn't give a shit about security. So you run the ol' `setenforce permissive` and move on.

**STOP.**

If this is you, you are bad. Bad as a systems administrator and bad at your job. The world has evolved and moved on, and your crusty ways are no longer right. There is no excuse, with the massive amount of documentation, full and complete package maintainer support for the rulesets, and the easy python utilities to manage rules should you hit a snag to not be using this incredible security layer from right now onwards. 

Open a shell on your RHEL/CentOS box. Type:

`yum install policycoreutils-python`

And boom. Now you have the magic secret sauce. 

SELinux is a tool that explicitly defines which apps, which files, and which processes can access which apps/files/processes across your system, and in what way. It's your tripwire for malicious software infections and downright prevents the majority 

### Scenario 1

Let's say your LEMP stack isn't serving pages you just tossed in there. You built the html, tossed it in /var/www, fired it up and...nothing. Instead of being pissed at selinux, you run the following command:

`grep nginx /var/log/audit/audit.log | audit2why`

and it'll spit back some output, similar to the following:

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

See that? Not only do you have a tool that parses and makes the logs human-readable for you, it even *tells you how to fix the issue*. No major diagnosis needed, you just need to add selinux 'context rules' for the HTML you just tossed up there.

**But, let's break it down even more:**

In the original query, I used grep to pick out a specific line that had an issue; I could have easily grep'd 'denied' and gotten the same one.

`avc: denied { name_connect }`

This means selinux has denied a connection. Furthermore, `pid=1272 comm="nginx" dest=8080` tells us that nginx was trying to communicate on port 8080. The rest of the message shows the selinux context it hit against.

Now, **Audit2Why** recommends two potential options. You're welcome to google them, but as I knew this was nginx serving content on the nonstandard port 8080 to a web browser, just run `setsebool -P httpd_can_network_connect 1` and you'll suddenly have it working if that's the only error you had.

Easy shit, right?

Let's do something harder. 

### Scenario 2

You've got the same LEMP stack, but you want nginx to serve connections to Bookstack in a non-default way. Let's say you pull the code from outside and you don't set up any selinux rules, and then find it doesn't work accessing the bookstack.html file:

```bash
# grep 1715415270.768:35 /var/log/audit/audit.log | audit2why
type=AVC msg=audit(1715415270.768:35): avc: denied { getattr } for pid=1440 \
  comm="nginx" path="/var/www/bookstack.html" dev=vda1 ino=1084 \
  scontext=unconfined_u:system_r:httpd_t:s0 \
  tcontext=unconfined_u:object_r:default_t:s0 tclass=file

  Was caused by:
  Missing type enforcement (TE) allow rule.
```

This is an example of how selinux can prevent a legitimate application from accessing data it shouldn't access (obviously simple).

#### Manual Fix

Modify the file label so that the httpd_t domain can access the file:

`chcon -v --type=httpd_sys_content_t /var/www/bookstack.html`

By default, this modification is deleted when the file system is relabelled. To make the change permanent, run:

`semanage fcontext -a -t httpd_sys_content_t /var/www/bookstack.html`

`restorecon -v /var/www/bookstack.html`

To modify file labels for groups of files, run:

`semanage fcontext -a -t httpd_sys_content_t /var/www(/.*)?`

`restorecon -Rv /var/www`

#### More Automated Approach

Screw doing that for files one at a time, am I right?

First, check what the file would read like (just to see, not functional):

`grep nginx /var/log/audit/audit.log | audit2allow -w -a`

That generated file will be used to modify the selinux domain for this context and allow the new areas. Now create a Type Enforcement (.te) policy:

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

```
#  semodule -i nginx.pp
#  semodule -l | grep nginx
```

Boom. Now you're fixing all sorts of shitty broken php apps and it takes you just a few minutes, like some kind of server wizard.

### SETools

Another utility that's handy to have. Install it using `yum install setools`.

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

### In Summary

It's 2018.

Stop disabling SELinux. 

You have no excuse now. 