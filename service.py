# -*- coding: utf-8 -*-

'''
*********************************************************
Script pro generaci playlistu z OTA služby OrangeTV SK
*********************************************************
Script je odvozen z Kodi addon service.playlist.o2tv,
který byl vytvořen z původního addon autora Štěpána Orta.
*********************************************************
'''

import os
import time
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib3
import traceback
from subprocess import call
import common as c
from o2tvgo import AuthenticationError
from o2tvgo import ChannelIsNotBroadcastingError
from o2tvgo import NoPurchasedServiceError
from o2tvgo import O2TVGO
from o2tvgo import TooManyDevicesError
params = False

_username_ = ""
_password_ = ""
_device_id_ = ""
_access_token_ = ""
_start_automatic_ = True
_start_manual_ = False
_start_hour_ = 6
_start_period_ = 6
_start_enable_ = True
_start_delay_ = 10
_playlist_type_ = 0
_stream_quality_ = 0
_channel_epgname_ = 0
_channel_epgid_ = 0
_channel_group_ = 0
_channel_groupname_ = ""
_channel_logo_ = 0
_channel_logopath_ = ""
_channel_logourl_ = ""
_channel_logogithub_ = ""
_channel_logoname_ = ""
_myscript_ = ""
_myscript_name_ = ""
_ffmpeg_ = ""
_last_downloaded_ = ""
_last_skipped_ = ""
_last_time_ = ""
_last_start_ = ""
_next_time_ = ""
_last_stest_ = ""
_next_test_ = ""
_o2tvgo_ = ""
_quality_ = 0
_name_ = ""
_icon_ = ""
_id_ = ""
_addon_ = ""
_profile_ = ""
_lang_ = ""
_version_ = ""
_playlist_path_ = ""
_playlist_src_ = ""
_playlist_dst_ = ""
_playlist_streamer_ = ""
_postdown_script_ = ""
_settings_file_ = ""
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
_start_period_hours_ = 1, 2, 3, 4, 6, 8, 12, 24
_no_error_ = 0
_authent_error_ = 1
_toomany_error_ = 2
_nopurch_error_ = 3
_error_code_ = 0, 1, 2, 3


def get_setting(setting):
    global _addon_
    return _addon_.getSetting(setting).strip().decode('utf-8')


def get_setting_bool(setting):
    return get_setting(setting).lower() == "true"


def get_setting_int(setting, default):
    try:
        return int(float(get_setting(setting)))
    except ValueError:
        return default


def set_setting(setting, value):
    global _addon_
    _addon_.setSetting(setting, str(value))


def _test_file(name):
    global _profile_
    try:
        f = open(xbmc.translatePath(os.path.join(_profile_, name)), 'r')
    except IOError:
        return False
    else:
        f.close()
        return True


def _time_change(name):
    global _profile_
    f = xbmc.translatePath(os.path.join(_profile_, name))
    return os.stat(f).st_mtime


def load_settings(save=False):
    global _username_
    _username_ = get_setting('username')
    global _password_
    _password_ = get_setting('password')
    global _device_id_
    _device_id_ = get_setting('device_id')
    global _access_token_
    _access_token_ = get_setting('access_token')

    global _start_automatic_
    _start_automatic_ = get_setting_bool('start_automatic')
    global _start_manual_
    _start_manual_ = get_setting_bool('start_manual')
    global _start_hour_
    _start_hour_ = get_setting_int('start_hour', 6)
    if save:
        set_setting('start_hour', _start_hour_)
    global _start_period_
    _start_period_ = get_setting_int('start_period', 6)
    if save:
        set_setting('start_period', _start_period_)
    global _start_enable_
    _start_enable_ = get_setting_bool('start_enable')
    global _start_delay_
    _start_delay_ = get_setting_int('start_delay', 10)
    if save:
        set_setting('start_delay', _start_delay_)

    global _playlist_type_
    _playlist_type_ = get_setting_int('playlist_type', 0)
    global _stream_quality_
    _stream_quality_ = get_setting_int('stream_quality', 0)
    global _channel_epgname_
    _channel_epgname_ = get_setting_int('channel_epgname', 0)
    global _channel_epgid_
    _channel_epgid_ = get_setting_int('channel_epgid', 0)
    global _channel_group_
    _channel_group_ = get_setting_int('channel_group', 0)
    global _channel_groupname_
    _channel_groupname_ = get_setting('channel_groupname')
    global _channel_logo_
    _channel_logo_ = get_setting_int('channel_logo', 0)
    global _channel_logopath_
    _channel_logopath_ = get_setting('channel_logopath')
    global _channel_logourl_
    _channel_logourl_ = get_setting('channel_logourl')
    global _channel_logogithub_
    _channel_logogithub_ = get_setting_int('channel_logogithub', 0)
    global _channel_logoname_
    _channel_logoname_ = get_setting_int('channel_logoname', 0)
    global _myscript_
    _myscript_ = get_setting_bool('myscript')
    global _myscript_name_
    _myscript_name_ = get_setting('myscript_name')
    global _ffmpeg_
    _ffmpeg_ = get_setting('ffmpeg_path')
    global _last_downloaded_
    _last_downloaded_ = get_setting('last_downloaded')
    global _last_skipped_
    _last_skipped_ = get_setting('last_skipped')
    global _last_time_
    _last_time_ = get_setting('last_time')
    global _last_start_
    _last_start_ = get_setting('last_start')
    global _next_time_
    _next_time_ = get_setting('next_time')
    global _last_stest_
    _last_stest_ = get_setting('last_test')
    global _next_test_
    _next_test_ = get_setting('next_test')


def test_settings():
    global _playlist_type_
    _username = get_setting('username')
    _password = get_setting('password')
    _login_error = not _username or not _password
    _start_automatic = get_setting_bool('start_automatic')
    _start_error = not _start_automatic
    _param_error = (_playlist_type_ == 0) or (_playlist_type_ > 3)
    return _login_error, _start_error, _param_error


def open_settings():
    global _id_
    execute('Addon.OpenSettings(%s)' % _id_, True)


def idle():
    return execute('Dialog.Close(busydialog)')


def yes_no_dialog(_line1_, _line2_, _line3_, _heading_=_name_, _nolabel_='', _yeslabel_=''):
    idle()
    return dialog.yesno(_heading_, _line1_, _line2_, _line3_, _nolabel_, _yeslabel_)


def notification(message, icon=_icon_, _time=5000):
    if icon == 'INFO':
        icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR':
        icon = xbmcgui.NOTIFICATION_ERROR
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%i,%s)" % (_name_, message.decode('utf-8'), _time, icon))


def info_dialog(message, icon=_icon_, _time=5000, sound=False):
    if icon == '':
        icon = _addon_.getAddonInfo('icon')
    elif icon == 'INFO':
        icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR':
        icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(_name_, message, icon, _time, sound=sound)


def log(msg, level=xbmc.LOGDEBUG):
    global _name_
    if type(msg).__name__ == 'unicode':
        msg = msg.encode('utf-8')
    xbmc.log("[%s] %s" % (_name_, msg.__str__()), level)


def log_not(msg):
    log(msg, level=xbmc.LOGNOTICE)


def _log_dbg(msg):
    log(msg, level=xbmc.LOGDEBUG)


def log_err(msg):
    log(msg, level=xbmc.LOGERROR)


def log_traceback(exc, exc_traceback):
    tb_lines = [line.rstrip('\n') for line in
                traceback.format_exception(exc.__class__, exc, exc_traceback)]
    for tb_line in tb_lines:
        log_err('Traceback: %s' % (c.to_string(tb_line)))


def _log_wrn(msg):
    log(msg, level=xbmc.LOGWARNING)


def _fetch_channels():
    global _o2tvgo_, _no_error_, _nopurch_error_, _toomany_error_, _authent_error_
    channels = None
    while not channels:
        try:
            channels = _o2tvgo_.live_channels()
        except AuthenticationError:
            return None, _authent_error_
        except TooManyDevicesError:
            return None, _toomany_error_
        except NoPurchasedServiceError:
            return None, _nopurch_error_
    return channels, _no_error_


def _reload_settings():
    _addon_.openSettings()
    global _username_
    _username_ = _addon_.getSetting("username")
    global _password_
    _password_ = _addon_.getSetting("password")
    global _stream_quality_
    global _quality_
    _stream_quality_ = int(_addon_.getSetting('stream_quality'))
    if _stream_quality_ == 0:
        _quality_ = _quality_low_
    else:
        _quality_ = _quality_high_
    global _o2tvgo_
    _o2tvgo_ = O2TVGO(_device_id_, _username_, _password_, _quality_, _log_dbg)


def _logo_file(channel):
    global _channel_logoname_
    if _channel_logoname_ == 0:
        f = c.logo_name(channel) + '.png'
    elif _channel_logoname_ == 1:
        f = c.logo_name(channel) + '.jpg'
    elif _channel_logoname_ == 2:
        f = channel + '.png'
    elif _channel_logoname_ == 3:
        f = channel + '.jpg'
    else:
        return ''
    return f


def _logo_path_file(channel):
    global _channel_logo_, _channel_logopath_, _channel_logourl_, _channel_logogithub_
    if _channel_logo_ == 2:
        path_file = os.path.join(_channel_logopath_, _logo_file(channel))
        if not os.path.isfile(path_file):
            path_file = ""
    elif _channel_logo_ == 3:
        path_file = _channel_logourl_ + _logo_file(channel)
    elif _channel_logo_ == 4:
        path_file = c.marhy[_channel_logogithub_] + c.logo_name(channel) + '.png'
    else:
        return ''
    return path_file


def channel_playlist():
    global _channel_group_, _channel_groupname_, _myscript_, _myscript_name_, _channel_logo_, \
        _playlist_type_, _channel_epgname_, _channel_epgid_, _ffmpeg_, _no_error_
    channels, _code = _fetch_channels()
    if not channels:
        return _code, -1, -1

    channels_sorted = sorted(channels.values(), key=lambda _channel: _channel.weight)
    if _channel_group_ == 1:
        group = c.default_group_name
    else:
        group = _channel_groupname_

    if _myscript_ == 1:
        streamer = c.pipe + os.path.join(_playlist_path_, _myscript_name_)
    else:
        streamer = c.pipe + os.path.join(_playlist_path_, _playlist_streamer_)

    playlist_src = '#EXTM3U\n'
    playlist_dst = '#EXTM3U\n'
    _num = 0
    _err = 0
    for channel in channels_sorted:
        try:
            log_not("Adding: " + channel.name)
            playlist_src += '#EXTINF:-1, %s\n%s\n' % (c.to_string(channel.name), c.to_string(channel.url()))
            playlist_dst += c.build_channel_lines(channel, _channel_logo_, _logo_path_file(channel.name), streamer, group, _playlist_type_, _channel_epgname_, _channel_epgid_, _channel_group_)
            _num += 1
        except ChannelIsNotBroadcastingError:
            log_not("... Not broadcasting. Skipped.")
            _err += 1
        except AuthenticationError:
            return _authent_error_, 0, 0
        except TooManyDevicesError:
            return _toomany_error_, 0, 0
    c.write_file(playlist_src, xbmc.translatePath(os.path.join(_profile_, _playlist_src_)), _log_dbg)
    c.write_file(playlist_dst, xbmc.translatePath(os.path.join(_profile_, _playlist_dst_)), _log_dbg)
    if _playlist_type_ == 3:
        c.write_streamer(xbmc.translatePath(os.path.join(_profile_, _playlist_streamer_)),
                         xbmc.translatePath(os.path.join(_profile_, _playlist_src_)), _ffmpeg_, _log_dbg)
    set_setting('last_time', time.strftime('%Y-%m-%d %H:%M'))
    set_setting('last_downloaded', c.to_string(_num))
    set_setting('last_skipped', c.to_string(_err))
    return _no_error_, _num, _err


def next_time_():
    global _start_period_, _start_hour_
    start_period = int(_start_period_hours_[int(_start_period_)])
    act_time_sec = time.time()
    act_date = time.strftime('%Y-%m-%d')
    act_start = ('%s %s:00' % (act_date, _start_hour_))
    act_start_sec = time.mktime(time.strptime(act_start, '%Y-%m-%d %H:%M'))
    offset_raw = (act_time_sec - act_start_sec) / (start_period * 3600)
    offset = int(offset_raw)
    if offset_raw >= 0:
        offset += 1
    offset *= start_period
    _next_time_sec = act_start_sec + offset * 3600
    _next_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(_next_time_sec))
    _log_dbg('next_time_ result: %s %d %d %s %f %f' % (act_start, act_start_sec, _next_time_sec,
                                                       _next_time, offset_raw, offset))
    return _next_time, _next_time_sec


def to_master(master):
    return int(time.mktime(time.strptime(time.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')) + master - time.time())


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    _addon_ = xbmcaddon.Addon('service.playlist.orangetv')
    _profile_ = xbmc.translatePath(_addon_.getAddonInfo('profile'))
    _lang_ = _addon_.getLocalizedString
    _name_ = _addon_.getAddonInfo('name')
    _version_ = _addon_.getAddonInfo('version')
    _id_ = _addon_.getAddonInfo('id')
    _icon_ = xbmc.translatePath(os.path.join(_addon_.getAddonInfo('path'), 'icon.png'))

    addon = xbmcaddon.Addon
    dialog = xbmcgui.Dialog()
    progressDialog = xbmcgui.DialogProgress()
    keyboard = xbmc.Keyboard
    infoLabel = xbmc.getInfoLabel
    addonInfo = addon().getAddonInfo
    execute = xbmc.executebuiltin

    _error_str_ = 'OK', 'AuthenticationError', 'TooManyDevicesError', 'NoPurchasedServiceError'
    _error_lang_ = 'OK', _lang_(30003), _lang_(30006), _lang_(30008)
    _quality_high_ = 'PC'
    _quality_low_ = 'MOBILE'
    _cycle_step_ = 5
    _master_delay_ = 60
    _playlist_path_ = _profile_
    _playlist_src_ = 'orangetv.generic.m3u8'
    _playlist_dst_ = 'orangetv.playlist.m3u8'
    _playlist_streamer_ = 'streamer.sh'
    _settings_file_ = 'settings.xml'

    urllib3.disable_warnings()

    log_not('Preparation for Service')

    load_settings(True)
    login_error, start_error, param_error = test_settings()
    while login_error or start_error or param_error:
        line1 = _lang_(30800)
        line2 = _lang_(30801) % (_lang_(30802) if login_error else '',
                                 _lang_(30803) if start_error else '',
                                 _lang_(30804) if param_error else '')
        line3 = _lang_(30805)
        if yes_no_dialog(line1, line2, line3):
            open_settings()
            xbmc.sleep(1000)
            load_settings(True)
            login_error, start_error, param_error = test_settings()
            continue
        else:
            break
    load_settings(True)

    if not _device_id_:
        first_device_id = c.device_id()
        second_device_id = c.device_id()
        if first_device_id == second_device_id:
            _device_id_ = first_device_id
        else:
            _device_id_ = c.random_hex16()
        set_setting("device_id", _device_id_)
    c.write_streamer(xbmc.translatePath(os.path.join(_profile_, _playlist_streamer_)),
                     xbmc.translatePath(os.path.join(_profile_, _playlist_src_)), _ffmpeg_, _log_dbg)

    try:
        if _stream_quality_ == 0:
            _quality_ = _quality_low_
        else:
            _quality_ = _quality_high_

        _o2tvgo_ = O2TVGO(_device_id_, _username_, _password_, _quality_, _log_dbg)

        log_not('Waiting %s s for Service' % _start_delay_)
        xbmc.sleep(_start_delay_ * 1000)

        log_not('START Service')
        info_dialog(_lang_(30049))
        set_setting('last_start', time.strftime('%Y-%m-%d %H:%M:%S'))

        start = True
        init_error = True
        last_minute = False
        error_report = False
        start_report = False
        change_report = False
        time_change_saved_sec = 0
        cycle_step = _cycle_step_
        master_delay = 0
        next_time = ''

        while not monitor.abortRequested():
            try:
                if monitor.waitForAbort(_cycle_step_):
                    break
                if master_delay > _cycle_step_:
                    master_delay = to_master(_master_delay_)
                    continue
                master_delay = _master_delay_ - _cycle_step_
                _log_dbg('Service running: full cycle - time: %s' % (time.strftime('%Y-%m-%d %H:%M:%S')))

                time_change_sec = _time_change(_settings_file_)
                if time_change_sec != time_change_saved_sec:
                    time_change_saved_sec = time_change_sec
                    time_change = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_change_sec))
                    log_not('Change in settings.xml: %s' % time_change)
                    load_settings()
                    log_not('Settings loaded')
                    login_error, start_error, param_error = test_settings()
                    if not (login_error or start_error or param_error):
                        next_time, next_time_sec = next_time_()
                        if next_time != _next_time_:
                            set_setting('next_time', next_time)
                            _next_time_ = next_time
                            log_not('Change of settings next time - next start: %s' % _next_time_)
                            change_report = True

                if login_error or start_error or param_error:
                    if not error_report:
                        error_report = True
                        info_dialog(_lang_(30048))
                        _log_wrn('Unfinished settings - login : %s, start : %s, param : %s' % (
                            c.to_string(login_error), c.to_string(start_error), c.to_string(param_error)))
                    _log_dbg('Service running: short cycle (Unfinished settings) - time: %s' % (
                        time.strftime('%Y-%m-%d %H:%M:%S')))
                    continue

                if error_report:
                    log_not('Finished settings')

                if start:
                    start = False
                    if not _next_time_ or _start_enable_:
                        next_time_sec = 0
                        log_not('Counter to download clearing - immediate start')
                    else:
                        start_report = True
                        next_time_sec = time.mktime(time.strptime(_next_time_, '%Y-%m-%d %H:%M'))
                        log_not('Setting next time - next start: %s' % _next_time_)

                if error_report or start_report or change_report:
                    error_report = False
                    start_report = False
                    change_report = False
                    info_dialog(_lang_(30047) % _next_time_)

                if (time.time() < next_time_sec) or not _start_automatic_:
                    continue

                log_not('Download starts')
                info_dialog(_lang_(30040))
                code, num, err = channel_playlist()
                if code == _no_error_:
                    info_dialog(_lang_(30041) % (num, err))
                    log_not('Download finishes %d/%d channel(s) downloaded/skipped' % (num, err))
                else:
                    info_dialog(_error_lang_[code])
                    log_not('Download aborted: %s' % (_error_str_[code]))

                next_time, next_time_sec = next_time_()
                if next_time != _next_time_:
                    set_setting('next_time', c.to_string(next_time))
                rc = call(_postdown_script_);
                if not xbmc.getCondVisibility('Pvr.IsPlayingTV') and _playlist_type_ == 1:
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":false}}')
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":true}}')
                info_dialog(_lang_(30047) % next_time)

            except Exception as ex:
                info_dialog(_lang_(30042))
                ex_type, ex_value, ex_traceback = sys.exc_info()
                log_err('LOOP error - exc_type: %s, exc_value: %s' % (c.to_string(ex_type), c.to_string(ex_value)))
                log_traceback(ex, ex_traceback)

        info_dialog(_lang_(30043))
        log_not('DONE Service')
    except Exception as ex:
        info_dialog(_lang_(30042))
        ex_type, ex_value, ex_traceback = sys.exc_info()
        log_err('INIT error - exc_type: %s, exc_value: %s' % (c.to_string(ex_type), c.to_string(ex_value)))
        log_traceback(ex, ex_traceback)
        info_dialog(_lang_(30043))
        log_not('DONE Service')
