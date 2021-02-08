Title: Project Update - Docker in everything!
Date: 2020-01-28 20:26
Category: Other
Tags: docker, update
Authors: Admiralspark
Summary: Containerization of my lab and my work

It's been a while since I submitted any lengthy content to this blog, for various reasons. If you want to hear why, continue on, but if you want to just skip to the new lab setup then skip this post.

# New/Newer/Newest Plans

When I originally wrote the [original full-stack open source network orchestration post]({filename}/Linux/OSSOrchestration-1.md), I had freshly finished deploying that system for a 'traditional' enterprise who had nothing like it before. No monitoring, no alerts, certainly no automation; they were reactive to most issues and stuck in the "too much work/no time to automate" loop. I learned at a previous employer that the only way to break out of that is to *make* time to automate-- use the [Scotty Principle](https://ipstenu.org/2011/the-scotty-principle/) to set expectations, enforce Read-Only Friday's and spend at least 4 hours a week researching and working on automation of *any kind*. I found that automation (and programming in general) never kicked in for me until one day I found a task I hated doing--manually searching through network gear for the specific port a specific device is talking on--and got motivated to figure out a way to solve it. I spent two days learning python from nothing, learning netmiko, connecting to my first device, accidentally wiping the config and reloading it, and finally successfully automating a 20 minute procedure down to 30 seconds. 

Was it worth it? At the time, for my sanity it was but for my employer, they probably wouldn't think so. But I communicated clearly with my boss and my customers that week that I was backed up on work, and it would be a few days until problem resolution. They were understanding (as most people are when you make sure to proactively communicate with them), and that two day stretch marked the beginning of a revolution in my toolset, problem solving and even my career. 

That tool eventually served as the inspiration for Netspark-Scripts, and the skills I developed there and from similar projects led me to crank out more and more work in the same amount of time *while* my team was shrinking from four, to three, to two, to just myself. I can completely say with confidence that the skills I developed and the drive I had for automating all parts of my job allowed me to make a complete career change and lifestyle change that has benefitted me tremendously.

**Anyway**, the FOSS stack has changed over time. All of the original tools are still there, but my Ansible use expanded to cover all of our linux servers, our windows servers, and every network device we can manage. I am the sole contributor to the project--I work on a team of five and most of the others don't see the value, *and that's okay*. I do it for my own benefit--every time I can push a new vlan out to a remote site with a 30 second code push to Gitlab instead of manually hitting every device there is more time I can spend doing actually important work. I envisioned that I'd do separate blog posts for each piece but I honestly don't have the motivation for it--I'm going to try and give a presentation at ArcticCon this year about it, and if I do I'll link it here. But, the software itself truly has changed how I approach problems at work:

A user walks in to report a broken update to $Software? "No problem, it'll be working by the time you get back to your desk". A one-line remote powershell session, `choco uninstall $software` and `choco install $software` and it's taken care of. 

Need a new server, 100% PCI compliant Category 1? [Kick off a template build with a script]({filename}/Other/powercli-deploy-template.md), over the next 30 seconds add the new hostname to the correct area of my Ansible inventory file, and then `ansible-playbook -i inventory cat1-deploy-windows.yml --limit=newserver.domain.tld` and a couple minutes later a hundred changes are pushed to it.

Director comes in, "Hey, we have a dozen servers under that PCI umbrella, and the auditors are going to be here this afternoon to make sure everything is configured exactly as we reported to them." No problem, run that same prevous ansible playbook without a limit and you're all set.

HR emails a new user creation form. Your first-line support people go into Rundeck, click the New User button, copy paste from the email and hit Go and a couple minutes later their dozen accounts are made, they're active in payroll, your insta-clone vms are ready for them to sign on from anywhere in the company and they already have the welcome email.

I know this has completely de-railed from where it originally was going, so let's bring it back. The stack before still exists but has been augmented--Gitlab now automatically spins up runners to run every test I could think of against all of my code, Rundeck is out there autoremediating "will not solve" issues with crappy enterprise software and support, and I'm spending a ton of time on my latest project--building all of this functionality again, but without an internet connection...on an *air-gapped* network. You'd think the process would be more or less the same, but lazy development practices by many open-source developers who work on these projects lead to situations where, if you want to run their software, you need internet connectivity all the time. Take LibreNMS: they require that you install a third-party repository now for php7.x on CentOS, and then also you run a shell script to install composer which adds *more* software locations and packages, and they do not once give you a complete requirements list of all packages that LibreNMS needs to run. Which, of course, means that you get to spend an incredible amount of time setting it up on an internet connection, grabbing a finalized package list with all dependencies, manually downloading them and adding them to your offline package repository (or something else, more to come). Frustration is one of the words I use now but not colorful enough for use back then.

# So Now What?

This, however, leads me to the What's Next part of the blog. Solving this problem happens to be *exactly* what linux containers and specifically Docker containers are *really good at*. All dependencies, all requirements, all options clearly documented and packaged into a nice binary file you pluck from whatever source you use and stick on to your system, and they **just work**. I needed Gitlab at home for some projects, so I added a container to Portainer, defined a few variables (like two for Traefik so it can automatically proxy the container), and a few minutes later it's up and running. Bookstack was even easier, I copy/pasted the Compose 2.0 file into Stacks in Portainer and boom! Up and running. There is a little learning curve here (not bad, I'll cover it soon™), but it's really that simple once you see how it works.

Now, I'm going to hit topics in short bursts of coverage. A ton of my own notes are ready to be brain-dumped here for everyone else to see, but they don't need lengthy stories like this post, so I expect to write more code/less blog as I keep going. I am always open to suggestions on pieces to cover, because I find that stuff I know doesn't seem that big or important enough for me to write about compared to the content peers in my field do, so I never end up putting to pen what I've been working on. 