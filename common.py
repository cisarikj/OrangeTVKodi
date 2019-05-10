#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import stat
import unicodedata
from uuid import getnode as get_mac

import config as cfg

version = '0.1'
date = '2019-05-08'
pipe = 'pipe://'
default_group_name = "OrangeTV"
marhy = 'https://marhycz.github.io/picons/640/', 'https://marhycz.github.io/picons/1024/'
log_file = os.path.join(cfg.playlist_path, 'playlist.log')
id_file = os.path.join(cfg.playlist_path, 'device_id')
authent_error = 'AuthenticationError'
toomany_error = 'TooManyDevicesError'
nopurch_error = 'NoPurchasedServiceError'


def device_id():
    mac = get_mac()
    hexed = hex((mac * 7919) % (2 ** 64))
    return ('0000000000000000' + hexed[2:-1])[16:]


def random_hex16():
    return ''.join([random.choice('0123456789abcdef') for x in range(16)])


def to_string(text):
    if type(text).__name__ == 'unicode':
        output = text.encode('utf-8')
    else:
        output = str(text)
    return output


def logo_name(channel):
    channel = unicode(channel, 'utf-8')
    channel = unicodedata.normalize('NFKD', channel)
    channel = channel.lower()
    name = ''
    for char in channel:
        if not unicodedata.combining(char) and (char.isalpha() or char.isdigit()):
            name += char
    return name


def add_param(param, value, cond):
    item = ''
    if cond:
        item = ' %s="%s"' % (param, str(value))
    return item


def write_file(content, name, log=None):
    if not log is None:
        log("Saving file: " + name)
    f = open(name, 'w')
    f.write(content)
    f.close()


def try_exec(name):
    f = name
    try:
        sts = os.stat(f)
        if not (sts.st_mode & stat.S_IEXEC):
            os.chmod(f, sts.st_mode | stat.S_IEXEC)
    except:
        pass


def write_streamer(streamer_file, playlist_file, ffmpeg_cmd, log=None):
    streamer_code = '#! /bin/bash\n' + \
                    'source=$*\n' + \
                    'tempplaylist=$(mktemp -u)".m3u8"\n' + \
                    'stream=$(grep -A 1 "${source}$" ' + playlist_file + \
                    ' | head -n 2 | tail -n 1)\n' + \
                    'wget -qO ${tempplaylist} ${stream}\n' + \
                    'streamcount=$(cat ${tempplaylist} | grep -Eo "(http|https)://[\da-z./?A-Z0-9\D=_-]*" | wc -l)\n' + \
                    'streamcount=$((streamcount-1))\n' + \
                    'if  [ "$streamcount" = "-1" ]; then streamcount=0; fi\n' + \
                    ffmpeg_cmd + ' -protocol_whitelist file,http,https,tcp,tls -fflags +genpts ' + \
                    '-loglevel fatal -i ${tempplaylist} -probesize 32 -reconnect_at_eof 1 -reconnect_streamed 1 ' + \
                    '-c copy -map p:${streamcount}? -f mpegts -tune zerolatency -bsf:v h264_mp4toannexb,dump_extra ' + \
                    '-mpegts_service_type digital_tv pipe:1\n'

    if not log is None:
        log('Saving Streamer: ' + streamer_file)
    write_file(streamer_code, streamer_file + '.sample')
    # _to_file(c.streamer_code, os.path.join(cfg.playlist_path, cfg.playlist_streamer + '.sample'))
    try_exec(streamer_file + '.sample')
    write_file(streamer_code, streamer_file)
    try_exec(streamer_file)


def build_channel_lines(channel, channel_logo, logoname, streamer, group, playlist_type, channel_epg_name, channel_epg_id, channel_group):
    name = channel.name
    logo = to_string(channel.logo_url)
    url = to_string(channel.url())
    epgname = name
    epgid = name
    r = ""
    # číslo programu v epg
    # viz https://www.o2.cz/file_conver/174210/_025_J411544_Razeni_televiznich_programu_O2_TV_03_2018.pdf
    channel_weight = to_string(channel.weight)
    # logo v mistnim souboru - kdyz soubor neexistuje, tak pouzit url
    if (channel_logo > 1) and (logoname != ""):
        logo = logoname
    if playlist_type == 1:
        r += '#EXTINF:-1'
        r += add_param('tvg-name', epgname, channel_epg_name != 0)
        r += add_param('tvg-id', epgid, channel_epg_id != 0)
        r += add_param('tvg-logo', logo, channel_logo != 0)
        r += add_param('tvg-chno', channel_weight, channel_epg_id != 0)
        r += add_param('group-titles', group, channel_group != 0)
        r += ', %s\n%s\n' % (name, url)
    if (playlist_type == 2) or (playlist_type == 3):
        r += '#EXTINF:-1'
        r += add_param('tvg-id', epgid, channel_epg_id != 0)
        r += add_param('tvg-logo', logo, channel_logo != 0)
        r += add_param('tvg-chno', channel_weight, channel_epg_id != 0)
        r += add_param('group-titles', group, channel_group != 0)
        r += ', %s\n' % name
        if playlist_type == 2:
            r += '%s\n' % url
        if playlist_type == 3:
            r += '%s %s\n' % (streamer, name)
    return r