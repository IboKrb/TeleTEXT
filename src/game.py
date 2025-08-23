class Raum:
    def __init__(self, name, beschreibung, aufgaben=None, personen=None, gegenstaende=None, verbindungen=None):
        self.name = name
        self.beschreibung = beschreibung
        self.aufgaben = aufgaben if aufgaben is not None else []
        self.personen = personen if personen is not None else []
        self.gegenstaende = gegenstaende if gegenstaende is not None else []
        self.verbindungen = verbindungen if verbindungen is not None else []

class Aufgabe:
    def __init__(self, id, name, beschreibung):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.beschreibung}"

class Spiel:
    def __init__(self):
        self.raeume = self.raum_erzeugen()
        self.aktueller_raum = self.raeume["flur"]

    def raum_erzeugen(self):
        # Räume zuerst ohne Verbindungen erzeugen
        flur = Raum("Flur", "Du siehst einen langen Gang mit ganz vielen Räumen.")
        post = Raum("Post", "Du siehst einen kleinen Raum mit einem Tisch und einem Stuhl.",
                    aufgaben=[
                        Aufgabe(1, "Post abholen", "Hole die Post von Holger ab."),
                        Aufgabe(2, "Brief sortieren", "Sortiere die eingegangenen Briefe.")
                    ],
                    personen=["Flo"])
        technikRaum = Raum("Technik", "Du siehst einen Raum voller Computer und Technik.",
                           aufgaben=[Aufgabe(3, "Drucker reparieren", "Repariere den Drucker im Technikraum.")],
                           personen=["Holger"])
        druckerRaum = Raum("Drucker", "Du siehst einen Raum mit einem Drucker.",
                           aufgaben=[Aufgabe(4, "Papier nachfüllen", "Lege Papier in den Drucker ein."),
                                     Aufgabe(5, "Toner wechseln", "Wechsle den Toner im Drucker.")],
                           personen=["Holger"])

        # Verbindungen setzen
        flur.verbindungen = [post, technikRaum, druckerRaum]
        post.verbindungen = [flur]
        technikRaum.verbindungen = [flur]
        druckerRaum.verbindungen = [flur]

        return {
            "flur": flur,
            "post": post,
            "technikraum": technikRaum,
            "druckerraum": druckerRaum
        }

    def raum_wechseln(self, neuer_raum):
        for raum in self.aktueller_raum.verbindungen:
            if raum.name.lower() == neuer_raum:
                self.aktueller_raum = raum
                self.raum_betreten()
                return
        print("Du kannst nicht dorthin gehen.")

    def aufgabe_ausfuehren(self, aufgabe_id):
        for aufgabe in self.aktueller_raum.aufgaben:
            if aufgabe.id == aufgabe_id:
                print(f"Aufgabe '{aufgabe.name}' ausgeführt!")
                self.aktueller_raum.aufgaben.remove(aufgabe)
                return
        print("Ungültige Aufgaben-ID.")

    def raum_betreten(self, ):
        print(f"\nDu bist jetzt im {self.aktueller_raum.name}.")
        print("Du kannst folgende Aktionen ausführen:")
        print(" - deinen Raum wechseln:", [raum.name for raum in self.aktueller_raum.verbindungen])
        if self.aktueller_raum.aufgaben != "":
            print(" - aufgabe anzeigen: anzeigen")
        eingabe = input("Was möchtest du tun? ").strip().lower()
        if eingabe == "post" or eingabe == "technik" or eingabe == "drucker" or eingabe == "flur":
            self.raum_wechseln(eingabe)
        elif eingabe == "anzeigen":
            if self.aktueller_raum.aufgaben:
                print("\nAufgaben in diesem Raum:")
            for aufgabe in self.aktueller_raum.aufgaben:
                print(aufgabe)
                if aufgabe != "":
                    aufgabe_id = int(input("Welche Aufgabe möchtest du ausführen (ID eingeben)? "))
                    self.aufgabe_ausfuehren(aufgabe_id)
        else:
            print("Keine Aufgaben mehr hier.")


    def spiel_starten(self):
        print("Willkommen zum Spiel!")
        while True:
            self.raum_betreten()
            
if __name__ == "__main__":
    spiel = Spiel()
    spiel.spiel_starten()
