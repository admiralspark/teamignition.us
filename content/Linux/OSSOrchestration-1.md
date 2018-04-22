Title: Full-Stack Open Source Network Monitoring Systems
Date: 2018-04-16 23:12
Category: Linux
Tags: linux, librenms, snmp
Authors: Admiralspark

<div class="alert alert-dismissible alert-info">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>Heads up!</strong> This is part one of a multi-part series on setting up a complete, free and open source monitoring and management solution for your business.
</div>

## Intro

A quick google search will show you that there's thousands of network monitoring solutions out there--from completely custom monitoring based on Nagios, to the beautiful Graphana dashboards, to the goliath of monitoring solutions, Solarwinds, and all of it's associated bills. I've spent time in shops that had PRTG free as their only monitoring, and I've spend time at businesses that licensed (and implemented!) the full suite of Solarwinds products.

When my current employer assigned me the task of "find everything we have and monitor it", I put together a wishlist of all the things I wanted in a monitoring product if I had access to a team of devs and a small loan of a million dollars:

- **Monitoring**. We needed a ton of alerting points, like storage and CPU utilization
- **Support all OS's**. Linux, Windows, network gear like Cisco IOS/Fortinet/Juniper/Dell etc, even printers
    - This meant SNMP was the only realistic option
- **Alerting via email**
    - as a bonus, alerting in any other way as well (text, chat notification, Telegram, etc)
- **Service checks** - not just that it's running, but that it's *operating properly*
- **Network configuration backups**
    - Stored in GIT if possible
- **Centralized logging (+ Alerting)**
- Event correlation?
- Auto-remediation?
- [Everything else in Stretch's Hierarchy of Network Needs?](http://packetlife.net/blog/2015/dec/14/stretchs-hierarchy-network-needs/)

To some with larger budgets, this is all a given, but to those without such fortune it seems an insurmountable task after you get the first gut-punch of vendor licensing costs after a demo. So, having run a few pieces of the kit I'm going to be diving into here in a homelab before and knowing what features I needed and how reliable they needed to be, I set out to implement a full solution for a business that had nothing.

As a high level, I'll be going through the installation and configuration of the following packages as we go on:

- **LibreNMS** - for Monitoring, dynamic Alerting, and centrally managing the rest of our software pieces below
- **Nagios Service Checks** - for monitoring services, seamlessly integrated into LibreNMS
- **Gitlab** - for centralized, change-tracking backups of device configuration files and any code you happen to run
- **Oxidized** - automatic configuration backups and revisioning, exporting to your Gitlab instance above
    - If you use centralized auth (RADIUS), you can even see *who made which changes when* using this, which is awesome for change management
- **Graylog** for centralized logging, alerting on those logs, and threat intelligence once we have it ingesting network traffic
    - I'll also talk a bit here about event correlation as I go along, this is a WIP right now, but a bunch of what makes a SIEM useful can be imoplemented here without having the full stack SIEM to babysit all day.
- **Ansible** - Once all of this is set up, you need to be able to deploy it *consistently* and *correctly*, so using Ansible to push to Windows, Linux and network devices. All, of course, backed up and managed by your git repo in Gitlab
- Finally, auto-remediation will be orchestrated by all of these pieces working together.

At the end of this, you will be able to react proactively instead of reactively to issues in your environment, have a better hgih-level and detailed view of what's actually happening in your network, and a scalable, widely-supported git-based solution for your device configurations, change management and automation systems. I'll try to cover all of the details that normally get skipped, like how to actually format your Oxidized configs and what Group Policies are needed for WinRM connectivity in Windows domains.

## First, the basics: LibreNMS

To begin, we'll [set up LibreNMS and monitor our first endpoint](https://docs.librenms.org/#Installation/Installation-CentOS-7-Nginx/). For future setups I will detail the installation, but with how fast development of LibreNMS has been recently, just follow that guide and you should be good to go.

### Tweaks to LibreNMS

I do have a few tweaks we should make to LibreNMS before proceeding on:

- If you have an Active Directory, set up LibreNMS to use [Active Directory Authentication](https://docs.librenms.org/#Extensions/Authentication/#active-directory-authentication). This is big, never set up a system with a single user access.
- Set it up to use the [Stable Update Channel](https://github.com/librenms/librenms/blob/master/doc/General/Releases.md#stable-branch). This is not master or devel, this is about once monthly and happens when they feel they have another stable release.
- If you want to have beautifully formatted email alerts, you can enable html emails and graphs:

```php
$config['email_html'] = TRUE;
$config['allow_unauth_graphs'] = 1;
```

- [Enable Nagios service checks](https://docs.librenms.org/#Extensions/Services/). These are awesome, and let you graph service performance like SQL and HTTP(s) response times. Supports custom queries as well!

Now, we're ready to proceed on to [Part 2: Centralized configuration revision and config backups]! (coming soon!)