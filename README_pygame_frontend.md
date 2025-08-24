# Pygame Frontend für euer Text-Adventure

## Schnellstart
1) Abhängigkeiten installieren:
   ```bash
   pip install pygame
   ```

2) Stellt sicher, dass sich folgende Dateien im selben Ordner befinden:
   - `spiel.py`, `raum.py`, `person.py`, `aufgabe.py`
   - **neu**: `pygame_game.py` (diese Datei)
   - optional: ein Ordner `assets/` mit Hintergrundbildern:
     - Dateinamen: `<raumname>.png` in Kleinbuchstaben, Leerzeichen als `_`.
       Beispiele:
       - `flur.png`
       - `büro_1.png` (oder `büro.png`, je nachdem wie ihr den Raumnamen wollt)
       - `großraumbüro.png`
       - `post.png`
       - `technik.png` / `technikraum.png`
       - `drucker.png` / `druckerraum.png`

3) Starten:
   ```bash
   python pygame_game.py
   ```

## Bedienung
- **Personen** (rechte obere Box): Klick auf eine Person → Dialog-Optionen erscheinen unten (Ja / Nein / Smalltalk).
  - "Ja" erzeugt wie im Terminalspiel eine Aufgabe via `spiel.aufgabe_von_person_p(person)` und erhöht die Beziehung (+2).
  - "Smalltalk" zeigt je nach `rede_lust` Text und erhöht die Beziehung (+1).
- **Wechseln** (rechte mittlere Box): Klick auf Zielraum-Namen → Raumwechsel (nutzt eure `raum_wechseln`-Logik).
- **Aufgaben** (rechte untere Box): Klick auf eine Aufgabe → Aufgabe wird ausgeführt und aus dem Raum entfernt.
- **Log-Fenster** (unten links): zeigt Status, Dialoge und Ereignisse.

## Hinweise
- Wir rufen **keine** `input()`-Funktionen mehr auf (die wären in Pygame blockierend).
  Stattdessen steuert die UI alle Entscheidungen und ruft eure vorhandenen Methoden an (z. B. `aufgabe_von_person_p`).
- Hintergrundbilder sind optional. Wenn keine Datei unter `assets/<raumname>.png` gefunden wird,
  zeigt das Spiel einen farbigen Fallback mit Raumtitel und Beschreibung.
- Für Einsteiger ist das ein guter Ausgangspunkt. Später könnt ihr:
  - Portraits für Personen rendern,
  - ein Inventar/Questscreen hinzufügen,
  - Zustand speichern/laden,
  - Musik/SFX einbauen,
  - Sprites/Animationen nutzen,
  - Entscheidungen persistent tracken (z. B. über Flags im `Spiel`).

Viel Spaß beim Bauen! 🎮
