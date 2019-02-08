Title: Powershell Snippets - Interacting with a REST API (and using Gitlab as an example!)
Date: 2019-02-08 09:39
Category: Windows
Tags: powershell, snippets, REST API
Authors: Admiralspark
Summary: Invoke-RestMethod in all its glory!
Status: draft

[Invoke-RestMethod](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-6) is Powershell's awesome REST API tool, and is a valuable function that I seem to be using more and more. Every developer seems to be building a RESTful API of some sort nowadays for their software, and being able to use these API's to reduce your workload and automate away more busywork means you're now free to work on the important jobs!

Today, I'll cover a bit of the syntax and then dive into an example of using it to interact with Gitlab!

## Invoke-RestMethod

As with most Powershell modules, we can use `Get-Help Invoke-RestMethod` and see every possible option that can be used in a way that's not really user-friendly. Here's what it all boils down to:

```powershell
Invoke-RestMethod -Method Get -Uri http://$Server/api/v4/projects/ 
```

This does a simple GET request to an endpoint, and returns the data formatted as powershell objects. For example, here I poll my gitlab instance to find the projects that we have stored there:

```powershell
$r = Invoke-RestMethod -Headers @{ 'PRIVATE-TOKEN'=$Token } -Uri http://$Server/api/v4/projects/
$r | Sort-Object -Property id | Format-Table -Property id, name

id name
-- ----
 1 Documentation
 2 TI-Ansible
 3 TI-Oxidized-Configs
 4 TI-Powershell-Scripts
 5 <snip>
 6 <snip>
```

We'll come back to the extra options I added in a second, but you can see that we sorted the objects returned from the REST API call and spit them into a formatted table. Good stuff! You can make all sorts of calls by specifying a different method: Delete, Get, Head, Merge, Options, Patch, Post, Put, Trace. 

Now, how do we use this?

## Gitlab - grabbing a ZIP of the current Master branch

I had a business need recently to have a recurring powershell task which grabbed the latest copy of the master branch of a repo, wrapped it in a zip, and spit it out to a directory on a share. The following script is what we came up with, to make it a bit modular:

```powershell
<# 
    ---------------------------------------------------------------------------
    Gitlab_Backups_Zip.ps1

    Admiralspark, January 2019
    
    .SYNOPSIS
    Grabs a copy of the latest config backups from Gitlab and puts on the
    server. 
    
    .DESCRIPTION
    Uses the Gitlab API and Invoke-RestMethod to get an authenticated copy of
    the network config backups. This is then date-coded and saved in the 
    Infosrvs directory specified in the defaults below. Then, it deletes any of them older than 2 weeks.
   
    .PARAMETER Token
    This is the personal access token generated from Gitlab.
    https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

    .PARAMETER Server
    The FQDN of the Gitlab server.

    .PARAMETER ProjectID
    The Gitlab Project ID when querying the API. To find this:

        $r = Invoke-RestMethod -Headers @{ 'PRIVATE-TOKEN'=$Token } -Uri http://$Server/api/v4/projects/
        $r | Sort-Object -Property id | Format-Table -Property id, name
    
    .PARAMETER BackupDir
    This is used to set the directory where the backup is stored. If this is
    not set, it defaults to the current Powershell Script Root (where the
    script is being run from).
    
    .EXAMPLE
    Gitlab_Backups_Zip.ps1
    GitLab_Backups_Zip.ps1 -BackupDir \\fileshare\Data\zips

#>

# Add WhatIf support, needs to be next to Param
[CmdletBinding(SupportsShouldProcess=$true)] 

param (
    [string]$Token,
    [string]$Server,
    [string]$ProjectID,
    [string]$BackupDir
)

# Grab date reference variable for logging purposes
$Date = (Get-Date).ToString('yyyyMMdd')

# Concat the filename automatically
$Filename = $Date + "_Config_Backups.zip"

# Save in the local folder if not specified
if (-Not $BackupDir) 
{
    $BackupDir = $PSScriptRoot
} 

$outfile = Join-Path $BackupDir $Filename

# Add headers to the request with our $Token set
$headers = @{
    'PRIVATE-TOKEN' = $Token
}

# GET /projects/:id/repository/archive[.format]
Invoke-RestMethod -Method Get -Headers $headers -Uri http://$Server/api/v4/projects/$projectID/repository/archive.zip -OutFile $outfile

# Now clean up the saved files folder
$OldFiles = Get-ChildItem -Path $BackupDir\* -Include *_Config_Backups.zip | Where-Object {$_.lastwritetime -lt (get-date).adddays(-14)}

# Iterate through the old files and remove them
foreach ($file in $OldFiles) {
    Remove-Item $file
}
```

So let's break it down. 

[Go get an access token from your Gitlab instance](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

Now, run the commands from earlier to find the ID of the repo you need to get zip copies of:

```powershell
$r = Invoke-RestMethod -Headers @{ 'PRIVATE-TOKEN'=$Token } -Uri http://$Server/api/v4/projects/
$r | Sort-Object -Property id | Format-Table -Property id, name
```

Now we set all of the environment variables we need:

```powershell
param (
    [string]$Token,
    [string]$Server,
    [string]$ProjectID,
    [string]$BackupDir
)
```

Then make the call:

```powershell
Invoke-RestMethod -Method Get -Headers $headers -Uri http://$Server/api/v4/projects/$projectID/repository/archive.zip -OutFile $outfile
```

This returns a binary stream (the zip file) which we spit out to $outfile (the directory where we want it). 

I then add some logic in to maintain only two week's worth of the files so we don't fill up the disk:

```powershell
# Now clean up the saved files folder
$OldFiles = Get-ChildItem -Path $BackupDir\* -Include *_Config_Backups.zip | Where-Object {$_.lastwritetime -lt (get-date).adddays(-14)}

# Iterate through the old files and remove them
foreach ($file in $OldFiles) {
    Remove-Item $file
}
```

And now, you kick off the script like so:

```powershell
Gitlab_Backups_Zip.ps1 -Token <tokenHere> -Server gitlab.ti.local -ProjectID 3 -BackupDir "\\datatub\share\backups"
```

and off it goes!