from __future__ import annotations

from flask import Flask, jsonify, render_template, request, abort

from models.character import Character

app = Flask(__name__)

_characters: dict[str, Character] = {}


def _seed() -> None:
    if _characters:
        return
    for c in [
        Character('Ryu', 100, 12, 8, ['Hadoken']),
        Character('Chun-Li', 90, 10, 14, ['Lightning Kick']),
        Character('Ken', 100, 13, 9, ['Shoryuken']),
        Character('Zangief', 120, 15, 5, ['Spinning Piledriver']),
    ]:
        _characters[c.name] = c


_seed()


def _serialize(c: Character) -> dict:
    return {**c.to_dict(), 'game_stats': c.to_game_stats()}


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/api/characters')
def list_characters():
    return jsonify([_serialize(c) for c in _characters.values()])


@app.post('/api/characters')
def create_character():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        abort(400, 'name is required')
    if name in _characters:
        abort(409, 'character already exists')
    try:
        health = int(data.get('health', 100))
        strength = int(data.get('strength', 10))
        agility = int(data.get('agility', 10))
    except (TypeError, ValueError):
        abort(400, 'health/strength/agility must be integers')
    skills = data.get('special_skills') or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    c = Character(name, health, strength, agility, skills)
    _characters[name] = c
    return jsonify(_serialize(c)), 201


if __name__ == '__main__':
    app.run(debug=True)