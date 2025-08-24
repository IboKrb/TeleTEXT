class Raum:
    def __init__(self, name, beschreibung, aufgaben=None, personen=None, gegenstaende=None, verbindungen=None):
        self.name = name
        self.beschreibung = beschreibung
        self.aufgaben = aufgaben if aufgaben is not None else []
        self.personen = personen if personen is not None else []
        self.gegenstaende = gegenstaende if gegenstaende is not None else []
        self.verbindungen = verbindungen if verbindungen is not None else []
