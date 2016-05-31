# TbSlack
TbSlack is an IRC bot that extracts posted tweets and reflects them to multiple Slack servers.
This is was a fun experiment and is currently in use for scraping a specific channel on IRC.

This is unversioned as no releases are planned.

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
| Field         | Type          | Description  |
| ------------- |:-------------:| -----:|
| `irc\_server`  | String              | |
| `irc\_port`    | Integer              | |
| `irc\_nick`    | String              | |
| `irc\_channel`    | String              | |
| `accepted\_nick`    | String              | |
| `testing`    | Boolean              | |
| `servers`    | Array[Server Item]              | |

### Server Item
| Field         | Type          | Description  |
| ------------- |:-------------:| -----:|
| `name`        | String              | |
| `username`    | Integer              | |
| `channel      | String              | |
| `batch\_time   | Integer              | |
| `batch\_amount`| Integer              | |
| `url`         | String | |

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
