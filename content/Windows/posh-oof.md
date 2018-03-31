Title: Powershell Snippets - Setting Out of Office (OOF) on a user's mailbox
Date: 2018-03-30 21:30
Category: Windows
Tags: powershell, snippets, exchange
Authors: Admiralspark

<p class="text-warning">This must be run in either the Exchange Management Shell or through a remote powershell connection to your Exchange servers. </p>

## Out of Office

This one is pretty straightforward--user's gone from work unexpectedly and you need to set their out of office reply without resetting their password or granting yourself access rights to their account. The script is here:

```powershell
Set-MailboxAutoReplyConfiguration -Identity domainuser -AutoReplyState Scheduled -StartTime "3/20/2018 08:00:00" -EndTime "3/22/2018 08:00:00" -InternalMessage "Hello, I'm out of the office on unplanned leave, if you need immediate assistance please contact $Supervisor at SupEmail@domain.name, thank you!" -ExternalMessage "Hello, I'm out of the office on unplanned leave, if you need immediate assistance please contact $Supervisor, thank you!" -ExternalAudience Known
```

The command makes use of the [Set-MailboxAutoReplyConfiguration](https://technet.microsoft.com/en-us/library/dd638217(v=exchg.160).aspx) cmdlet in powershell. This is mirrored by the [Get-MailboxAutoReplyConfiguration](https://technet.microsoft.com/en-us/library/dd638081(v=exchg.160).aspx) cmdlet which will tell you what's currently set. 

These are the options we can use:

<table class="table table-hover">
  <thead>
    <tr>
      <th scope="col">Value</th>
      <th scope="col">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Identity</th>
      <td>The domain <b>username</b> of the user who you're configuring OOF for.</td>
    </tr>
    <tr>
      <th scope="row">AutoReplyState</th>
      <td><b>Enabled</b>, <b>Disabled</b>, or <b>Scheduled</b>. This lets you set specific times for it to be on, or just permanently on/off if you don't know the date range. </td>
    </tr>
    <tr>
      <th scope="row">StartTime and EndTime</th>
      <td>The start/end dates which are required when AutoReplyState is set to Scheduled. Usage is (including quotes): <b>"MM/DD/YYYY HH:MM:SS"</b> in 24h format.</td>
    </tr>
    <tr>
      <th scope="row">InternalMessage</th>
      <td>The message which will be shown to internal recipients.</td>
    </tr>
    <tr>
      <th scope="row">ExternalMessage</th>
      <td>The message which will be shown to external recipients. This may not need to include contact information.</td>
    </tr>
    <tr>
      <th scope="row">ExternalAudience</th>
      <td><b>None</b>, <b>Known</b>, or <b>All</b>. All is default if this is not specified, none will only reply with an OOF message to internal people, and Known will reply to internal emails and anyone who is in the contacts list (GAL and personal one). 
</td>
    </tr>
  </tbody>
</table> 