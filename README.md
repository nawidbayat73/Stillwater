# STILLWATER — The Last Tide

**ECHØ Studios · ECHØ CEO Nawid**

Kapitel I–VII für Windows x64. Im Hauptmenü führt **Kapitel IV–VII · Nach der RIGEL** zum späteren Abschnitt. Nach Abschluss von Kapitel III erscheint dort ein direkter Einstieg in Kapitel IV.

## Die Uferstraße

Der Straßenabschnitt von **The Other Shore** und seine überflutete Fassung in **The Last Tide** verwenden neue 3D-Modelle. Die Netzmacherei, Haus Miller, Haus Ward, die Küstenpost, das Café, der Lesesaal, die Bootswerkstatt und das Uhrwerk haben eigene Innenräume und Einrichtungen. Gehwege, Gärten und Kai verbinden die Gebäude. In Kapitel VII weisen Notleuchten durch den Hinterausgang von Haus Ward zum Turm.

[Windows-ZIP mit EXE und Start-BAT](https://raw.githubusercontent.com/nawidbayat73/Stillwater/downloads-uferstrasse/Stillwater-Uferstrasse-Windows.zip) · [Blender-Szene und GLBs](https://raw.githubusercontent.com/nawidbayat73/Stillwater/downloads-uferstrasse/Stillwater-Uferstrasse-3D.zip)

## Start

Entpacke das Windows-ZIP. Starte `Stillwater-The-Last-Tide.exe` oder `Stillwater-Starten.bat`. In Kapitel IV–VII bewegst du dich mit WASD und der Maus. E interagiert mit der Umgebung, F schaltet die Taschenlampe, Umschalt sprintet und Esc öffnet die Pause.

## Projekt bauen

`pack.py` erweitert die ursprüngliche Windows-x64-EXE aus Alpha 0.3.0 um den Wiederaufbau der späteren Kapitel. Die Uferstraße steckt als GLB in `game/scenery/`. Die gepackte Blender-Szene liegt im 3D-ZIP. Der Straßenabschnitt und die Sturm-Ergänzungen stehen dort als getrennte Kollektionen.

```sh
python3 pack.py PFAD/ZUR/BASIS.exe build/Stillwater-The-Last-Tide.exe
```

Für Änderungen an der Geometrie lassen sich die Modelle mit Blender 4.3.2 neu erzeugen. Für die Texturen werden Python 3, Pillow, NumPy und die DejaVu-Schriften benötigt.

```sh
python3 art/textures.py /tmp/stillwater-art/textures
blender -b --python-exit-code 1 --python art/build_scenery.py -- game/scenery build/Stillwater-Uferstrasse.blend
python3 pack.py PFAD/ZUR/BASIS.exe build/Stillwater-The-Last-Tide.exe
```

## Prüfung

Die Laufwegprüfung steuert die Figur mit echten Eingaben durch die Uferstraße, um die Hinweispunkte, den Weg bei Flut und die Kollision am Anleger zu testen. Die Kampagnenprüfung testet die Übergänge und die drei Enden. Beide Befehle verwenden eigene Spielstände.

```sh
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_shore.gd
XDG_DATA_HOME="$(mktemp -d)" godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_campaign.gd
```
