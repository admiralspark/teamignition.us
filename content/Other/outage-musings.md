Title: Post-Mortem Mortality Musings
Date: 2018-10-05 07:00
Category: Other
Tags: networking
Authors: Admiralspark
Summary: The difference between what you think is going to happen, and what does

## "We're having a major network outage"

Those words are the ones a network engineer hopes to never hear, and yet for some reason can never escape. 

In a perfect world, we've built highly redundant systems and practiced what to do in case of an outage event. Every system has multiple paths to reach the end goal, every tech knows their role and responsibility in the event that it doesn't work out, and the business has A Plan™ for when SHTF. 

But of course, reality isn't quite so rosy. Budgets, 'sins of the fathers', and just plain unknown easter eggs trip us up on the way, and the difference between a beautifully crafted system being brought to its knees or being brought back online might come down to whether you can keep a cool head or not when it hits. 

We had a large outage recently that had many contributing factors I'm going to go over, in hopes that someone here sees them and doesn't get trapped in the same situation we did.

### Can you hear me now?

The first issue was a self-inflicted one on my part. Carrying around two smartphones with thick protective cases in my pocket all day long drove me nuts, so I had my work phone forwarded to my personal one. My original justification was that the work phone was at my desk (which always has service), my personal phone had the same carrier and I had already checked to make sure that their coverage/signal quality was the same so I'd never be in a deadspot with the personal phone where work would've...worked.

Well, I just swapped carriers for my personal cell two days ago. Last night I was at my local amateur radio club's meeting and had no service in the building, so when I finally left I got the familiar DING DING of voicemails with no missed calls. Turns out...it was my boss and our chief engineer calling me to tell me that everything was FUBAR and I needed to head in, NOW...and the voicemail was 2 hours old. Oops. Suffice to say....I'm carrying the work phone now.

So, think about that. If everything starts burning, will you be able to know? Are you SURE the alert notifications will reach you? Our monitoring server sits on the virtualized hosts behind the root cause of our outage so those emails and notifications never hit me until we'd restored services. **Do you have a monitor for the monitor?**

### Are you sure that the redundancy is redundant?

I'll get this out of the way now: the root cause of our outage was a core switch that lost its brains and started flapping ports, and caused a cascading spanning-tree failure. I'll go over the "what we thought vs what it was" stuff later, but one issue we found was that in our big network loop.....one of the trunks had been disconnected for over a year, so it was more like a long leg. We had no monitoring for that (mistake #1), we found that the server infrastructure did not handle failover fast enough (iSCSI took 6 seconds to pivot...so several sensitive apps shit themselves), and we also didn't have the plan for prepping the hardware spare ironed out ahead of time.

Are you sure spanning tree is configured? Are you sure it works? Map this stuff out. Make a plan, share the plan with your group, and then verify it in production. 

### Do you really have access to everything you need when SHTF?

So, here's a list of things we needed that we didn't have in our disaster plan:

- Config Backups - They were stored, in git revision, backed up automatically...to a server on the host that was taken down. Oops. 
    - Consider having a local copy synced, weekly or daily depending on your needs
- IP Spreadsheet/IPAM assignments/Something correlating network gear DNS entries to IP addresses
    - Fell into my own trap here, having DNS names was nice...until the virtualized DNS server isn't reachable
- Password manager - Did you store that database on a virtualized appliance? Do you have an offline backup?
- Recovery process practiced - Hardware spares are only as good as you can quickly redeploy them
    - Make sure you have on-hand tools for transferring configs to hardware spares (FTP server, usb, however they do it) or provisioning systems that work when the network doesn't
- Redundant monitoring
    - Is your monitoring server virtualized? Does it have something else monitoring it? If it goes down, how will you know after hours?
- Physical copy of the network map
    - Ideally, have names and IP's of network gear, plus uplinks/critical ports labeled. 
    - Save it offline as well as in your backups. 
    - Have enough information in it that you could rebuild it enough to get to your config and server backups, if all of your network gear lost their configs entirely. 

I highly encourage someone to play out an outage event at various different levels in the network. Start at someone cutting an ethernet cable with scissors, move to spanning tree issues, move to VRRP/routing issues, move to authentication servers being down, then virtualization hosts (test vmotions and HA), then applications themselves. **Don't forget your phone system!**

## Final Lessons

Do you have a plan for how to access network gear if your centralized auth fails? Do you know which order your business applications and services need to be restored in? Remember, this means both the order to restore interconnected services so they come up correctly, and how to prioritize which service groups are needed first for business continuity. 

Do you have the right people available on-call? Do you have a plan for what to do if one of them gets hit by a bus? Or forgets his cellphone?

Think about these things and practice them ahead of time. All you need to do is have a roundtable discussion, you don't even need to force an outage "as a test", but the more realistic the better when shit hits the fan. 

Good luck out there. 