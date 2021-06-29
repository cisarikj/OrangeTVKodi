#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Wrapper pro O2TV Go
"""

import requests

__author__ = "Štěpán Ort"
__license__ = "MIT"
__version__ = "1.1.8"
__email__ = "stepanort@gmail.com"

_COMMON_HEADERS = {"X-NanguTv-App-Version": "Android#7.6.3",
                   "X-NanguTv-Device-Name": "Nexus 7",
                   "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; Nexus 6 Build/LMY47A)",
                   "Accept-Encoding": "gzip",
                   "Connection": "Keep-Alive"}


def _to_string(text):
    if type(text).__name__ == 'unicode':
        output = text.encode('utf-8')
    else:
        output = str(text)
    return output


# Kanál


class LiveChannel:

    # JiRo - doplněn parametr kvality
    def __init__(self, o2tv, channel_key, name, logo_url, weight, quality):
        self._o2tv = o2tv
        self.channel_key = channel_key
        self.name = name
        self.weight = weight
        self.logo_url = logo_url
        self.quality = quality  # doplněn parametr kvality

    def url(self):
        if not self._o2tv.access_token:
            self._o2tv.refresh_access_token()
        access_token = self._o2tv.access_token
        if not self._o2tv.subscription_code:
            self._o2tv.refresh_configuration()
        subscription_code = self._o2tv.subscription_code
        playlist = None
        while access_token:
            params = {"serviceType": "LIVE_TV",
                      "subscriptionCode": subscription_code,
                      "channelKey": self.channel_key,
                      "deviceType": self.quality,
                      "streamingProtocol": "HLS"}  # JiRo - doplněn parametr kvality
            headers = _COMMON_HEADERS
            cookies = {"access_token": access_token,
                       "deviceId": self._o2tv.device_id}
            req = requests.get('http://app01.gtm.orange.sk/sws/server/streaming/uris.json',
                               params=params, headers=headers, cookies=cookies)
            json_data = req.json()
            access_token = None
            if 'statusMessage' in json_data:
                status = json_data['statusMessage']
                if status == 'bad-credentials':
                    access_token = self._o2tv.refresh_access_token()
                elif status == 'channel.not-found':
                    raise ChannelIsNotBroadcastingError()
                else:
                    raise Exception(status)
            else:
                # Pavuucek: Pokus o vynucení HD kvality
                playlist = ""
                # pro kvalitu STB nebo PC se pokusíme vybrat HD adresu.
                # když není k dispozici, tak první v seznamu
                for uris in json_data["uris"]:
                    if self.quality == "STB" or self.quality == "PC":
                        if uris["resolution"] == "HD" and playlist == "":
                            playlist = uris["uri"]
                    else:
                        # pro ostatní vracíme SD adresu
                        if uris["resolution"] == "SD" and playlist == "":
                            playlist = uris["uri"]
                # playlist nebyl přiřazený, takže první adresa v seznamu
                if playlist == "":
                    playlist = json_data["uris"][0]["uri"]
        return playlist


class ChannelIsNotBroadcastingError(BaseException):
    pass


class AuthenticationError(BaseException):
    pass


class TooManyDevicesError(BaseException):
    pass


# JiRo - doplněna kontrola zaplacené služby
class NoPurchasedServiceError(BaseException):
    pass


class O2TVGO:

    def __init__(self, device_id, username, password, quality, log_function=None):  # JiRo - doplněn parametr kvality
        self.username = username
        self.password = password
        self._live_channels = {}
        self.access_token = None
        self.subscription_code = None
        self.locality = None
        self.offer = None
        self.device_id = device_id
        self.quality = quality  # JiRo - doplněn parametr kvality
        self.log_function = log_function

    def _log(self, message):
        if self.log_function:
            self.log_function(message)
    def get_access_token_password(self):
        self._log('Getting Token via password...')
        if not self.username or not self.password:
            raise AuthenticationError()
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
        data = {'grant_type': 'password',
				'client_id': 'orangesk-mobile',
				'client_secret': 'e4ec1e957306e306c1fd2c706a69606b',
				'isp_id': '5',
                'username': self.username,
                'password': self.password,
                'platform_id': 'b0af5c7d6e17f24259a20cf60e069c22',
				'custom': 'orangesk-mobile',
				'response_type': 'token'
				}
        req = requests.post('https://oauth01.gtm.orange.sk/oauth/token',
                            data=data, headers=headers, verify=False)
        j = req.json()
        if 'error' in j:
            error = j['error']
            if error == 'authentication-failed':
                self._log('Authentication Error')
                return None
            else:
                raise Exception(error)
        self.access_token = j["access_token"]
        self.expires_in = j["expires_in"]
        self._log('Token OK')
        return self.access_token
		
    def refresh_access_token(self):
        if not self.access_token:
            self.get_access_token_password()
        if not self.access_token:
            self._log('Authentication Error (failed to get token)')
            raise AuthenticationError()
        return self.access_token

    def refresh_configuration(self):
        if not self.access_token:
            self.refresh_access_token()
        access_token = self.access_token
        headers = _COMMON_HEADERS
        cookies = {"access_token": access_token, "deviceId": self.device_id}
        req = requests.get(
            'https://app01.gtm.orange.sk/sws//subscription/settings/subscription-configuration.json', headers=headers,
            cookies=cookies)
        j = req.json()
        if 'errorMessage' in j:
            error_message = j['errorMessage']
            status_message = j['statusMessage']
            # JiRo - změna z 'unauthorized-device' na 'devices-limit-exceeded'
            if status_message == 'devices-limit-exceeded':
                raise TooManyDevicesError()
            else:
                raise Exception(error_message)
        self.subscription_code = _to_string(j["subscription"])
        self.offer = j["billingParams"]["offers"]
        self.tariff = j["billingParams"]["tariff"]
        self.locality = j["locality"]

    def live_channels(self):
        if not self.access_token:
            self.refresh_access_token()
        access_token = self.access_token
        if not self.offer:
            self.refresh_configuration()
        offer = self.offer
        if not self.tariff:
            self.refresh_configuration()
        tariff = self.tariff
        if not self.locality:
            self.refresh_configuration()
        locality = self.locality
        quality = self.quality  # JiRo - doplněn parametr kvality
        if len(self._live_channels) == 0:
            headers = _COMMON_HEADERS
            cookies = {"access_token": access_token,
                       "deviceId": self.device_id}
            params = {"locality": self.locality,
                      "tariff": self.tariff ,
                      "isp": "5",
					  "imageSize": "LARGE",
                      "language": "slo",
                      "deviceType": self.quality,
                      "liveTvStreamingProtocol": "HLS",
                      "offer": self.offer}  # doplněn parametr kvality
            req = requests.get('http://app01.gtm.orange.sk/sws/server/tv/channels.json',
                               params=params, headers=headers, cookies=cookies)
            j = req.json()
            purchased_channels = j['purchasedChannels']
            if len(purchased_channels) == 0:  # JiRo - doplněna kontrola zaplacené služby
                raise NoPurchasedServiceError()  # JiRo - doplněna kontrola zaplacené služby
            items = j['channels']
            for channel_id, item in items.iteritems():
                if channel_id in purchased_channels:
                    live = item['liveTvPlayable']
                    if live:
                        channel_key = _to_string(item['channelKey'])
                        logo = _to_string(item['logo'])
                        if not logo.startswith('http://'):
                            logo = 'http://app01.gtm.orange.sk/' + logo
                        name = _to_string(item['channelName'])
                        weight = item['weight']
                        self._live_channels[channel_key] = LiveChannel(
                            self, channel_key, name, logo, weight, quality)  # doplněn parametr kvality
            done = False
            offset = 0     
                           
        return self._live_channels
