Title: Powershell Snippets - Force Replication Across the Domain
Date: 2018-03-30 17:30
Category: Windows
Tags: powershell, snippets, AD
Slug: posh-replication
Authors: Admiralspark
Summary: The first in a series of Powershell quick tip articles, this one concerning Active Directory replication

Ever run into a situation where you're stuck waiting for a change you made with Active Directory Users and Computers (ADUC) or Exchange Control Panel (ECP) to propagate? Well, this should help you out then! 

Active directory replication is something many organizations don't put a lot of time into planning after they initially set up the domain, or there's so much accumulated technical debt that nobody wants to touch the AD servers as they might be the straw that breaks the camel's back. That means you might use dsa.msc to add a user to a group, but they're located at another site and your replication is an hour, so you tell them they need to wait...which is ridiculous, in 2018. 

This will let you 