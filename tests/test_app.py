"""Tests for app.py — targets 100% branch coverage."""
import pytest
import app as app_module
from app import app, _characters, _seed, _serialize


@pytest.fixture(autouse=True)
def reset_characters():
    """Restore the character dict to a clean seeded state before each test."""
    _characters.clear()
    _seed()
    yield
    _characters.clear()
    _seed()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


class TestSeed:
    def test_seed_populates_defaults(self):
        assert 'Ryu' in _characters
        assert 'Chun-Li' in _characters
        assert 'Ken' in _characters
        assert 'Zangief' in _characters

    def test_seed_is_idempotent(self):
        count_before = len(_characters)
        _seed()
        assert len(_characters) == count_before


class TestSerialize:
    def test_has_game_stats(self):
        c = _characters['Ryu']
        d = _serialize(c)
        assert 'game_stats' in d
        assert 'max_hp' in d['game_stats']


class TestIndex:
    def test_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200


class TestListCharacters:
    def test_returns_list(self, client):
        r = client.get('/api/characters')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        assert len(data) == 4

    def test_each_entry_has_game_stats(self, client):
        data = client.get('/api/characters').get_json()
        for entry in data:
            assert 'game_stats' in entry


class TestCreateCharacter:
    def test_create_valid(self, client):
        payload = {'name': 'Blanka', 'health': 110, 'strength': 11, 'agility': 9, 'special_skills': ['Electric Thunder']}
        r = client.post('/api/characters', json=payload)
        assert r.status_code == 201
        d = r.get_json()
        assert d['name'] == 'Blanka'

    def test_create_missing_name(self, client):
        r = client.post('/api/characters', json={})
        assert r.status_code == 400

    def test_create_blank_name(self, client):
        r = client.post('/api/characters', json={'name': '  '})
        assert r.status_code == 400

    def test_create_duplicate(self, client):
        r = client.post('/api/characters', json={'name': 'Ryu'})
        assert r.status_code == 409

    def test_create_invalid_health(self, client):
        r = client.post('/api/characters', json={'name': 'NewGuy', 'health': 'bad'})
        assert r.status_code == 400

    def test_create_no_json_body(self, client):
        r = client.post('/api/characters', content_type='application/json', data='not-json')
        assert r.status_code == 400

    def test_create_defaults_used_when_omitted(self, client):
        r = client.post('/api/characters', json={'name': 'DefaultGuy'})
        assert r.status_code == 201
        d = r.get_json()
        assert d['health'] == 100
        assert d['strength'] == 10
        assert d['agility'] == 10

    def test_create_skills_as_string(self, client):
        payload = {'name': 'Guile', 'special_skills': 'Sonic Boom, Flash Kick'}
        r = client.post('/api/characters', json=payload)
        assert r.status_code == 201
        d = r.get_json()
        assert 'Sonic Boom' in d['special_skills']
        assert 'Flash Kick' in d['special_skills']

    def test_create_skills_none(self, client):
        payload = {'name': 'Guile2', 'special_skills': None}
        r = client.post('/api/characters', json=payload)
        assert r.status_code == 201
        d = r.get_json()
        assert d['special_skills'] == []
