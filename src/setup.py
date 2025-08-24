from person import Person
from raum import Raum

class Setup:
    """
    Verantwortlich für das reine Anlegen von Personen und Räumen.
    Keine Game-Loop- oder IO-Methoden.
    """

    def personen_erzeugen(self):
        holger = Person("Holger", "Teamleiter", "Sehr nett und immer hilfsbereit.", rede_lust=4)
        flo = Person("Flo", "Stellvertretender Teamleiter", "Gesprächsfreudig – kann nicht aufhören zu reden!", rede_lust=7)
        kirsten = Person("Kirsten", "Projektmanager", "Nervig und anstrengend.", rede_lust=3)
        return {
            "holger": holger,
            "flo": flo,
            "kirsten": kirsten
        }

    def raum_erzeugen(self, personen):
        flur = Raum("Flur", "Du siehst einen langen Gang mit ganz vielen Räumen.")
        buero1 = Raum("Büro 1", "Ein schickes Büro mit PC und Kaffee.", personen=[personen["holger"]])
        grossraumbuero = Raum("Großraumbüro", "Viele Tische und Arbeitsplätze.", personen=[personen["flo"], personen["kirsten"]])
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