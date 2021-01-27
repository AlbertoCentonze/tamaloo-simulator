from __future__ import annotations
import random
from math import floor


class Game:
    def __init__(self, players: int = 2, output: bool = False):
        self.__output = output
        self.__deck = []
        self.__players = []
        self.__thrown_card = None
        self.__runned_cycles = 0
        self.refill_deck()
        random.shuffle(self.__deck)
        for p in range(players):
            self.__players.append(Hand(self, p, dumb_player))

    def get_output(self) -> bool:
        return self.__output

    def get_deck(self) -> list[Card]:
        return self.__deck

    def get_player(self, index: int) -> Hand:
        return self.__players[index]

    def get_players_number(self) -> int:
        return len(self.__players)

    def get_runned_cycles(self) -> int:
        return self.__runned_cycles

    def print_game_info(self) -> None:
        if self.__output:
            return
        try:
            print("Next card " + str(self.__deck[-1]))
        except:
            print("Error")
        if self.__thrown_card is not None:
            print("Last card thrown " + str(self.__thrown_card))
        print(self.__players)

    def simulate_cycle(self) -> bool:
        tamaloo = False
        for index, hand in enumerate(self.__players):
            if self.__output:
                print("It's the turn of player " + str(index + 1))
                self.print_game_info()
            # input()
            hand.draw_and_replace()
            self.throw_same_card()
            tamaloo = tamaloo or hand.get_ai().call_tamaloo()
            if (len(self.__deck) == 1):
                self.refill_deck()
                # input()
        self.__runned_cycles += 1
        return tamaloo

    def simulate_game(self) -> None:
        while not self.simulate_cycle():
            pass
        self.simulate_cycle()
        self.find_winner()

    def refill_deck(self) -> None:
        for x in range(4):
            for i in list(range(1, 14)):
                self.__deck.append(Card(i))
        if self.__output:
            print("deck refilled")

    def throw_same_card(self):
        for player in self.__players:
            for card in player.get_cards():
                if random.choice([True, False]) and card == self.__thrown_card and card.get_known():
                    player.get_cards().remove(card)
                    if self.__output:
                        print("Player " + str(player.get_player_index() + 1) +
                              " remembered correctly a card")
                        print(self.__players)
                    # input()

    def find_winner(self) -> list(int):
        min_value = 1000000
        winner_indexes = []
        all_scores = []
        for index, player in enumerate(self.__players):
            cards_sum = 0
            for card in player.get_cards():
                cards_sum += card.get_value()
            all_scores.append(cards_sum)
            if cards_sum < min_value:
                winner_indexes = []
                min_value = cards_sum
                winner_indexes.append(index)
            elif cards_sum == min_value:
                winner_indexes.append(index)
        if not self.__output:
            return winner_indexes
        if len(winner_indexes) == 1:
            print("The winner is player " + str(winner_indexes[0]))
        elif len(winner_indexes) > 1:
            winners = ""
            for index in winner_indexes:
                winners += (str(index) + " ")
            print("The winner are players " + winners)
        print(all_scores)

        return winner_indexes

    def set_thrown_card(self, card: Card) -> None:
        self.__thrown_card = card
        card.side_effect()
        card.set_known(None)

    def get_thrown_card(self) -> Card:
        return self.__thrown_card


class Hand:
    def __init__(self, game: Game, index: int, ai: AI):
        self.__cards = []
        self.__game = game
        self.__player_index = index
        self.__ai = ai(self)
        self.draw(4)
        for x in range(2):
            self.__cards[x].set_known(True)

    def draw(self, amount: int = 1) -> None:
        for i in range(amount):
            card = self.get_game().get_deck().pop()
            card.set_owner(self)
            self.__cards.append(card)

    def draw_and_replace(self) -> None:
        try:
            new_card = self.get_game().get_deck().pop()
        except:
            self.get_game().refill_deck()
            return self.draw_and_replace()
        new_card.set_owner(self)
        replacement_scores = []
        for old_card in self.__cards:
            replacement_scores.append(self.get_ai().replace_card(new_card))
        replacement_scores.append(self.get_ai().keep_cards(new_card))
        max_value = -1
        max_value_indexes = []
        for index, value in enumerate(replacement_scores):
            if value > max_value:
                max_value_indexes = []
                max_value = value
                max_value_indexes.append(index)
            elif value == max_value:
                max_value_indexes.append(index)
        choice = random.choice(max_value_indexes)
        if choice == len(self.__cards):  # don't replace
            self.get_game().set_thrown_card(new_card)
        elif choice < len(self.__cards):  # replce cards
            old_card = self.get_card(choice)
            self.__add_card(new_card)
            self.get_game().set_thrown_card(old_card)
            self.__cards.remove(old_card)

    def get_game(self) -> Game:
        return self.__game

    def get_player_index(self) -> int:
        return self.__player_index

    def get_ai(self) -> AI:
        return self.__ai

    def get_card(self, index: int = -1) -> Card:
        if index == -1:
            return random.choice(self.__cards)
        return self.__cards[index]

    def get_cards(self) -> list[Card]:
        return self.__cards

    def __add_card(self, card: Card) -> None:
        card.set_owner(self)
        card.set_known(True)
        self.__cards.append(card)

    def __repr__(self) -> str:
        return self.__cards.__repr__()

    def to_string(self) -> str:
        return "p" + str(self.__player_index + 1)

    def switch_cards_between_players(c1: Card, c2: Card) -> None:
        print("bella")
        hand1 = c1.get_owner().get_cards()
        hand2 = c2.get_owner().get_cards()
        hand1.append(c2)
        hand2.append(c1)
        c1.set_known(False)
        c2.set_known(False)
        tmp_owner = c1.get_owner()
        c1.set_owner(c2.get_owner())
        c2.set_owner(tmp_owner)
        hand1.remove(c1)
        hand2.remove(c2)


class Card:
    def __init__(self, value: int):
        self.__value = value
        self.__known = False
        self.__owner = None

    def __repr__(self) -> str:
        seen = ""
        if self.__known is not None:
            seen = "k" if self.__known else "u"
        if self.__owner is not None:
            return str(self.__value) + seen + "-p" + str(self.get_owner().get_player_index() + 1)
        return str(self.__value) + seen

    def __eq__(self, other: Card) -> bool:
        if isinstance(other, Card):
            return self.__value == other.__value
        return False

    def set_known(self, value: bool) -> None:
        self.__known = value

    def get_known(self) -> bool:
        return self.__known

    def set_owner(self, player: Hand) -> None:
        self.__owner = player

    def get_owner(self) -> Hand:
        return self.__owner

    def get_value(self) -> int:
        return self.__value

    def side_effect(self) -> None:
        if (self.__value == 13):
            self.__king()
        elif (self.__value == 12):
            self.__queen()
        elif (self.__value == 11):
            self.__joker()

    def __king(self) -> None:
        player_index = self.get_owner().get_ai().pick_king_target()
        self.get_owner().get_game().get_player(player_index).draw()

    def __queen(self) -> None:
        cards = self.get_owner().get_ai().pick_queen_targets()
        if len(cards) == 0:
            return
        Hand.switch_cards_between_players(cards[0], cards[1])

    def __joker(self) -> None:
        card = self.get_owner().get_ai().pick_joker_target()
        if card is not None:
            card.set_known(True)


class AI:
    score = int

    def __init__(self, player: Hand):
        self.__hand = player

    def get_player_hand(self) -> Hand:
        return self.__hand

    def get_output(self) -> bool:
        return self.__hand.get_game().get_output()

    def replace_card(self, new_card: Card) -> score:
        raise Exception("empty replace card ai")

    def keep_cards(self, new_card: Card) -> score:
        raise Exception("emtpy keep card ai")

    def pick_king_target(self) -> int:
        raise Exception("emtpy king ai")

    def pick_queen_targets(self) -> list[Card]:
        raise Exception("emtpy queen ai")

    def pick_joker_target(self) -> Card:
        raise Exception("emtpy joker ai")

    def call_tamaloo(self) -> bool:
        if len(self.get_player_hand().get_cards()) == 0:
            if self.get_output():
                print("Tamaloo was called because an hand was emtpy")
            return True


class dumb_player(AI):
    def __init__(self, player: Hand):
        super().__init__(player)

    def replace_card(self, new_card: Card) -> AI.score:
        return random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def keep_cards(self, new_card: Card) -> AI.score:
        return random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def call_tamaloo(self) -> bool:
        super().call_tamaloo()
        if self.get_player_hand().get_game().get_runned_cycles() > 5:
            tamaloo = random.choice([True, False, False])
            if tamaloo and super().get_output():
                print("Tamaloo was called by a dumb player")
            return tamaloo

    def pick_king_target(self) -> int:
        available_indexes = list(
            range(self.get_player_hand().get_game().get_players_number()))
        available_indexes.remove(self.get_player_hand().get_player_index())
        return random.choice(available_indexes)

    def pick_queen_targets(self) -> list[Card]:
        try:
            available_indexes = list(
                range(self.get_player_hand().get_game().get_players_number()))
            i1 = random.choice(available_indexes)
            i2 = i1
            while i2 == i1:
                i2 = random.choice(available_indexes)
            players = []
            players.append(self.get_player_hand().get_game().get_player(i1))
            players.append(self.get_player_hand().get_game().get_player(i2))
            picked_cards = []
            for p in players:
                cards_indexes = list(range(len(p.get_card())))
                picked_cards.append(random.choice(cards_indexes))
            return picked_cards
        except:
            return []

    def pick_joker_target(self) -> Card:
        if len(self.get_player_hand().get_cards()):
            return self.get_player_hand().get_card()
        return None


if __name__ == "__main__":
    i = 2
    n = 0
    while n < 500:
        while i < floor(52/4):
            print(n)
            game = Game(i)
            game.simulate_game()
            i += 1
        i = 2
        n += 1
