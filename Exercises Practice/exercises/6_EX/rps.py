"""Some facilities to implement playing strategies for Rock-Paper-Scissors.
"""

import random
from typing import List, Counter
from typing import Any, Optional, Sequence, Iterable
from typing import NewType

__all__ = [
    'Option', 'ROCK', 'PAPER', 'SCISSORS', 'OPTIONS',
    'Outcome', 'TIE', 'WIN', 'LOSS',
    'judge_encounter',
    'Distribution', 'choose_random',
    'Player', 'OutcomeStats', 'Referee',
]

#: Type for choice options
#: Constraint: only 0, 1, 2 used
Option = NewType('Option', int)

#: Constants of Option
ROCK, PAPER, SCISSORS = Option(0), Option(1), Option(2)
OPTIONS: List[Option] = [ROCK, PAPER, SCISSORS]
    
#: Type for outcomes of an RPS encounter
#: 0 (tie), 1 (Player 1), or 2 (Player 2)
Outcome = NewType('Outcome', int)

#: Constants of Outcome
TIE = Outcome(0)
WIN = Outcome(1)
LOSS = Outcome(2)


def judge_encounter(choice_1: Option, choice_2: Option) -> Outcome:
    """Judge an RPS encounter, returning who wins: Player 1 or 2 (TIE for tie).
        
    >>> judge_encounter(ROCK, ROCK)
    0
    >>> judge_encounter(PAPER, SCISSORS)
    2
    >>> judge_encounter(ROCK, SCISSORS)
    1
    """
    return Outcome((choice_1 - choice_2) % len(OPTIONS))


#: Type for probability distribution on OPTIONS
#: Assumptions for distr: Distribution
#:
#:   * all(0 <= p <= 1 for p in distr)
#:   * sum(distr) == 1
#:   * len(distr) == len(OPTIONS)
Distribution = Sequence[float]


def choose_random(distr: Distribution) -> Option:
    """Make random choice according to given distribution.
    
    >>> choose_random([1, 0, 0])
    0
    >>> choose_random([0, 1, 0])
    1
    >>> choose_random([0, 0, 1])
    2
    >>> all(choose_random([1/3, 1/3, 1/3]) in OPTIONS for _ in range(100))
    True
    """
    return Option(random.choices(OPTIONS, weights=distr, k=1)[0])


class Player:
    """An abstract player for Rock-Paper-Scissors.
    
    Usage:
    
    1. Create an instance, player, of a subclass of Player.
    2. Repeatedly call
       2.a. player.choose()
       2.b. player.inform(prev_opp)
       
    >>> player = Player('Test')
    >>> player
    Player('Test')
    >>> print(player)
    Test
    >>> player.choose()
    Traceback (most recent call last):
        ...
    NotImplementedError: method is abstract
    >>> player.inform(PAPER)
    """
    
    def __init__(self, name: str) -> None:
        """Initialize player with given name.
        """
        self.name = name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"
    
    def __str__(self) -> str:
        return self.name
    
    def choose(self) -> Option:
        """Choose from OPTIONS for this turn.
        """
        raise NotImplementedError("method is abstract")
        
    def inform(self, opponent_previous: Option) -> None:
        """Inform player of opponent's previous choice.
        """
        pass  # default behavior: ignore


class OutcomeStats:
    """A count per Outcome (mutable).
    
    >>> stats = OutcomeStats()
    >>> stats
    OutcomeStats(Counter())
    >>> print(stats)
    0 wins - 0 ties - 0 losses
    >>> stats.win_fraction()
    Traceback (most recent call last):
        ...
    AssertionError: No wins and losses
    >>> stats.update([WIN])
    >>> stats.win_fraction()
    1.0
    >>> stats.update([LOSS, TIE, LOSS, TIE, LOSS])
    >>> stats.win_fraction()
    0.25
    >>> print(stats)
    1 wins - 2 ties - 3 losses
    """
    
    def __init__(self, counts: Counter[Outcome] = None) -> None:
        self.counts: Counter[Outcome]  # (needed for type checking)
        if counts is None:
            self.counts = Counter()
        else:
            self.counts = counts
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.counts!r})"
    
    def __str__(self) -> str:
        return ' - '.join([f"{self.counts[WIN]} wins",
                           f"{self.counts[TIE]} ties",
                           f"{self.counts[LOSS]} losses",
                          ])
    
    def update(self, iterable: Iterable[Outcome]) -> None:
        """Update with all given outcomes.
        """
        self.counts.update(iterable)

    def win_fraction(self) -> float:
        """Return fraction win / (win + loss).
        """
        win_loss = self.counts[WIN] + self.counts[LOSS]
        assert  win_loss != 0, 'No wins and losses'
        return self.counts[WIN] / win_loss


class Referee:
    """A referee for RPS games between two given players (immutable).
    """
    
    def __init__(self, player_1: Player, player_2: Player) -> None:
        """Initialize referee with two given players.
        """
        self.player_1 = player_1
        self.player_2 = player_2
        
    def play_encounter(self) -> Outcome:
        """Play one encounter between the two players,
        returning outcome.
        """
        choice_1 = self.player_1.choose()
        choice_2 = self.player_2.choose()
        
        self.player_1.inform(choice_2)
        self.player_2.inform(choice_1)

        return judge_encounter(choice_1, choice_2)
    
    def play_games(self, n: int, verbose=False) -> OutcomeStats:
        """Play n encounters between the two players,
        returning outcome statistics.
        """
        stats = OutcomeStats()
        stats.update(self.play_encounter() for _ in range(n))
        if verbose:
            print(f"{self.player_1} vs {self.player_2}")
            print(stats)
            print(f"win fraction: {stats.win_fraction():1.2f}")
            
        return stats