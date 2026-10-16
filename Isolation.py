"""
Isolation - gra przeciwko sztucznej inteligencji.

Zasady:
https://en.wikipedia.org/wiki/Isolation_(board_game)
Autorzy: [Maciej Kupcewicz-Szwoch s29467, Szymon Witowski s29099]

"""

from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax


class Isolation(TwoPlayerGame):
    """Gra Isolation na planszy 5x5."""

    def __init__(self, players):
        self.players = players
        self.current_player = 1

        self.size = 5
        self.positions = [(0, 0), (4, 4)]
        self.blocked = set()
        self.moves_played = 0

    def moves_for(self, player):
        """Zwraca dostepne ruchy wybranego gracza."""
        x, y = self.positions[player - 1]
        moves = []

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:

                if dx == 0 and dy == 0:
                    continue

                nx = x + dx
                ny = y + dy

                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if (nx, ny) not in self.blocked:
                        if (nx, ny) not in self.positions:
                            moves.append(f"{nx},{ny}")

        return moves

    def possible_moves(self):
        """Zwraca ruchy aktualnego gracza."""
        return self.moves_for(self.current_player)

    def make_move(self, move):
        """Przesuwa gracza i blokuje poprzednie pole."""
        player = self.current_player - 1

        x, y = map(int, move.split(","))

        self.blocked.add(self.positions[player])
        self.positions[player] = (x, y)
        self.moves_played += 1

    def is_over(self):
        """Gra konczy sie, gdy gracz nie ma ruchow."""
        return len(self.possible_moves()) == 0

    def scoring(self):
        """Ocena pozycji dla algorytmu Negamax."""
        if self.is_over():
            return -100

        return len(self.possible_moves())

    def show(self):
        """Wyswietla plansze i dostepne ruchy."""
        print("\n   0 1 2 3 4")

        for x in range(self.size):
            print(x, " ", end="")

            for y in range(self.size):
                pos = (x, y)

                if pos == self.positions[0]:
                    symbol = "1"
                elif pos == self.positions[1]:
                    symbol = "2"
                elif pos in self.blocked:
                    symbol = "X"
                else:
                    symbol = "."

                print(symbol, end=" ")

            print()

        # easyAI wyswietla plansze przed zmiana gracza
        if self.moves_played == 0:
            next_player = 1
        else:
            next_player = 3 - self.current_player

        print("\nNastepny gracz:", next_player)
        print("Dostepne ruchy:", self.moves_for(next_player))


# Uruchomienie gry
if __name__ == "__main__":
    ai = Negamax(4)

    game = Isolation([
        Human_Player(),
        AI_Player(ai)
    ])

    game.play()

    print("\nKoniec gry!")
    print("Wygrywa gracz", 3 - game.current_player)
