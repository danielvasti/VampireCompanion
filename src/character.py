# src/character.py

class Character:
    def __init__(self, name):
        self.name = name
        self.clan = None
        self.disciplines = {}
        self.bane = None
        
        self.attributes = {}
        self.skills = {}
        self.specialties = {} # NOVO: Dicionário para guardar as especialidades

    def set_clan(self, clan_name, clan_data):
        if clan_name in clan_data:
            self.clan = clan_name
            self.disciplines = clan_data[clan_name]["disciplines"]
            self.bane = clan_data[clan_name]["bane"]
        else:
            print(f"Erro: Clã '{clan_name}' não encontrado.")

    def initialize_stats(self, attributes_data, skills_data):
        # (Esta função permanece idêntica)
        for category in attributes_data.values():
            for attr in category:
                self.attributes[attr] = 1
        for category in skills_data.values():
            for skill in category:
                self.skills[skill] = 0
        self.specialties.clear() # Limpa especialidades ao reiniciar

    def add_specialty(self, skill, specialty_text):
        """NOVO: Adiciona uma especialidade a uma perícia."""
        if skill not in self.specialties:
            self.specialties[skill] = []
        self.specialties[skill].append(specialty_text)