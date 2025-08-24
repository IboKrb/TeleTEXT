class Aufgabe:
    def __init__(self, id, name, beschreibung):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.beschreibung}"
