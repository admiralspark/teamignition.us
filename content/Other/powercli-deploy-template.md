Title: Deploying VMs from Template via PowerCLI
Date: 2018-09-20 5:30
Category: Other
Tags: powercli, vmware
Authors: Admiralspark
Summary: Tired of trying to make the flash client work? Want automation? Use PowerCLI!

## The Goods

This will be quick and easy, but it's easier for me to be able to reference it than to type it out every time. You need to have your information ready ahead of time for your environment. If you've never done this before, I'll run through the enumeration via CLI now.

First, you need the name of your template:

``` powershell
Get-Template
```

This will spit out the templates pre-made. I assume you have a template ready to deploy from already? ;)

Once you have that, assign the object to a session variable like so:

``` powershell
$template = Get-Template -Name 'CentOS7_Template'
```

Now, you need to find a datastore to store the vmdx files on. We typically try to balance them out, so I look for datastores in our site by free space:

```powershell
Get-Datastore | where { $_.Name -match "Branch" } | sort -Property FreeSpaceGB -Descending
```

This will kick back a list of the datastores that match by order of free space left. Once you pick one, assign the object to a variable:

```powershell
$ds = Get-Datastore -Name 'BRANCH-DEV5'
```

Now, find a cluster to assign the hosts to (or, assign to specific host if you need/want to, but this is typically better):

```powershell
Get-Cluster
```

...and assign that baby's resource pool to a variable:

```powershell
$rp = Get-ResourcePool -Location 'Branch_Cluster'
```

Now add in a few more variables:

```powershell
$name = 'TeamIgnition'
$numCPU = 1
$ram = 2
```

...and run it out! (no splatting for effect)

```powershell
New-VM -Template $template -Name $name -ResourcePool $rp -Datastore $ds -DiskStorageFormat Thick | `
Set-VM -NumCpu $numCPU -MemoryGB $ram -Confirm:$false | `
Start-VM -Confirm:$false
```

And there you go! As you can see by the variable assignments, you could totally use this to spin up VM's based on a csv sheet, or input from other sources. I'm still working to have Rundeck triggers for it, but it should be trivial once I have time. 