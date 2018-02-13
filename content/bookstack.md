Title: Bookstack installation on Centos 7
Date: 2018-02-12 21:30
Category: Linux
Tags: bookstack, selinux, centos
Slug: bookstack-install
Authors: Admiralspark
Summary: Proper, secure installation of Bookstack on Centos 7

This will cover the installation of Bookstack on Centos 7 including selinux and the firewall, which other guides disable. 

[From their website:](https://www.bookstackapp.com/) "BookStack is a simple, self-hosted, easy-to-use platform for organising and storing information." 

<p class="text-warning">This will also be using php71u, because nobody in the world really wants to run php5 still. This guide assumes a clean base Centos 7 minimal image and standard SELinux settings out of the box.</p>

## Prerequisites

Run the following commands to prep your system for Bookstack:
```bash
yum -y install epel-release
yum -y install https://centos7.iuscommunity.org/ius-release.rpm
yum -y install git mariadb-server nginx php71u php71u-fpm php71u-gd php71u-mbstring php71u-mysqlnd php71u-pdo php71u-tidy php71u-cli php71u-json php71u-xml
```

## MySQL Setup

This is fairly straightforward, first we do the normal secure install:
```bash
systemctl restart mariadb.service
mysql_secure_installation
```

Now put in the password of your choice, answer yes to everything else, and proceed:
```sql
mysql -u root -p
CREATE DATABASE IF NOT EXISTS bookstackdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON bookstackdb.* TO 'bookstackuser'@'localhost' IDENTIFIED BY 'bookstackpass' WITH GRANT OPTION;
FLUSH PRIVILEGES;
quit
```

## PHP Settings

Next, we edit PHP-FPM's config file:
`vim /etc/php-fpm.d/www.conf`

Change/verify the following variables are set properly in the www.conf file:
```bash
listen = /var/run/php-fpm.sock
listen.owner = nginx ; 
listen.group = nginx ; 
listen.mode = 0660 ; 
user = nginx ; 
group = nginx ; 
php_value[session.save_path] = /var/www/sessions
```

## NGINX Configuration

And on to Nginx:

`mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.orig`

`vim /etc/nginx/nginx.conf`

Paste the following Nginx config:
```
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
  worker_connections 1024;
}

http {
  log_format main '$remote_addr - $remote_user [$time_local] "$request" '
  '$status $body_bytes_sent "$http_referer" '
  '"$http_user_agent" "$http_x_forwarded_for"';

  access_log /var/log/nginx/access.log main;

  sendfile on;
  tcp_nopush on;
  tcp_nodelay on;
  keepalive_timeout 65;
  types_hash_max_size 2048;

  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  include /etc/nginx/conf.d/*.conf;
}
```

Now we edit the server configuration:
```
server {
  listen 80;
  server_name localhost;
  root /var/www/BookStack/public;

  access_log /var/log/nginx/bookstack_access.log;
  error_log /var/log/nginx/bookstack_error.log;

  client_max_body_size 1G;
  fastcgi_buffers 64 4K;

  index index.php;

  location / {
  try_files $uri $uri/ /index.php?$query_string;
  }

  location ~ ^/(?:\.htaccess|data|config|db_structure\.xml|README) {
  deny all;
  }

  location ~ \.php(?:$|/) {
  fastcgi_split_path_info ^(.+\.php)(/.+)$;
  include fastcgi_params;
  fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
  fastcgi_param PATH_INFO $fastcgi_path_info;
  fastcgi_pass unix:/var/run/php-fpm.sock;
  }

  location ~* \.(?:jpg|jpeg|gif|bmp|ico|png|css|js|swf)$ {
  expires 30d;
  access_log off;
  }
}
```

## Bookstack Installation
Composer Install (if PHP fails for some reason, look for similar issues here: https://www.rootusers.com/upgrade-php-5-6-7-1-centos-7-linux/):
```
cd /usr/local/bin
curl -sS https://getcomposer.org/installer | php
mv composer.phar composer
```

Bookstack install:
```
cd /var/www
mkdir /var/www/sessions
git clone https://github.com/BookStackApp/BookStack.git --branch release --single-branch
cd BookStack && composer install
```

Once that's complete, back up the env file and edit it:
```
cp .env.example .env
vim .env
```

Verify that the following settings are correctly set based on the MySQL user you created earlier:
```
DB_HOST=localhost
DB_DATABASE=bookstackdb
DB_USERNAME=bookstackuser
DB_PASSWORD=bookstackpass
```

## Cleanup
```
php artisan key:generate --force
chown -R nginx:nginx /var/www/{BookStack,sessions}
php artisan migrate --force
```

Enable the services:
`systemctl enable nginx.service && systemctl enable mariadb.service && systemctl enable php-fpm.service`

Firewall rules:
```
firewall-cmd --permanent --add-port 80/tcp
firewall-cmd --reload
```

Selinux rule:

`setsebool -P httpd_unified 1`

Now, reboot! 

This is now a complete installation. You will sign in with the default username of `admin@example.com` with the password of `password`. 

However, since you may want to use this at work, here's how you'd configure LDAP authentication via Active Directory.

## Group-Based LDAP Authentication via Microsoft Active Directory

Install the required package:
`yum install php71u-ldap`

Set the SELinux permission:
`setsebool -P httpd_can_network_connect 1`

Edit the .env file:
`vim /var/www/BookStack/.env`

And add the following values:
```
# LDAP Settings
LDAP_SERVER=ad1.contoso.com:389
LDAP_BASE_DN="OU=Contoso Co,DC=contoso,DC=com"
LDAP_DN=ldapuser@contoso.com
LDAP_PASS=ldapuserpassword
LDAP_USER_FILTER="(&(SAMAccountName=${user})(memberOf=CN=BookStackAdmin,OU=Contoso Groups,OU=Contoso Co,DC=contoso,DC=com))"
LDAP_VERSION=3
```

Now run
`php artisan optimize`
to verify it's good to go!

<p class="text-warning">Note: the filter is checking if SAMAccountName $user exists and is ALSO matching as a memberOf the CN=BookStackAdmin group using the full Distinguished Name. This is not documented anywhere.</p>