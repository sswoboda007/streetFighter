"""Tests for tournaments.py — targets 100% branch coverage."""
import pytest
from models.character import Character
from tournaments import MatchResult, Tournament, simulate_match


def make_char(name, health=100, strength=10, agility=10):
    return Character(name, health, strength, agility, [f'{name}_skill'])


class TestSimulateMatch:
    def test_returns_match_result(self):
        a = make_char('A')
        b = make_char('B')
        r = simulate_match(a, b)
        assert isinstance(r, MatchResult)
        assert r.winner in (a.name, b.name)

    def test_does_not_mutate_inputs(self):
        a = make_char('A')
        b = make_char('B')
        a_hp_before = a.health
        b_hp_before = b.health
        simulate_match(a, b)
        assert a.health == a_hp_before
        assert b.health == b_hp_before

    def test_faster_fighter_goes_first(self):
        fast = make_char('Fast', agility=20)
        slow = make_char('Slow', agility=5)
        r = simulate_match(fast, slow)
        assert r.log[1].startswith('Fast')

    def test_slower_fighter_goes_second_when_equal_agility_a_first(self):
        a = make_char('A', agility=10)
        b = make_char('B', agility=10)
        r = simulate_match(a, b)
        assert r.log[1].startswith('A')

    def test_winner_is_survivor(self):
        strong = make_char('Strong', health=1000, strength=500)
        weak = make_char('Weak', health=10, strength=1)
        r = simulate_match(strong, weak)
        assert r.winner == 'Strong'

    def test_winner_log_appended(self):
        a = make_char('A')
        b = make_char('B')
        r = simulate_match(a, b)
        assert r.log[-1].startswith('Winner:')

    def test_tie_resolved_by_health(self):
        a = Character('A', 100, 10, 10, [])
        b = Character('B', 100, 10, 10, [])
        r = simulate_match(a, b, max_rounds=0)
        assert r.winner == 'A'

    def test_both_ko_resolved_by_health(self):
        a = Character('A', 1, 1000, 10, [])
        b = Character('B', 1, 1000, 10, [])
        r = simulate_match(a, b, max_rounds=1)
        assert r.winner in ('A', 'B')

    def test_only_b_ko(self):
        a = Character('A', 1000, 500, 5, [])
        b = Character('B', 1, 1, 10, [])
        r = simulate_match(a, b)
        assert r.winner == 'A'

    def test_only_a_ko(self):
        a = Character('A', 1, 1, 5, [])
        b = Character('B', 1000, 500, 10, [])
        r = simulate_match(a, b)
        assert r.winner == 'B'


class TestTournamentSingleElimination:
    def test_single_fighter_no_bracket(self):
        t = Tournament('Test', [make_char('Solo')])
        t.run()
        assert t.champion == 'Solo'
        assert t.bracket == []

    def test_empty_fighters(self):
        t = Tournament('Empty', [])
        t.run()
        assert t.champion is None

    def test_two_fighters(self):
        a = make_char('A')
        b = make_char('B')
        t = Tournament('T', [a, b])
        t.run()
        assert t.champion in ('A', 'B')
        assert len(t.bracket) == 1

    def test_four_fighters(self):
        fighters = [make_char(n) for n in ('A', 'B', 'C', 'D')]
        t = Tournament('T', fighters)
        t.run()
        assert t.champion in ('A', 'B', 'C', 'D')
        assert len(t.bracket) == 2

    def test_odd_fighters_bye(self):
        fighters = [make_char(n) for n in ('A', 'B', 'C')]
        t = Tournament('T', fighters)
        t.run()
        assert t.champion in ('A', 'B', 'C')

    def test_bracket_resets_on_rerun(self):
        fighters = [make_char(n) for n in ('A', 'B')]
        t = Tournament('T', fighters)
        t.run()
        t.run()
        assert len(t.bracket) == 1


class TestTournamentRoundRobin:
    def test_round_robin_format(self):
        fighters = [make_char(n) for n in ('A', 'B', 'C')]
        t = Tournament('RR', fighters, format='round_robin')
        t.run()
        assert t.champion in ('A', 'B', 'C')
        assert len(t.standings) == 3
        assert len(t.bracket[0]) == 3

    def test_round_robin_two_fighters(self):
        a = make_char('A')
        b = make_char('B')
        t = Tournament('RR', [a, b], format='round_robin')
        t.run()
        assert t.champion in ('A', 'B')


class TestTournamentToDict:
    def test_to_dict_keys(self):
        fighters = [make_char(n) for n in ('A', 'B')]
        t = Tournament('T', fighters)
        t.run()
        d = t.to_dict()
        assert set(d) == {'name', 'format', 'fighters', 'champion', 'standings', 'bracket'}

    def test_to_dict_bracket_structure(self):
        fighters = [make_char(n) for n in ('A', 'B')]
        t = Tournament('T', fighters)
        t.run()
        d = t.to_dict()
        match = d['bracket'][0][0]
        assert set(match) == {'fighter_a', 'fighter_b', 'winner', 'log'}
