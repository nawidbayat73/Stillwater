# STILLWATER — The Last Tide

**ECHØ Studios · ECHØ CEO Nawid**

Kapitel I–VII für Windows x64. Im Hauptmenü führt **Kapitel IV–VII · Nach der RIGEL** zum späteren Abschnitt. Nach Abschluss von Kapitel III erscheint dort ein direkter Einstieg in Kapitel IV.

## Überarbeitete Schauplätze

Im neuen Einstieg hört Elias Maras Nachricht an Bord. Das rote Hafenlicht markiert den Anleger, bevor es über den Nordkai zur Straßensperre geht. Blackcliff, die RIGEL, der Gezeitenstollen und Platform 6 haben neue Ausstattungen, lesbare Schilder und szenenspezifisches Licht. Die überarbeitete Uferstraße verbindet die eingerichteten Häuser, Läden und Werkstätten. In der Resonanzkammer verändert sich das Licht und die Anlage reagiert auf jede Entscheidung.

Der Nordkai bekam neue Bootsmodelle, Hafenobjekte, Fahrzeuge und Küstenvegetation. Fotografische Texturen und Normalenkarten geben Holz, Fels, Asphalt und Metall mehr Tiefe. Wände, Türen, Geländer und größere Requisiten haben passende Kollisionskörper. Kleine Dekorationen wie Tassen und loses Papier lassen sich weiterhin aus der Nähe betrachten.

[Windows-ZIP mit EXE und BATs](https://media.githubusercontent.com/media/nawidbayat73/Stillwater/downloads-materialien/Stillwater-Materialien-Windows.zip) · [Download-BAT](https://raw.githubusercontent.com/nawidbayat73/Stillwater/downloads-materialien/Stillwater-Download.bat) · [Blender-Szenen und GLBs](https://media.githubusercontent.com/media/nawidbayat73/Stillwater/downloads-materialien/Stillwater-Materialien-3D.zip)

## Start

Entpacke das Windows-ZIP. Starte `Stillwater-The-Last-Tide.exe` oder `Stillwater-Starten.bat`. In Kapitel IV–VII bewegst du dich mit WASD und der Maus. E interagiert mit der Umgebung, F schaltet die Taschenlampe, Umschalt sprintet und Esc öffnet die Pause.

## Projekt bauen

`pack.py` erweitert die ursprüngliche Windows-x64-EXE aus Alpha 0.3.0 um den Wiederaufbau der späteren Kapitel. `game/scenery/` enthält die neuen 3D-Sets als GLB und die zugehörigen Layouts für Kollisionen, Licht und Interaktionspunkte. Das 3D-ZIP enthält die Modelle in drei Blender-Dateien mit gepackten Texturen. Die fotografischen Oberflächen stammen von Poly Haven. [Quellen und Lizenz](art/surfaces/Quellen.md)

```sh
python3 pack.py PFAD/ZUR/BASIS.exe build/Stillwater-The-Last-Tide.exe
```

Für Änderungen an der Geometrie lassen sich die Modelle mit Blender 4.3.2 neu erzeugen. Für die Texturen werden Python 3, Pillow, NumPy und die DejaVu-Schriften benötigt.

```sh
python3 art/textures.py /tmp/stillwater-art/textures --game-maps game/finish
blender -b --python-exit-code 1 --python art/build_scenery.py -- game/scenery build/Stillwater-Uferstrasse.blend
blender -b --python-exit-code 1 --python art/build_campaign.py -- game/scenery build/Stillwater-Szenen.blend
blender -b --python-exit-code 1 --python art/build_coastal.py -- game/scenery build/Stillwater-Kueste.blend
python3 pack.py PFAD/ZUR/BASIS.exe build/Stillwater-The-Last-Tide.exe
```

## Prüfung

Die Laufwegprüfungen steuern die Figur vom Boot bis zu Nora und bei Flut durch die Uferstraße. Die Kollisionsprüfung steuert die Figur gegen Hindernisse und durch geöffnete Türen in allen sieben Kapiteln. Die Kampagnenprüfung testet die späteren Übergänge und die drei Enden. Alle Befehle verwenden eigene Spielstände.

```sh
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_arrival.gd
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_shore.gd
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_campaign.gd
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_solids.gd
```
