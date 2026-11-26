# STILLWATER — The Last Tide

**ECHØ Studios · ECHØ CEO Nawid**

Dieser Wiederaufbau verwendet den aus acht BIN-Dateien wiederhergestellten Windows-Build für Kapitel I–III als Basis. Kapitel IV–VII wurden daraus und aus den erhaltenen Szenenbeschreibungen neu aufgebaut. Im Hauptmenü lässt sich der Abschnitt nach der RIGEL direkt starten. Auch am Ende von Kapitel III erscheint der Einstieg.

## Windows

Entpacke das Windows-ZIP. Starte `Stillwater-The-Last-Tide.exe` oder doppelklicke auf `Stillwater-Starten.bat`. Die neuen Kapitel verwenden WASD, Maus, E zum Interagieren, F für die Taschenlampe, Umschalt zum Sprinten und Esc für die Pause.

## Modelle und Wiederaufbau

Die GLB-Dateien für Höhlen, Platform 6, Other Shore, die überflutete Stadt und die Resonanzkammer lassen sich in Blender importieren. Die Integration und die Erstellung der neuen Schauplätze liegen unter `game/`. Das Windows-ZIP und das Modell-ZIP liegen unter Releases.

Zum Bauen wird die ursprüngliche x64-EXE aus Alpha 0.3.0 benötigt.

```sh
python3 pack.py PFAD/ZUR/BASIS.exe build/Stillwater-The-Last-Tide.exe
XDG_DATA_HOME=/tmp/stillwater-test godot --headless --fixed-fps 60 --main-pack build/Stillwater-The-Last-Tide.exe --script tools/test_campaign.gd
XDG_DATA_HOME=/tmp/stillwater-export godot --headless --main-pack build/Stillwater-The-Last-Tide.exe --script tools/export_models.gd -- /tmp/stillwater-modelle
```

Der Test startet den eingebetteten Spielstand im Godot-Editor-Binary und prüft den Einstieg im Hauptmenü, die Kapitelzustände und die drei Ausgänge. Die Protokolle testen die Windows-Datei als eingebettetes Spielpaket unter Linux. Eine Ausführung der EXE auf einem Windows-PC steht aus.
