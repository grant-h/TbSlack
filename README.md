# TbSlack
TbSlack is an IRC bot that extracts posted tweets and reflects them to multiple Slack servers.
This is was a fun experiment and is currently in use for scraping a specific channel on IRC.

This is unversioned as no releases are planned.

## Features
* IRC Twitter message parsing (see below for example)
* Message queuing for Slack API
* Per Twitter user coloring (to easily track the same user)
* Autolinking of Twitter usernames
* Easy to read logging

## Example IRC Twitter Message and Slack Display

```
[2016-07-27 15:55:19.970961] Tweet: <egyp7> RT @HollyGraceful: Anyone familiar with botnet design/analysis got a minute spare to chat about some design considerations for an article I'm writing? PM me :)
[2016-07-27 15:55:21.067707] Tweet: <ProjectZeroBugs> LastPass: design flaw in communication between privileged and unprivileged components https://bugs.chromium.org/p/google-security-research/issues/detail?id=884
```

![IRC Twitter to Slack view](https://i.imgur.com/bmLVaGk.png)

## Installing and Running

All dependencies are provided by pip

```
pip -r requirements.txt
```

Then all you need to run is

```
python tb-slack.py yourconfig.json
```

This will load `yourconfig.json` or `config.json` if no argument was specified.

## Configuration
Below is a description of the configuration options available for this bot

### Top-Level
| Field          | Type                | Description  |
| ---------------|---------------------|--------------|
| `irc_server`   | String              | The IRC hostname to connect to |
| `irc_port`     | Integer             | The IRC port to connect over |
| `irc_nick`     | String              | The bot's nick in IRC|
| `irc_channel`  | String              | Which channel to join upon connecting |
| `accepted_nick`| String              | The nickname to listen for Twitter messages from (everyone else ignored, except when testing is active) |
| `testing`      | Boolean             | Places the bot in to test mode, meaning it will not send to Slack and it will accept private messages |
| `servers`      | Array[Server Item]  | The Slack servers to broadcast to |

### Server Item
| Field         | Type        | Description  |
| ------------- |-------------|--------------|
| `name`        | String      | A helpful name for the Slack server entry |
| `username`    | Integer     | What username the Slack bot should have |
| `channel`     | String      | The channel within the Slack server to broadcast to |
| `batch_time`  | Integer     | How much time until queued Slack messages are flushed |
| `batch_amount`| Integer     | The amount the message queue should hold until it's flushed |
| `url`         | String      | The Slack API URL with secrets |

The bot will queue IRC messages and do a flush once it receives enough messages (`batch_amount`) or the timeout (`batch_time`) is reached. This feature is to be nice to Slack servers with the 10,000 message limit.

### Example configuration

Here's an example configuration that will connect to `irc.example.com:6667` as YourNick and join the channel #listen-channel. Any messages received from the nickname listen\_nick will be parsed for a Tweet message. If a valid tweet is found, it will be transformed to a Slack compatible format and queued for transmission to any servers.

```javascript
{
  "irc_server" : "irc.example.com",
  "irc_port" : 6667,
  "irc_nick" : "YourNick",
  "irc_channel" : "#listen-channel",
  "accepted_nick" : "listen_nick",
  "testing" : false,
  "servers" : [
    {
      "name" : "My Slack Server",
      "username" : "Testbot",
      "channel" : "#tweets",
      "batch_time" : 3600,
      "batch_amount" : 40,
      "url" : "https://hooks.slack.com/services/MYAUTHURL/FOR/SLACK"
    }
  ]
}
```

## License
Unlicensed and free to use for everyone (public domain).
