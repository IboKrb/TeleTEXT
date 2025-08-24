class Person:
    def __init__(self, name, rolle, beschreibung, rede_lust=5):
        self.name = name
        self.rolle = rolle
        self.beschreibung = beschreibung
        self.dialog_history = []
        self.relationship = 0  
        self.rede_lust = rede_lust  

    def sprich(self):
        print(f"{self.name} ({self.rolle}): {self.beschreibung}")
        print(f"{self.name}: Hallo! Möchtest du etwas für mich erledigen?")
        antwort = input("Deine Antwort (ja/nein/Smalltalk): ").strip().lower()
        if antwort == "ja":
            print(f"{self.name}: Super! Ich habe eine Aufgabe für dich.")
            return "task"  
        elif antwort == "smalltalk" and self.rede_lust > 3:
            print(f"{self.name}: Oh, ich rede so gerne... Übrigens, wusstest du schon, dass ...")
        elif antwort == "nein":
            print(f"{self.name}: Schade, vielleicht später!")
        else:
            print(f"{self.name}: Okay.")
        self.dialog_history.append(antwort)

    def beziehung_steigern(self, punkte=1):
        self.relationship += punkte
        print(f"Der Beziehungswert zu {self.name} ist jetzt {self.relationship}.")
