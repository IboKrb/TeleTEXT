from raum import Raum
from aufgabe import Aufgabe
from person import Person

class Spiel:
    def __init__(self):
        self.personen = self.personen_erzeugen()
        self.raeume = self.raum_erzeugen()
        self.aktueller_raum = self.raeume["flur"]

    def personen_erzeugen(self):
        holger = Person("Holger", "Teamleiter", "Sehr nett und immer hilfsbereit.", rede_lust=4)
        flo = Person("Flo", "Stellvertretender Teamleiter", "Gesprächsfreudig – kann nicht aufhören zu reden!", rede_lust=7)
        kirsten = Person("Kirsten", "Projektmanager", "Nervig und anstrengend.", rede_lust=3)
        return {
            "holger": holger,
            "flo": flo,
            "kirsten": kirsten
        }

    def raum_erzeugen(self):
        flur = Raum("Flur", "Du siehst einen langen Gang mit ganz vielen Räumen.")
        buero1 = Raum("Büro 1", "Ein schickes Büro mit PC und Kaffee.", personen=[self.personen["holger"]])
        grossraumbuero = Raum("Großraumbüro", "Viele Tische und Arbeitsplätze.", personen=[self.personen["flo"], self.personen["kirsten"]])
        post = Raum("Post", "Du siehst einen kleinen Raum mit einem Tisch und einem Stuhl.")
        technikraum = Raum("Technik", "Du siehst einen Raum voller Computer und Technik.")
        druckerraum = Raum("Drucker", "Du siehst einen Raum mit einem Drucker.")

        flur.verbindungen = [buero1, grossraumbuero, post, technikraum, druckerraum]
        buero1.verbindungen = [flur]
        grossraumbuero.verbindungen = [flur]
        post.verbindungen = [flur]
        technikraum.verbindungen = [flur]
        druckerraum.verbindungen = [flur]

        post.aufgaben = []
        technikraum.aufgaben = []
        druckerraum.aufgaben = []

        return {
            "flur": flur,
            "büro": buero1,
            "großraumbüro": grossraumbuero,
            "post": post,
            "technikraum": technikraum,
            "druckerraum": druckerraum
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

    def raum_betreten(self):
        print(f"\nDu bist jetzt im {self.aktueller_raum.name}. \n")
        print(self.aktueller_raum.beschreibung)
        print("\nDu kannst folgende Aktionen ausführen:")
        aktionen = ["raum wechseln", "mit person sprechen", "aufgabe ausführen", "aufgabe anzeigen", "status"]
        print(" - " + ", ".join(aktionen))
        if self.aktueller_raum.personen == []:
            print("\nIn diesem Raum sind keine Personen.")
        elif self.aktueller_raum.personen: 
            print("\nIn diesem Raum sind:", [p.name for p in self.aktueller_raum.personen])

        eingabe = input("\nWas möchtest du tun? ").strip().lower()
        if eingabe == "raum wechseln":
            print("\nMögliche Räume:", [raum.name for raum in self.aktueller_raum.verbindungen])
            zielraum = input("\nWohin möchtest du gehen? ").strip().lower()
            self.raum_wechseln(zielraum)
        elif eingabe == "mit person sprechen":
            if self.aktueller_raum.personen:
                print("\nMit wem möchtest du sprechen?", [p.name for p in self.aktueller_raum.personen])
                person_name = input("Name der Person: ").strip().capitalize()
                for p in self.aktueller_raum.personen:
                    if p.name.lower() == person_name.lower():
                        antwort = p.sprich()
                        if antwort == "task":
                            self.aufgabe_von_person_p(p)
                            p.beziehung_steigern(2)
                        else:
                            p.beziehung_steigern(1)
                        break
                else:
                    print("\nDiese Person ist nicht hier.")
            else:
                print("\nHier ist gerade niemand.")
        elif eingabe == "aufgabe anzeigen":
            if self.aktueller_raum.aufgaben:
                for aufgabe in self.aktueller_raum.aufgaben:
                    print(aufgabe)
            else:
                print("\nKeine Aufgaben verfügbar.")
        elif eingabe == "aufgabe ausführen":
            if self.aktueller_raum.aufgaben:
                for aufgabe in self.aktueller_raum.aufgaben:
                    print(aufgabe)
                try:
                    aufgabe_id = int(input("Aufgabe ID ausführen: "))
                    self.aufgabe_ausfuehren(aufgabe_id)
                except ValueError:
                    print("\nUngültige Eingabe.")
            else:
                print("Keine Aufgaben hier.")
        elif eingabe == "status":
            for pname, p in self.personen.items():
                print(f"\n{p.name}: Beziehung {p.relationship}")
        else:
            print("Aktion nicht erkannt.")

    def aufgabe_von_person_p(self, person):
        if person.name == "Holger":
            neue_aufgabe = Aufgabe(10, "Brief abgeben", "Gehe zur Post und gib den Brief ab.")
            self.raeume["post"].aufgaben.append(neue_aufgabe)
            print(f"\n{person.name} gibt dir die Aufgabe: {neue_aufgabe}")
        elif person.name == "Flo":
            neue_aufgabe = Aufgabe(11, "Dokument drucken", "Drucke ein Dokument im Druckerraum.")
            self.raeume["druckerraum"].aufgaben.append(neue_aufgabe)
            print(f"\n{person.name} gibt dir die Aufgabe: {neue_aufgabe}")
        elif person.name == "Kirsten":
            neue_aufgabe = Aufgabe(12, "Technik kontrollieren", "Überprüfe die Technik im Technikraum.")
            self.raeume["technikraum"].aufgaben.append(neue_aufgabe)
            print(f"\n{person.name} gibt dir die Aufgabe: {neue_aufgabe}")

    def spiel_starten(self):
        print("\nWillkommen zum Team-Adventure!")
        while True:
            self.raum_betreten()
