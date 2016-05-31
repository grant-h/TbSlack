#!/usr/bin/env python
# An IRC tweet -> Slack bot in python
#
# Grant Hernandez <grant.h.hernandez@gmail.com>
# Based off of IRC example by
#   Joel Rosdahl <joel@rosdahl.net>

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

from server import SlackServer, SlackPost

import re
import json
import datetime
from ttp import ttp  # twitter text parsing

# From http://tools.medialab.sciences-po.fr/iwanthue/index.php
# Sorted by their color difference
COLORS = ["#6a0032", "#01cf49", "#604bf7", "#74c200", "#8900b2",
          "#b3dc3d", "#00179a", "#e2cf4a", "#ff53f4", "#008c43",
          "#e6008a", "#5d8200", "#4b7cff", "#936d00", "#0264ce",
          "#ac1c00", "#0192f7", "#ff5259", "#00aeb1", "#c30038",
          "#019abe", "#940034", "#94d7f4", "#7f3400", "#ed97ff",
          "#232e00", "#c1b9ff", "#00664b", "#ff7d8e", "#002172",
          "#c1d693", "#5a005b", "#bdd2cc", "#2a1632", "#fcbfb8",
          "#005053", "#ff99bf", "#00556d"]


class TbSlack(irc.bot.SingleServerIRCBot):

    def __init__(
            self,
            channel,
            nickname,
            server,
            port,
            slackServers,
            accepted_nick,
            testing=False):
        recon = irc.bot.ExponentialBackoff(min_interval=0.01)
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname, recon=recon)
        self.channel = channel
        self.colormap = {}
        self.colormapIter = 0
        self.testing = testing
        self.accepted_nick = accepted_nick

        self.slack = slackServers
        self.ttp = ttp.Parser(include_spans=True)

        print(
            "TbSlack connecting to {}:{} as {}".format(
                server, port, nickname))
        print("Listening to IRC messages from {}".format(self.accepted_nick))

        if self.testing:
            print("** TESTING MODE ACTIVE")

        for i in slackServers:
            print("- Broadcasting to {}".format(i))

    def on_nicknameinuse(self, c, e):
        print("WARNING: nickname in use...")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("Now joining {}".format(self.channel))
        c.join(self.channel)

    def on_disconnect(self, c, e):
        print("WARNING: disconnected from server...")

    def on_join(self, c, e):
        print("Joined {}".format(self.channel))

    # strips IRC colors as per the spec. Probably doesnt work for strange cases
    def strip_colors(self, msg):
        return re.sub("\x03([0-9]{1,2})?(,[0-9]{1,2})?", "", msg)

    def on_pubmsg(self, c, e):
        src = e.source.nick
        msg = e.arguments[0]

        # strip color control characters
        msg = self.strip_colors(msg)

        if src == self.accepted_nick:
            self.process_tb(e, msg)
        else:
            print("PUB_MSG: <{}> {}".format(src, msg.encode("utf-8")))

    def on_privmsg(self, c, e):
        src = e.source.nick
        msg = e.arguments[0]

        # strip color control characters
        msg = self.strip_colors(msg)

        print("PRIVMSG: <{}> {}".format(src, msg.encode("utf-8")))

        if self.testing:
            self.process_tb(e, msg)

    def process_tb(self, e, tweet):
        print("[{}] Tweet: {}".format(
            str(datetime.datetime.today()), tweet.encode("utf-8")))

        tokens = tweet.split(" ")

        if len(tokens) < 1:
            print("Malformed tweet (no tokens)")
            return

        tweeter = tokens[0]
        tokens = tokens[1:]
        final_msg = ""
        header = ""

        if re.match("^<.+>$", tweeter) is None:
            print("Malformed tweet (invalid tweeter)")
            return

        tweeter = re.findall("^<(.+)>$", tweeter)[0]

        if len(tokens) < 1:
            print("Malformed tweet (blank tweet)")
            return

        is_rt = tokens[0] == "RT"

        def mklink(target, text=""):
            if text == "":
                return u"<{}>".format(target)
            else:
                return u"<{}|{}>".format(target, text)

        def mkat(t):
            return mklink(u"https://twitter.com/{}".format(t),
                          u"@{}".format(t))

        def mkhash(t):
            return mklink(u"https://twitter.com/hashtag/{}".format(t),
                          u"#{}".format(t))

        if is_rt:
            target = tokens[1]
            tokens = tokens[2:]

            if re.match("^@.+:$", target) is None:
                print("Malformed retweet (bad target)")
                return

            target = re.findall("^@(.+):$", target)[0]

            header = "{} :repeat: {}".format(mkat(tweeter), mkat(target))
        else:
            header = "{} tweeted".format(mkat(tweeter))

        if len(tokens) < 1:
            print("Malformed tweet (missing body after header)")
            return

        # we are limited to one color in Slack. Base it off of the tweeter
        color = ""

        if tweeter in self.colormap:
            color = self.colormap[tweeter]
        else:
            c = COLORS[self.colormapIter]
            self.colormapIter = (self.colormapIter + 1) % len(COLORS)

            self.colormap[tweeter] = c
            color = c

        body = " ".join(tokens)
        res = self.ttp.parse(body)
        users = set([r[0] for r in res.users])
        tags = set([r[0] for r in res.tags])

        for i in users:
            body = body.replace(u"@" + i, mkat(i))

        for i in tags:
            body = body.replace(u"#" + i, mkhash(i))

        final_msg += header + ": " + body

        # print final_msg

        if len(self.slack):
            for i in self.slack:
                i.postRich(header, body, color, tweet)
        else:
            if self.testing:
                post = SlackPost()
                post.addAttachment(header, body, color, tweet)

                print("Test send: " + str(post))


def banner():
    print("TbSlack by Grant")
    print("")


def usage():
    import sys
    global EXENAME

    print("usage: " + EXENAME + " config.json")
    sys.exit(1)


def main(args):
    banner()

    slackServers = []
    configFp = None

    try:
        configName = args[0] if len(args) else "config.json"
        configFp = open(configName, "r")
    except IOError:
        usage()

    config = json.load(configFp)
    configFp.close()

    # load slack servers
    for i in config["servers"]:
        slackServers.append(
            SlackServer(
                i["url"],
                i["name"],
                i["username"],
                i["channel"],
                (i["batch_time"],
                 i["batch_amount"])))

    # load irc info
    server = config["irc_server"]
    port = config["irc_port"]
    channel = config["irc_channel"]
    nickname = config["irc_nick"]
    accepted_nick = config["accepted_nick"]
    testing = config["testing"]

    bot = TbSlack(channel, nickname, server,
                  port, slackServers, accepted_nick, testing)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("Disconnecting on user Ctrl-C")
        bot.disconnect()

if __name__ == "__main__":
    import sys

    global EXENAME
    EXENAME = sys.argv[0]

    main(sys.argv[1:])
