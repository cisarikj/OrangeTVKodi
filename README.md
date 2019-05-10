OrangeTVKodi 2v1
============

Tato sada skriptu a doplňku pro Kodi slouží pro vygenerování playlistů tak, aby služba OrangeTV Slovensko šla použít v Kodi, nebo v TVHeadendu.
Obě části jsou víceméně funkčně stejné a slouží k témuž účelu. Kterou část použijete záleží na vás.

Část 1 - Doplněk pro Kodi
-------------------------
Doplněk je vhodný zejména pro případy, kdy pro přehrávání používáte pouze IPTV Simple Client, nebo kdy je Kodi a TVHeadend spouštěn na jednom stroji.

### Instalace
- Stáhněte si [poslední verzi](https://github.com/cisarikj/OrangeTVKodi/releases/latest)
- Otevřete Kodi a povolte si **Neznámé zdroje** v **Nastavení -> Systém -> Doplňky** 
- Nainstalujte doplněk ze staženého zip souboru
- Proveďte nastavení doplňku - zadejte své uživatelské jméno a heslo. Doplněk najdete v sekci **Služby**

Pokud vše nastavíte správně, ve složce nastavení doplňku by se měly objevit soubory `orangetv.generic.m3u8` a `orangetv.playlist.m3u8`, které použijte pro IPTV Simple Client, nebo TVHeadend.
Umístění složky nastavení doplňku se liší podle platformy. Na windows bývá v C:\Users\jméno_uživatele\AppData\Roaming\Kodi\userdata\addon_data\service.playlist.orangetv\

Více informací naleznete na fóru [xbmc-kodi.cz](https://www.xbmc-kodi.cz/prispevek-playlist-orangetv-addon)

Část 2 - Samostatný skript
--------------------------
Skript je vhodný pro pokročilé uživatele, kteří mají aspoň základní znalosti Linuxu. Je vhodné ho spouštět periodicky (např. 1x za 24hod.)

### Instalace
- Nainstalujte si Python verze 2.7 (skript zatím není kompatibilní s Pythonem verze 3)
- Stáhněte si [poslední verzi](https://github.com/cisarikj/OrangeTVKodi/releases/latest) a rozbalte zip soubor do libovolné složky
- spusťte `pip install -r requirements.txt`, čímž si nainstalujete potřebné podpůrné knihovny
- upravte si nastavení v souboru `config.py`, zejména uživatelské jméno a heslo. Položku `device_id` můžete nechat prázdnou.
- spusťte skript pomocí příkazu `python playlist.py` nebo `./playlist.py`

Více informací naleznete na fóru [xbmc-kodi.cz](https://www.xbmc-kodi.cz/prispevek-playlist-orangetv-addon)

Řešení potíží
-------------
Nikdo není dokonalý a potíže se se mohou objevit kdykoliv.
V současné době je známo několik problémů na které byste mohli narazit:
- Nastavení skriptu verze 0.1 není kompatibilní s předchozími. Nachází se v jiném souboru, takže musíte zapsat veškerá nastavení znovu.
- V případě potíží při instalaci nové verze doplňku pro Kodi pomáhá smazat adresář s nastaveními. Na windows se nachází např. v `C:\Users\jméno_uživatele\AppData\Roaming\Kodi\userdata\addon_data\service.playlist.orangetv\`.
- Potíže s přihlášením zatím nejsou zcela vyřešeny a mohou záviset na problémech na straně Orange. 

Pokud jste objevili jiný problém, nebo chybu nejdříve hledejte v [seznamu chyb](https://github.com/Pavuucek/O2TVKodi/issues) a až v případě, že svojí chybu nenajdete, [vytvořte nové hlášení](https://github.com/cisarikj/OrangeTVKodi/issues/new).

Autoři
------

- Štěpán Ort
- JiRo
- Cromac
- Michal Kuncl (Pavůček)
- Jan Cisárik (johnyzh94) - úprava O2TVKodi pre OrangeTV

Pomoct s vývojem můžete i vy! Jak na to? Stačí si vytvořit [fork](https://help.github.com/articles/fork-a-repo) tohoto repozitáře, provést příslušné změny a poté otevřít [pull request](https://help.github.com/articles/using-pull-requests).
