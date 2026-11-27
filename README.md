# Augenzimmer

Webseite für den Fernseher im **Augenzimmer** (Plastik aus dem *Gedankenaufzug*, Kunstmappe 2026).
Ein altes Handy steckt als Bildschirm im Zimmer und spielt das Augen-Video in Dauerschleife.

## Ablauf auf dem Handy

Einfache Schleife: `video/nachrichten.mp4` läuft einmal ganz, dann ein kurzes Störbild, dann `video/auge.mp4`
(Auge öffnet sich erschrocken, schaut umher, schließt sich), dann wieder Störbild und Nachrichten – endlos.
Einmal tippen schaltet in den Vollbildmodus; der Bildschirm bleibt an (Wake Lock über HTTPS).

Die Version mit Kamera-Auslöser und Blickverfolgung ist im Verlauf (Commit „Echtes Augen-Video …“) gespeichert
und kann später wieder aufgegriffen werden. Die Datei `video/auge_echt.mp4` gehört zu dieser Version.

## Neues Augen-Video einsetzen

Neue Aufnahme (iPhone, .mov) stabilisieren und umwandeln, dann die Zeiten unter `CLIP` in `index.html` anpassen:
```
ffmpeg -i IMG_xxxx.mov -vf "vidstabdetect=tripod=60:result=t.trf" -f null -
ffmpeg -i IMG_xxxx.mov -vf "vidstabtransform=input=t.trf:tripod=1:zoom=6,crop=iw:iw*9/16,scale=1280:720" -an -c:v libx264 -crf 23 -g 5 -pix_fmt yuv420p -movflags +faststart video/auge_echt.mp4
```
Die .mov-Originale werden nicht ins Repo übernommen (`.gitignore`).

## Veröffentlichen mit GitHub Pages

1. Repository auf GitHub veröffentlichen (GitHub Desktop: **Publish repository**, Haken bei „Keep this code private“ **entfernen** – Pages ist im kostenlosen Konto nur für öffentliche Repositories verfügbar).
2. Auf github.com im Repository: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**.
3. Nach ein bis zwei Minuten ist die Seite erreichbar unter
   **https://akingstone.github.io/augenzimmer/**

## Auf dem Handy im Zimmer

- Seite öffnen, einmal tippen → Vollbild, Video startet, Bildschirm bleibt an (Wake Lock über HTTPS).
- Besser noch: **Zum Home-Bildschirm hinzufügen** und von dort starten – dann ohne Browserleiste.
- Automatische Bildschirmsperre in den Handy-Einstellungen ausschalten und Ladekabel anschließen.
- Seite einmal laden, solange WLAN da ist; das Video läuft danach in Schleife.

## Nachrichten-Video (`video/nachrichten.mp4`)

Ausgedachter Sender „INNENWELT 24“ mit echten, frei lizenzierten Aufnahmen. Laufband-Zahlen aus Umweltbundesamt- und IPCC-Zusammenfassungen.
Neu bauen: `python3 werkzeug/nachrichten_bauen.py werkzeug/nachrichten_segmente.json video/nachrichten.mp4` (Pfade in der JSON anpassen).

### Bildnachweise
- Krieg in der Ukraine (Kyjiw 2022–2024): Staatlicher Katastrophenschutzdienst der Ukraine (dsns.gov.ua), CC BY 4.0, über Wikimedia Commons
- Camp Fire, Kalifornien 2018: California Air National Guard / DVIDS, gemeinfrei (Wikimedia Commons, `DOD_106218663.webm`)
- Lahaina, Hawaii 2023: B-Roll of Hawaii Wildfire, DVIDS, gemeinfrei (Wikimedia Commons)
- Leine-Hochwasser Hemmingen 2017: Wikimedia Commons, CC0
- Ahrtal 2021: Jean-Christophe Verhaegen / © European Union, CC BY 4.0 (Wikimedia Commons, „Consequences of the floodings in Ahrweiler, Germany“ Nr. 3, 28, 55)
- Hurrikane 2017: NASA Goddard, „Intense String of Hurricanes Seen From Space“, gemeinfrei
- Augen-Video: eigene Aufnahme von Annika Königstein
