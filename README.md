# Augenzimmer

Webseite für den Fernseher im **Augenzimmer** (Plastik aus dem *Gedankenaufzug*, Kunstmappe 2026).
Ein altes Handy steckt als Bildschirm im Zimmer und spielt das Augen-Video in Dauerschleife.

## Ablauf auf dem Handy

Die Nachrichten (`video/nachrichten.mp4`) laufen in Schleife. Erkennt die Frontkamera eine Person vor dem Zimmer, kommt ein Störbild,
das gezeichnete Auge reißt erschrocken auf und folgt der Person mit dem Blick. Ist 6 Sekunden niemand mehr da, schließt es sich
und die Nachrichten laufen weiter. Das Kamerabild wird nur im Handy ausgewertet, nichts wird gespeichert oder gesendet.

Das Auge wird live aus Einzelteilen zusammengesetzt (`auge/`: Lid-Stellungen, Iris, Geometrie), damit es der Person folgen kann.
`video/auge.mp4` ist die feste Fassung (z. B. für den Video-Link in der Mappe).

Einstellungen über die Adresse, z. B. `https://akingstone.github.io/augenzimmer/?debug=1`:
- `debug=1` – Kamerabild und Messwerte anzeigen
- `spiegeln=0` – Blickrichtung links/rechts tauschen, falls das Auge in die falsche Richtung schaut
- `schwelle=0.02` – empfindlicher (Standard 0.03)
- `warten=10` – Sekunden ohne Person, bis das Auge zugeht (Standard 6)
- Am Computer: Taste `A` löst das Auge testweise aus

## Video einfügen

1. Das Video als **`auge.mp4`** in den Ordner `video/` legen.
2. Format: MP4 (H.264), Hochformat oder Querformat passend zum Handy im Zimmer, **unter 25 MB** (GitHub erlaubt höchstens 100 MB pro Datei).
3. Ein iPhone-Video (.mov/HEVC) vorher umwandeln, z. B. mit HandBrake (Preset „Fast 1080p30“) oder:
   ```
   ffmpeg -i auge.mov -c:v libx264 -crf 26 -preset veryfast -an -movflags +faststart auge.mp4
   ```
   Ton wird weggelassen, weil der Browser stummes Video automatisch abspielen darf.

Solange `video/auge.mp4` fehlt, zeigt die Seite ein gezeichnetes Ersatz-Auge, das blinzelt und sich umschaut.

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
- Augen-Video: Zeichnung „Trauer“ von Annika Königstein, animiert
