from __future__ import annotations
import random


class Game:
    def __init__(self, players: int = 2):
        self.__deck = []
        self.__players = []
        self.__players_number = players
        self.__thrown_card = None
        for x in range(4):
            for i in list(range(1, 14)):
                self.__deck.append(Card(i))
        random.shuffle(self.__deck)
        for p in range(players):
            self.__players.append(Hand(self, p, AI))

    def get_deck(self) -> list[Card]:
        return self.__deck

    def get_player(self, index: int) -> Hand:
        return self.__players[index]

    def get_players_number(self) -> int:
        return len(self.__players)

    def print_game_info(self) -> None:
        print(self.__deck)
        print(self.__players)

    def simulate_cycle(self) -> bool:
        tamaloo = False
        for hand in self.__players:
            hand.draw_and_replace()
            tamaloo = tamaloo or hand.get_ai().call_tamaloo()
        return tamaloo
    
    def simulate_game(self) -> None:
        while not self.simulate_cycle():
            pass
        self.simulate_cycle()
        self.find_winner()

    def find_winner(self) -> list(int):
        min_value = 1000000
        winner_indexes = []
        for index, player in enumerate(self.__players):
            cards_sum = sum(player.__cards)
            if cards_sum < min_value:
                winner_indexes = []
                min_value = cards_sum
                winner_indexes.append(index)
            elif cards_sum == min_value:
                winner_indexes.append(index)

        if len(winner_indexes) == 1:
            print("The winner is player " + str(winner_indexes[0]))
        elif len(winner_indexes) > 1:
            winners = ""
            for index in winner_indexes:
                winners += (str(index) + " ")  
            print("The winner is player " + winners)



        return winner_indexes



    def set_thrown_card(self, card: Card) -> None:
        self.__thrown_card = card
        card.side_effect()

    def get_thrown_card(self) -> Card:
        return self.__thrown_card


class Hand:
    def __init__(self, game: Game, index: int, ai: AI):
        self.__cards = []
        self.__game = game
        self.__player_index = index
        self.__ai = ai(game, self)
        self.draw(4)
        for x in range(2):
            self.__cards[x].set_known(True)

    def draw(self, amount: int = 1) -> None:
        for i in range(amount):
            card = self.get_game().get_deck().pop()
            card.set_owner(self.__player_index)
            self.__cards.append(card)

    def draw_and_replace(self) -> None:
        new_card = self.get_game().get_deck().pop()
        replacement_scores = []
        for old_card in self.__cards:
            replacement_scores.append(self.get_ai().replace_card(new_card))
        replacement_scores.append(self.get_ai().keep_card(new_card))
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
        if choice == len(self.__cards):
            self.get_game().set_thrown_card(new_card)
        elif choice < len(self.__cards):
            old_card = self.get_card(choice)
            self.__cards.append(new_card)
            self.get_game().set_thrown_card(old_card)
            self.__cards.remove(old_card)
            

    def get_game(self) -> Game:
        return self.__game

    def get_player_index(self) -> int:
        return self.__player_index

    def get_ai(self) -> AI:
        return self.__ai

    def get_card(self, index: int) -> Card:
        return self.__cards[index]

    def __repr__(self) -> str:
        return self.__cards.__repr__()

    def switch_cards_between_players(c1: Card, c2: Card) -> None:
        hand1 = c1.get_owner().__cards
        hand2 = c2.get_owner().__cards
        hand1.append(c2)
        hand2.append(c1)
        c1.set_known(False)
        c2.set_known(False)
        hand1.remove(c1)
        hand2.remove(c2)

class Card:
    def __init__(self, value: int, player=None):
        self.__value = value
        self.__known = False
        self.__owner = player

    def __repr__(self) -> str:
        seen = "k" if self.__known else "u"
        return str(self.__value) + seen

    def set_known(self, value: bool) -> None:
        self.__known = value

    def set_owner(self, player: Hand) -> None:
        self.__owner = player

    def get_owner(self) -> Hand:
        return self.__owner

    def side_effect(self) -> None:
        if (self.__value == 13):
            self.__king()
        elif (self.__value == 12):
            self.__queen()
        elif (self.__value == 11):
            self.__joker()

    def __king(self,) -> None:
        player_index = self.get_owner().get_ai().pick_king_target()
        self.get_owner().get_other_players()[player_index].draw()

    def __queen(self) -> None:
        c1, c2 = self.get_owner().get_ai().pick_queen_targets()
        Hand.switch_cards_between_players(c1, c2)

    def __joker(self) -> None:
        card = self.get_owner().get_ai().pick_joker_target()
        card.set_known(True)


class AI:
    def __init__(self, game: Game, player: Hand):
        raise Exception(
            "Can't instantiate this class without overriding its methods")

    score = int

    def replace_card(self, new_card: Card) -> score:
        pass

    def keep_card(self, new_card: Card) -> score:
        pass

    def pick_king_target(self) -> int:
        pass

    def pick_queen_targets(self) -> list[Card]:
        pass

    def pick_joker_target(self) -> Card:
        pass

    def call_tamaloo(self) -> bool:
        pass


if __name__ == "__main__":
    game = Game(2)
    game.print_game_info()
    game.simulate_game()
