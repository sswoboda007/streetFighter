class Character:
    def __init__(self, name, health, strength, agility, special_skills, max_health=None):
        self.name = name
        self.health = health
        self.max_health = max_health if max_health is not None else health
        self.strength = strength
        self.agility = agility
        self.special_skills = list(special_skills) if special_skills else []

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

    def reset(self):
        self.health = self.max_health

    def is_ko(self):
        return self.health <= 0

    def to_dict(self):
        return {
            'name': self.name,
            'health': self.health,
            'max_health': self.max_health,
            'strength': self.strength,
            'agility': self.agility,
            'special_skills': list(self.special_skills),
            'palette': self.palette(),
        }

    def palette(self):
        presets = {
            'Ryu':     {'skin': 0xf2c28b, 'gi': 0xf0f0f0, 'belt': 0x222222, 'hair': 0x3a2a1a, 'accent': 0xd13b3b},
            'Ken':     {'skin': 0xf2c28b, 'gi': 0xd13b3b, 'belt': 0x222222, 'hair': 0xf0c674, 'accent': 0x222222},
            'Chun-Li': {'skin': 0xf2c28b, 'gi': 0x2a6fd6, 'belt': 0xf0c674, 'hair': 0x1a1a1a, 'accent': 0xf0c674},
            'Zangief': {'skin': 0xe0a070, 'gi': 0x8b1a1a, 'belt': 0x222222, 'hair': 0x3a2a1a, 'accent': 0xf0c674},
        }
        return presets.get(self.name, {
            'skin': 0xf2c28b, 'gi': 0x888888, 'belt': 0x222222, 'hair': 0x222222, 'accent': 0xf0c674,
        })

    def to_game_stats(self):
        return {
            'max_hp': self.max_health,
            'damage_light': self.strength,
            'damage_heavy': self.strength * 2,
            'move_speed': 120 + self.agility * 10,
            'attack_cooldown_ms': max(200, 600 - self.agility * 20),
        }

    def __str__(self):
        return f'Character({self.name}, Health: {self.health}, Strength: {self.strength}, Agility: {self.agility})'