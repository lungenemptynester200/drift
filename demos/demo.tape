Output demos/demo.gif

Set Shell "cmd"
Set FontSize 14
Set Width 1200
Set Height 750
Set Theme "Catppuccin Mocha"
Set Padding 20
Set Framerate 24
Set PlaybackSpeed 1.0

# Hauptbefehl - analyze auf Repo-Root
Type "drift analyze --repo ." Sleep 400ms Enter

# Warte auf vollständige Ausgabe
Sleep 5s

# Zeige CI-Gate Befehl (Exit Code 1 erwartet)
Sleep 1500ms
Type "drift check --fail-on high" Sleep 400ms Enter
Sleep 3s
