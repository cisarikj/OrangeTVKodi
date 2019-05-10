@echo off
set zip="c:\program files\7-zip\7z.exe"
if exist service.playlist.o2tv.zip del service.playlist.o2tv.zip
%zip% a service.playlist.o2tv.zip ..\o2tvkodi\ -r -x!*.pyc -x!.idea -x!.git -x!device_id -x!playlist.log -x!o2tv.generic.m3u8 -x!o2tv.playlist.m3u8 -x!streamer.sh*
%zip% rn service.playlist.o2tv.zip o2tvkodi\ service.playlist.o2tv\
%zip% d service.playlist.o2tv.zip service.playlist.o2tv\config.py
%zip% rn service.playlist.o2tv.zip service.playlist.o2tv\config.py.sample service.playlist.o2tv\config.py
