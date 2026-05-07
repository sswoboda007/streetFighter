"""Tournament scheduling and matchmaking for Street Fighter.

Provides a simple single-elimination bracket generator plus a
round-robin scheduler. Matches are simulated using the Character
model's attack loop; the faster (higher agility) fighter strikes first.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import List, Optional

from models.character import Character


@dataclass
class MatchResult:
    fighter_a: str
    fighter_b: str
    winner: str
    log: List[str] = field(default_factory=list)


def simulate_match(a: Character, b: Character, max_rounds: int = 50) -> MatchResult:
    """Simulate a 1v1 match. Does not mutate the input characters."""
    ca = Character(a.name, a.max_health, a.strength, a.agility, a.special_skills, a.max_health)
    cb = Character(b.name, b.max_health, b.strength, b.agility, b.special_skills, b.max_health)
    log: List[str] = [f'{ca.name} (HP {ca.health}) vs {cb.name} (HP {cb.health})']

    first, second = (ca, cb) if ca.agility >= cb.agility else (cb, ca)
    for _ in range(max_rounds):
        log.append(first.attack(second))
        if second.is_ko():
            break
        log.append(second.attack(first))
        if first.is_ko():
            break

    if ca.is_ko() and not cb.is_ko():
        winner = cb.name
    elif cb.is_ko() and not ca.is_ko():
        winner = ca.name
    else:
        winner = ca.name if ca.health >= cb.health else cb.name
    log.append(f'Winner: {winner}')
    return MatchResult(fighter_a=a.name, fighter_b=b.name, winner=winner, log=log)


@dataclass
class Tournament:
    name: str
    fighters: List[Character]
    format: str = 'single_elimination'  # or 'round_robin'
    bracket: List[List[MatchResult]] = field(default_factory=list)
    standings: List[str] = field(default_factory=list)
    champion: Optional[str] = None

    def run(self) -> None:
        self.bracket = []
        if self.format == 'round_robin':
            self._run_round_robin()
        else:
            self._run_single_elim()

    def _run_single_elim(self) -> None:
        if not self.fighters:
            return
        current = list(self.fighters)
        while len(current) > 1:
            round_results: List[MatchResult] = []
            winners: List[Character] = []
            pairs = list(zip(current[0::2], current[1::2]))
            bye = current[-1] if len(current) % 2 == 1 else None
            for a, b in pairs:
                r = simulate_match(a, b)
                round_results.append(r)
                winners.append(a if r.winner == a.name else b)
            if bye is not None:
                winners.append(bye)
            self.bracket.append(round_results)
            current = winners
        self.champion = current[0].name if current else None

    def _run_round_robin(self) -> None:
        wins = {c.name: 0 for c in self.fighters}
        round_results: List[MatchResult] = []
        for a, b in itertools.combinations(self.fighters, 2):
            r = simulate_match(a, b)
            round_results.append(r)
            wins[r.winner] += 1
        self.bracket.append(round_results)
        self.standings = sorted(wins, key=lambda n: wins[n], reverse=True)
        self.champion = self.standings[0] if self.standings else None

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'format': self.format,
            'fighters': [c.name for c in self.fighters],
            'champion': self.champion,
            'standings': self.standings,
            'bracket': [
                [
                    {
                        'fighter_a': m.fighter_a,
                        'fighter_b': m.fighter_b,
                        'winner': m.winner,
                        'log': m.log,
                    }
                    for m in rnd
                ]
                for rnd in self.bracket
            ],
        }