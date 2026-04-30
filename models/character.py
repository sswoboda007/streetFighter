class Character:
    def __init__(self, name, health, strength, agility, special_skills):
        self.name = name
        self.health = health
        self.strength = strength
        self.agility = agility
        self.special_skills = special_skills

    def attack(self, target):
        damage = self.strength  # Example damage calculation
        target.health -= damage
        return f'{self.name} attacks {target.name} for {damage} damage!'

    def use_special_skill(self, skill, target):
        if skill in self.special_skills:
            # Implement special skill logic here
            return f'{self.name} uses {skill} on {target.name}!'
        else:
            return f'{self.name} does not have the skill {skill}.'

    def __str__(self):
        return f'Character({self.name}, Health: {self.health}, Strength: {self.strength}, Agility: {self.agility})'