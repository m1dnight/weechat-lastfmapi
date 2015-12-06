"""
    lastfmapi.py

    author: Christophe De Troyer <christophe@call-cc.be>
      desc: Shows your last played track on last.fm.
     usage:
       /set plugins.var.python.lastfmapi.username yourusername
       /set plugins.var.python.lastfmapi.apikey apikey
       /set plugins.var.python.lastfmapi.command "/me is listening to %s"
       /lastfm

   license: GPLv3

   history:
       0.1 - First version
"""

import weechat
import feedparser

weechat.register("lastfmapi", "Christophe De Troyer", "0.1", "GPL3", "Shows your last played track on last.fm.", "", "")

defaults = {
        "username" : "yourusername",
        "apikey" : "apikey",
        "command" : "/me is listening to %s"
}

cmd_hook_process = ""
cmd_buffer       = ""
cmd_stdout       = ""
cmd_stderr       = ""

for k, v in defaults.iteritems():
        if not weechat.config_is_set_plugin(k):
                weechat.config_set_plugin(k, v)

def lastfm_cmd(data, buffer, args):
        global cmd_hook_process, cmd_buffer, cmd_stdout, cmd_stderr
        if cmd_hook_process != "":
                weechat.prnt(buffer, "Lastfmapi is already running!")
                return weechat.WEECHAT_RC_OK
        cmd_buffer = buffer
        cmd_stdout = ""
        cmd_stderr = ""
        python2_bin = weechat.info_get("python2_bin", "") or "python"

        # Read configuration entires.
        username = weechat.config_get_plugin('username')
        apikey   = weechat.config_get_plugin('apikey')        
        
        cmd_hook_process = weechat.hook_process(
                python2_bin + " -c \"\n"
                "import json\n"
                "import requests\n"
                "import sys\n"
                "api_key  = '%s'\n"
                "api_user = '%s'\n"
                "api_url  = 'http://ws.audioscrobbler.com/2.0/'\n"
                "\n"
                "def get_data():\n"
                "    payload = {'method': 'user.getRecentTracks',\n"
                "               'nowplaying': 'true',\n"
                "               'user': api_user,\n"
                "               'api_key': api_key,\n"
                "               'format': 'json',\n"
                "               'limit': '1'}\n"
                "    r = requests.get(api_url, params=payload)\n"
                "    return r.text\n"
                "\n"
                "def last_or_now_playing():\n"
                "    json_data = get_data()\n"
                "    parsed = json.loads(json_data)\n"
                "    last_track = parsed['recenttracks']['track'][0]\n"
                "    title = last_track['name']\n"
                "    artist = last_track['artist']['#text']\n"
                "    return {'title': title, 'artist': artist}\n"
                "    \n"
                "data = last_or_now_playing()\n"
                "\n"
                "print('{0} - {1}'.format(data['artist'], data['title']))\n" % (apikey, username),
                10000, "lastfm_cb", "")
        return weechat.WEECHAT_RC_OK


def lastfm_cb(data, command, rc, stdout, stderr):
        global cmd_hook_process, cmd_buffer, cmd_stdout, cmd_stderr
        cmd_stdout += stdout
        cmd_stderr += stderr
        if int(rc) >= 0:
                if cmd_stderr != "":
                        weechat.prnt(cmd_buffer, "%s" % cmd_stderr)
                if cmd_stdout != "":
                        weechat.command(cmd_buffer, weechat.config_get_plugin("command") % cmd_stdout.replace('\n',''))
                cmd_hook_process = ""
        return weechat.WEECHAT_RC_OK

hook = weechat.hook_command(
        "lastfm",
        "Shows your last played track on last.fm. Configure first:\n\n"
        "    /set plugins.var.python.lastfmapi.username yourusername\n\n"
        "    /set plugins.var.python.lastfmapi.apikey apikey\n\n"        
        "The posted message is a simple string that will be formatted with 1 argument:\n\n"
        "    /set plugins.var.python.lastfmapi.command is listening to %s\n",
        "", "", "", "lastfm_cmd", "")
