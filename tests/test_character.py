"""Tests for models/character.py — targets 100% branch coverage."""
import pytest
from models.character import Character


class TestCharacterInit:
    def test_default_max_health(self):
        c = Character('Ryu', 100, 12, 8, ['Hadoken'])
        assert c.max_health == 100

    def test_explicit_max_health(self):
        c = Character('Ryu', 80, 12, 8, ['Hadoken'], max_health=100)
        assert c.max_health == 100

    def test_empty_special_skills(self):
        c = Character('Ryu', 100, 12, 8, [])
        assert c.special_skills == []

    def test_none_special_skills(self):
        c = Character('Ryu', 100, 12, 8, None)
        assert c.special_skills == []

    def test_skills_are_copied(self):
        skills = ['Hadoken']
        c = Character('Ryu', 100, 12, 8, skills)
        skills.append('Shoryuken')
        assert c.special_skills == ['Hadoken']


class TestAttack:
    def test_attack_reduces_health(self):
        attacker = Character('Ryu', 100, 12, 8, [])
        target = Character('Ken', 100, 13, 9, [])
        msg = attacker.attack(target)
        assert target.health == 88
        assert 'Ryu attacks Ken for 12 damage!' == msg


class TestUseSpecialSkill:
    def test_known_skill(self):
        c = Character('Ryu', 100, 12, 8, ['Hadoken'])
        target = Character('Ken', 100, 13, 9, [])
        msg = c.use_special_skill('Hadoken', target)
        assert msg == 'Ryu uses Hadoken on Ken!'

    def test_unknown_skill(self):
        c = Character('Ryu', 100, 12, 8, ['Hadoken'])
        target = Character('Ken', 100, 13, 9, [])
        msg = c.use_special_skill('Shoryuken', target)
        assert msg == 'Ryu does not have the skill Shoryuken.'


class TestReset:
    def test_reset_restores_health(self):
        c = Character('Ryu', 100, 12, 8, [], max_health=100)
        c.health = 50
        c.reset()
        assert c.health == 100


class TestIsKo:
    def test_not_ko(self):
        c = Character('Ryu', 100, 12, 8, [])
        assert not c.is_ko()

    def test_ko_at_zero(self):
        c = Character('Ryu', 0, 12, 8, [])
        assert c.is_ko()

    def test_ko_below_zero(self):
        c = Character('Ryu', -5, 12, 8, [])
        assert c.is_ko()


class TestToDict:
    def test_keys_present(self):
        c = Character('Ryu', 100, 12, 8, ['Hadoken'])
        d = c.to_dict()
        assert set(d) == {'name', 'health', 'max_health', 'strength', 'agility', 'special_skills', 'palette'}

    def test_special_skills_copied(self):
        c = Character('Ryu', 100, 12, 8, ['Hadoken'])
        d = c.to_dict()
        d['special_skills'].append('x')
        assert c.special_skills == ['Hadoken']


class TestPalette:
    @pytest.mark.parametrize('name', ['Ryu', 'Ken', 'Chun-Li', 'Zangief'])
    def test_known_characters(self, name):
        c = Character(name, 100, 10, 10, [])
        p = c.palette()
        assert 'skin' in p and 'gi' in p

    def test_unknown_character_default_palette(self):
        c = Character('Unknown', 100, 10, 10, [])
        p = c.palette()
        assert p['gi'] == 0x888888


class TestToGameStats:
    def test_structure(self):
        c = Character('Ryu', 100, 12, 8, [])
        gs = c.to_game_stats()
        assert set(gs) == {'max_hp', 'damage_light', 'damage_heavy', 'move_speed', 'attack_cooldown_ms'}

    def test_values(self):
        c = Character('Ryu', 100, 12, 8, [])
        gs = c.to_game_stats()
        assert gs['max_hp'] == 100
        assert gs['damage_light'] == 12
        assert gs['damage_heavy'] == 24
        assert gs['move_speed'] == 200
        assert gs['attack_cooldown_ms'] == 440

    def test_attack_cooldown_floor(self):
        c = Character('Fast', 100, 10, 30, [])
        gs = c.to_game_stats()
        assert gs['attack_cooldown_ms'] == 200


class TestStr:
    def test_str(self):
        c = Character('Ryu', 100, 12, 8, [])
        assert str(c) == 'Character(Ryu, Health: 100, Strength: 12, Agility: 8)'
