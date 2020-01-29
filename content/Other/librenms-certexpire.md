Title: LibreNMS - Certificate Expiration Service Checks
Date: 2019-08-02 17:39
Category: Other
Tags: librenms, services, certs
Authors: Admiralspark
Summary: Be warned when you're running out of time to swap certificates

If you've [followed along on the journey so far]({filename}/Linux/OSSOrchestration-2.md), you probably have LibreNMS set up with several modules enabled and tied to your AD. One thing I mention in there is that you should enable the Nagios-style service checks, from the checkmd project. One of the plugins I use all the time is the [http service check](https://www.monitoring-plugins.org/doc/man/check_http.html).

## Checking your HTTP(S) Services

Setting up a service check for your HTTP-based services is pretty easy: just go to your device in LibreNMS, click the Services tab, and hit Add Service on the right. This will let you pick from all of the available tools. For now, choose the HTTP service and leave everything else default, and hit go.

Pretty soon, you should see some graphs start to fill:

![basic http check]({static}/images/librenms-servicegraphs1.PNG)

It tracks your latency (in ms) of the service response time as well as the size of what an HTTP GET had returned. This is highly useful data and you can build custom alerting around thresholds for this if you want. By default, a Warning or Error state will only return if the service stops responding.

## Adding Options

Those are fine and dandy, but I also needed to track certificate expiration so we can proactively replace them instead of hoping we remember them years later. Certificate expiration is a solved kind of busywork and this is an excellent opportunity to avoid downtime by getting ahead of the problem. Just think, wouldn't it be nice to not ever come in to work to be hit by "all VDI is down for everyone!", only to find it's an expired cert?

Add another service check to your box, but this time use the options set here:

![cert check]({static}/images/librenms-httpcertexpire.PNG)

**--sni** enables TLS hostname extension support

**-S** enables SSL checking

**-p 443** sets the port to check - you're not limited to default ports

**-C 30** sets the check to fail if the cert will be invalid within 30 days!

This is an awesome tool to let you know ahead of time when your certs will expire, and can easily be tweaked to check all of your backend https connections, not just websites. Of course, you can use the API to add the check when you provision a server with Ansible down the line too!