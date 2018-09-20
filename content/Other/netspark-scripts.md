Title: Netspark-Scripts Refactoring Release!
Date: 2018-07-15 17:30
Category: Other
Tags: python, networking, scripting, automation
Authors: Admiralspark
Summary: Finally, a new release!

It's been a long time in the making but I've finally released the new and improved [netspark-scripts](https://github.com/admiralspark/NetSpark-Scripts)!

### Why?

Netspark-Scripts was originally an open-source project I created to demonstrate what Netmiko-based code could actually look like, in an attempt to help the network administrators out there hit that nirvana moment when they see the true How and Why it works. In later 2016 I finally decided I'd had it manually SSHing into each of my network switches, routers and firewalls to do basic management and I decided to build a way to make the wonderfully powerful computer sitting in front of me do it for me.

The very first thing I automated was a tool to remote into a group of switches and find what port a mac address was sitting on, and spit it out to the cli. I used this to take the manual process of searching for a phone across a customer's infrastructure from a 20 minute job to a 30 *second* job, something I sometimes did a dozen times a day. The rest was easy--adding features, automating newer tasks, etc. I eventually began a rewrite of the code to make it have a single script to run, and

### The New Hot Sauce

As you can see in the Example_Scripts folder,I used to build the majority of my scripts using a template. That was good but the correct solution to re-using 80% of the code every time was to make it into a library. The other issue I hit was performance--single-thread processing is garbage slow when you're just trying to `wr mem` on 400+ network devices.

So, I rewrote it with new features in mind:

- "--info" and "--config" modes
  - info mode runs commands in regular execution mode, so you'd enter things like "wr mem" or "show run" using this
  - config mode runs commands in configuration mode, although it is level-aware (I'll demo this later on)
- Multiprocessing
  - Using the awesome multiprocessing.Dummy library, I split this into 8-threaded execution. Obviously networks will need to be tweaked, but 8 seems to be a sweet spot. 8x the speed!

Now, basically, it's a command-line multiprocessing for loop! Want to write mem on a hundred machines? `python netspark.py --info "wr mem" --csv allmyswitches.csv`! Have a config file prepped to set up RADIUS auth on your routers? `python netspark.py --config radiussetup.txt --csv routers.csv`!

As always, it's open source and accepting contributions, I only ask that you explain the changes you make in the PR!