Title: Powershell Snippets - Cleanly logging to a file
Date: 2018-12-27 19:40
Category: Windows
Tags: powershell, snippets, logging
Authors: Admiralspark
Summary: For when you just need a text file you can tail -f

In powershell, something that's often overlooked is the *logging* of what your script does. Future you and your future users will thank you for setting this up ahead of time, making it easier to troubleshoot issues as you run into them. 

There's two ways to handle this: spitting it to a text file (what we're doing here), and sending it to the Windows Eventlog (I'll cover at a later date). 

## Logging to a File

Here's the entire block we're going to use:

```powershell
$DateMS = (Get-Date).ToString('MMddyyyy-hh:mm:ss.fff')

$LogName = "$(gc env:computername).log"
$Logfile = Join-Path $PSScriptRoot $LogName

Function LogWrite
{
    Param ([string]$logstring)
    Add-Content $Logfile -value "$DateMS + $logstring"
}

$scriptName = $MyInvocation.MyCommand.Name
LogWrite " $scriptName -------------------------------"
```

It might look confusing at first, but I'll break it out into sections as we go. I originally stole the idea from [here (stackoverflow)](https://stackoverflow.com/a/7835668). 

```powershell
$DateMS = (Get-Date).ToString('MMddyyyy-hh:mm:ss.fff')
```

This is pretty straightforward: we can call on **$DateMS** to get the current date/time, formatted as it shows, so that each log entry can be correlated in the file. I chose to break it down to milliseconds here just for my own needs, but you might find that a bit too verbose.

```powershell
$LogName = "$(gc env:computername).log"
$Logfile = Join-Path $PSScriptRoot $LogName
```

**$LogName** makes use of the global environment variable `$(gc env:computername)` which will resolve to the hostname of the machine the script is running on. I actually have my scripts all dump their output to the same file, so I can pull up the file based on the computername and see which scripts ran recently and how far they got. 

**$Logfile** just makes use of Join-Path to cleanly build the path string for where the log files are stored. Repeat after me: **I will never use hardcoded paths!**. I took advantage of the [$PSScriptRoot](https://stackoverflow.com/a/3667376) variable, which always is equal to the **relative** path of the directory where the script is running from, to spit the log outputs in that same folder--this lets me run the script from a share or server (signed, of course) and centrally keep the logs. Obviously, tweak this as needed for where you want to save them. 

```powershell
Function LogWrite
{
    Param ([string]$logstring)
    Add-Content $Logfile -value "$DateMS + $logstring"
}
```

The function itself! LogWrite is the meat of the whole operation here. `Param ([string]$logstring)` just tells the interpreter that this function has one "parameter"; in our case, it takes everything after when we call LogWrite and assigns it to the variable **$logstring**. Then, `Add-Content $Logfile -value "$DateMS + $logstring"` adds a new line to the file **$Logfile**, begins it with the current value of **$DateMS**, and adds the **$logstring** content to that line. Since it's wrapped in a function, we can call on it anywhere in our script now. 

```powershell
$scriptName = $MyInvocation.MyCommand.Name
LogWrite "$scriptName -------------------------------"
```

This last piece is a flair I added for cleanliness. `$MyInvocation.MyCommand.Name` evaluates to the name of the script, so I have the script always add this line with several dashes to cleanly split up the content of the log file. I find this especially useful when I have extremely verbose logs and I repeatedly run scripts for testing purposes, but it's not really needed. 

Speaking of, this is how we use our LogWrite function:

```powershell
LogWrite "Here's a log entry I want to make!"
```

Pretty simple eh? I like to take every line that I write to screen with Write-Error/Write-Verbose/Write-Debug and copy it here as well, so that my log *file* has all of the information I'll need even if I don't write it all to screen. Another good tip: make heavy use of Write-Verbose over just writing everything to screen, you'll have a much cleaner logging to console that way and anyone who wants the scrolling text can just run your script with **-Verbose** to get the full output!

Hope that helps a few people add some simple logging for now, at least until they get their system logging sorted out!

Cheers.