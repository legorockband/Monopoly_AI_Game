import random

class Player:
    def __init__(self, name: str, color=(0,0,0)):
        self.name = name
        self.color = color
        self.money = 1500
        self.position = 0
        self.properties_owned = []
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_free_cards = 0
        self.doubles_rolled_consecutive = 0 

    def move(self, spaces_to_move: int, board):
        old_position = self.position

        if old_position + spaces_to_move >= len(board.spaces):
            self.collect_money(200)
            print(f"{self.name} passed Go and Collected $200.")

        self.position = (self.position + spaces_to_move) % len(board.spaces)

        print(f"{self.name} moved to {board.spaces[self.position].name}.")
        # Trigger the land_on logic for the space the player landed on
        board.spaces[self.position].land_on(self, board)

    def collect_money(self, amount: int):
        self.money += amount
        print(f"{self.name} collected ${amount}. Current money: ${self.money}")

    def pay_money(self, amount: int):
        self.money -= amount
        print(f"{self.name} paid ${amount}. Current money: ${self.money}")
        if self.money < 0:
            print(f"!!! {self.name} is bankrupt! (Game ends for this player in a real game) !!!")

    def add_property(self, property_obj):
        """Adds a property to the player's owned list and sets the property's owner."""
        self.properties_owned.append(property_obj)
        property_obj.owner = self
        print(f"{self.name} now owns {property_obj.name}.")

    def has_monopoly(self, color_group: str, board):
        """Checks if the player owns all properties in a given color group."""
        # Get all properties of this color group from the board
        group_properties = [s for s in board.spaces if isinstance(s, Property) and s.color_group == color_group]
        
        # Check if the player owns all of them
        for prop in group_properties:
            if prop.owner != self:
                return False
        return True
    
    def count_railroads(self):
        return sum(1 for p in self.properties_owned if isinstance(p, Railroad))

    def count_utilities(self):
        return sum(1 for p in self.properties_owned if isinstance(p, Utility))

class Dice:
    def __init__(self):
        self.die1_value = 0
        self.die2_value = 0

    def roll(self):
        """Rolls two dice and returns their sum and if it was a double."""
        self.die1_value = random.randint(1, 6)
        self.die2_value = random.randint(1, 6)
        roll_sum = self.die1_value + self.die2_value
        is_double = (self.die1_value == self.die2_value)
        print(f"Rolled {self.die1_value} and {self.die2_value} (Sum: {roll_sum}). {'DOUBLES!' if is_double else ''}")
        return roll_sum, is_double

class Card:
    def __init__(self, description: str, card_type: str, action_type: str, value: any = None, target_space_index: int = None):
        self.description = description
        self.card_type = card_type
        self.action_type = action_type #move_to, collect_money, pay_money, get_out_of_jail
        self.value = value #amount of money
        self.target_space_index = target_space_index #for move_to actions

    def execute(self, player, game):
        print(f"Card Drawn ({self.card_type}): {self.description}")
        if self.action_type == "collect_money":
            player.collect_money(self.value)
        elif self.action_type == "pay_money":
            if player.money >= self.value:
                player.pay_money(self.value)
            else:
                game.start_debt(player, self.value, creditor=None, reason=f"Card: {self.description}")
        elif self.action_type == "move_to":
            
            if self.target_space_index == -3:
                player.position = (player.position - 3 + len(game.board.spaces)) % len(game.board.spaces)
                print(f"{player.name} moved back to {game.board.spaces[player.position].name}.")
                game.board.spaces[player.position].land_on(player, game.board)
                return
            
            #if passing GO
            if player.position > self.target_space_index: #passing GO unless target is GO 0 index itself
                player.collect_money(200)
                print(f"{player.name} passed GO and collected $200.")
            
            player.position = self.target_space_index
            print(f"{player.name} advanced to {game.board.spaces[player.position].name}.")
            game.board.spaces[player.position].land_on(player, game.board)

        elif self.action_type == "go_to_jail":
            player.in_jail = True
            player.position = game.board.jail_space_index
            player.jail_turns = 0
            print(f"{player.name} sent to Jail!")

        elif self.action_type == "get_out_of_jail":
            player.get_out_of_jail_free_cards += 1
            print(f"{player.name} received a Get Out of Jail Free card.")

        elif self.action_type == "it_is_your_birthday":
            # Collect $10 from each other player
            for other_player in game.players:
                if other_player != player:
                    other_player.pay_money(self.value)
                    player.collect_money(self.value)

            print(f"{player.name} collected ${self.value * (len(game.players) - 1)} from other players.")

        elif self.action_type == "street_repairs":
            house_cost = self.value.get("house", 0)
            hotel_cost = self.value.get("hotel", 0)
            total_cost = 0
            for prop in player.properties_owned:
                if isinstance(prop, Property):
                    total_cost += prop.num_houses * house_cost
                    total_cost += (1 if prop.has_hotel else 0) * hotel_cost
            if total_cost > 0:
                player.pay_money(total_cost)
                print(f"{player.name} paid ${total_cost} for street repairs.")
            else:
                print(f"{player.name} has no houses or hotels to repair, so pays $0.")
        else:
            print(f"WARNING: Unhandled card action type: {self.action_type}")

class Space:
    #Base Class for Spaces
    def __init__(self, name: str, index: int, space_type: str):
        self.name = name
        self.index = index
        self.type = space_type

    def land_on(self, player, board):
        print(f"  {player.name} landed on {self.name} ({self.type}).")

class GoSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "Go")

    def land_on(self, player, board):
        #super().land_on(player, board)
        player.collect_money(200)
        print(f"{self.name} landed on Go and Collected $200.")

class Property(Space):
    def __init__(self, name: str, index: int, cost: int, color_group: tuple[int, int, int],
                 rent_values: list, house_cost: int, mortgage_value: int):
        
        super().__init__(name, index, "Property")
        self.cost = cost
        self.owner = None
        self.color_group = color_group
        self.rent_values = rent_values
        self.house_cost = house_cost
        self.num_houses = 0
        self.has_hotel = False
        self.is_mortgaged = False
        self.mortgage_value = mortgage_value

    def calculate_rent(self, player_has_monopoly: bool):
        if self.is_mortgaged:
            return 0
        if self.has_hotel:
            return self.rent_values[5]
        if self.num_houses > 0:
            return self.rent_values[self.num_houses]
        if player_has_monopoly:
            return self.rent_values[0] * 2
        return self.rent_values[0]

    # Will be Updating this.
    def land_on(self, player, board):
        super().land_on(player, board)
        if self.owner is None:
            affordable = player.money >= self.cost
            board.game.pending_purchase ={"player": player, "property": self, "affordable": affordable}
            # if property is unowned and player can afford it -> we save info in the pending_purchase
            if affordable:
                print(f"  {player.name} may buy {self.name} for ${self.cost}.")
                    #In a full game, this would trigger an auction. Simplified for now.
            else:
                print(f"  {player.name} cannot afford {self.name} (${self.cost}).")
            return

        elif self.owner != player:
            # Property is owned by another player, pay rent
            player_owns_monopoly = self.owner.has_monopoly(self.color_group, board)
            rent_amount = self.calculate_rent(player_owns_monopoly)
            if rent_amount > 0:
                board.game.pending_rent = {
                    "player": player,
                    "owner": self.owner,
                    "property": self,
                    "amount": rent_amount
                }
                print(f"  {player.name} landed on {self.name} (owned by {self.owner.name}) and pays ${rent_amount} rent.")
            else:
                print(f"  {self.name} is mortgaged, no rent due.")
            return 

        else:
            print(f"  {player.name} landed on their own property, {self.name}.")
            return

    def group_mates(self, board):
        """All properties in my color group (including me)."""
        return [s for s in board.spaces
                if isinstance(s, Property) and s.color_group == self.color_group]
    
    def can_build_house(self, owner, board):
        if self.owner != owner: return (False, "Not owner")
        if self.is_mortgaged: return (False, "Mortgaged")
        if self.has_hotel: return (False, "Already a hotel")
        if not owner.has_monopoly(self.color_group, board):
            return(False, "Need monpoly")
        if any(p.is_mortgaged for p in self.group_mates(board)):
            return (False, "Unmortgage the whole set first")
        
        group = self.group_mates(board)
        no_hotel = [p for p in group if not p.has_hotel]
        min_houses = min((p.num_houses for p in no_hotel), default=4)
        if self.num_houses > min_houses:
            return (False, "Build evenly across the set")
        if self.num_houses >= 4:
            return (False, "Already 4 houses (buy hotel instead)")
        if owner.money < self.house_cost:
            return(False, "Not enough cash")
        return (True, "")
    
    def can_build_hotel(self, owner, board):
        if self.owner != owner: return (False, "Not owner")
        if self.is_mortgaged: return (False, "Mortgaged")
        if any(p.is_mortgaged for p in self.group_mates(board)):
            return (False, "Unmortgage the whole set first")
        if self.has_hotel: return (False, "Already a hotel")
        if not owner.has_monopoly(self.color_group, board):
            return (False, "Need monopoly")
        if self.num_houses < 4:
            return (False, "Need 4 houses here first")
        if owner.money < self.house_cost:
            return (False, "Not enough cash")

        return (True, "")

    
    def build_house(self, owner):
        owner.pay_money(self.house_cost)
        self.num_houses += 1
        print(f"{owner.name} built a house on {self.name} (now {self.num_houses}).")
    
    def build_hotel(self, owner):
        owner.pay_money(self.house_cost)
        self.num_houses = 0
        self.has_hotel = True
        print(f"{owner.name} built a HOTEL on {self.name}.")

    def can_sell_house(self, owner, board):
        if self.owner != owner:
            return (False, "Not owner")
        if self.has_hotel:
            return (False, "Must sell hotel first")
        if self.num_houses <= 0:
            return (False, "No houses to sell")
        
        # you can not make this property have fewer houses than another property in the same set by more than 1
        group = [p for p in self.group_mates(board) if not p.has_hotel]
        max_houses = max((p.num_houses for p in group), default=0)
        if self.num_houses < max_houses:
            return (False, "Sell evenly across the set")
        return (True, "")
    
    def can_sell_hotel (self, owner, board):
        if self.owner != owner:
            return (False, "Not owner")
        if not self.has_hotel:
            return (False, "No hotel to sell")
        return (True, "")
    
    # bank pays half the house price
    def sell_house(self, owner):
        owner.collect_money(self.house_cost // 2)
        self.num_houses = max(0, self.num_houses - 1)
        print(f"{owner.name} sold a house on {self.name} (now {self.num_houses}).")

    # bank pays half the hotel price - hotel price equal the house price of color set
    def sell_hotel(self, owner):
        owner.collect_money(self.house_cost // 2)
        self.has_hotel = False
        self.num_houses = 4
        print(f"{owner.name} sold a HOTEL on {self.name} (now 4 houses).")

    def can_mortgage(self, owner, board):
        """Owner may mortgage only if this title is unmortgaged, owned by them,
        and the entire color set has NO houses/hotels."""
        if self.owner != owner:
            return (False, "Not owner")
        if self.is_mortgaged:
            return (False, "Already mortgaged")
        # cannot have improvements anywhere in the set
        for p in self.group_mates(board):
            if p.num_houses > 0 or p.has_hotel:
                return (False, "Remove houses/hotels from the whole set first")
        return (True, "")

    def can_unmortgage(self, owner):
        if self.owner != owner:
            return (False, "Not owner")
        if not self.is_mortgaged:
            return (False, "Not mortgaged")
        payoff = int(round(self.mortgage_value * 1.10))
        if owner.money < payoff:
            return (False, f"Need ${payoff} to unmortgage")
        return (True, "")

    def mortgage(self, owner):
        ok, _ = self.can_mortgage(owner, owner.board if hasattr(owner, "board") else None)
        # we trust UI/Game to check; still keep it safe:
        self.is_mortgaged = True
        owner.collect_money(self.mortgage_value)
        print(f"{owner.name} mortgaged {self.name} for ${self.mortgage_value}.")

    def unmortgage(self, owner):
        payoff = int(round(self.mortgage_value * 1.10))
        self.is_mortgaged = False
        owner.pay_money(payoff)
        print(f"{owner.name} unmortgaged {self.name} by paying ${payoff}.")





class Railroad(Space):
    """Represents a Railroad property."""
    def __init__(self, name: str, index: int, cost: int, mortgage_value: int):
        super().__init__(name, index, "Railroad")
        self.cost = cost
        self.owner = None
        self.is_mortgaged = False # Simplified: not actively used for mortgage logic
        self.mortgage_value = mortgage_value

    def calculate_rent(self, num_railroads_owned: int):
        """Calculates the rent for railroads based on how many the owner has."""
        if self.is_mortgaged:
            return 0
        rents = {1: 25, 2: 50, 3: 100, 4: 200}
        return rents.get(num_railroads_owned, 0)

    def land_on(self, player, board):
        super().land_on(player, board)
        if self.owner is None:
                affordable = player.money >= self.cost
                board.game.pending_purchase = {"player": player, "property": self, "affordable": affordable}
                if affordable:
                    print(f"  {player.name} may buy {self.name} for ${self.cost}.")
                else:
                    print(f"  {player.name} cannot afford {self.name} (${self.cost}).")
                return
    
        elif self.owner != player:
            # Railroad is owned by another player, pay rent
            num_owned = self.owner.count_railroads()
            rent_amount = self.calculate_rent(num_owned)
            if rent_amount > 0:
                board.game.pending_rent = {
                    "player": player,
                    "owner": self.owner,
                    "property": self,
                    "amount": rent_amount
                }
                print(f"  {player.name} landed on {self.name} (owned by {self.owner.name}) and pays ${rent_amount} rent.")

            else:
                print(f"  {self.name} is mortgaged, no rent due.")
        else:
            print(f"  {player.name} landed on their own railroad, {self.name}.")
    
    def can_mortgage(self, owner, board=None):
        if self.owner != owner: return (False, "Not owner")
        if self.is_mortgaged:   return (False, "Already mortgaged")
        return (True, "")

    def can_unmortgage(self, owner):
        if self.owner != owner:     return (False, "Not owner")
        if not self.is_mortgaged:   return (False, "Not mortgaged")
        payoff = int(round(self.mortgage_value * 1.10))
        if owner.money < payoff:    return (False, f"Need ${payoff}")
        return (True, "")

    def mortgage(self, owner):
        self.is_mortgaged = True
        owner.collect_money(self.mortgage_value)
        print(f"{owner.name} mortgaged {self.name} for ${self.mortgage_value}.")

    def unmortgage(self, owner):
        payoff = int(round(self.mortgage_value * 1.10))
        self.is_mortgaged = False
        owner.pay_money(payoff)
        print(f"{owner.name} unmortgaged {self.name} by paying ${payoff}.")


class Utility(Space):
    def __init__(self, name: str, index: int, cost: int, mortgage_value: int):
        super().__init__(name, index, "Utility")
        self.cost = cost
        self.owner = None
        self.is_mortgaged = False #not actively used for mortgage logic
        self.mortgage_value = mortgage_value

    def calculate_rent(self, dice_roll_sum: int, num_utilities_owned: int):
        if self.is_mortgaged:
            return 0
        if num_utilities_owned == 1:
            return dice_roll_sum * 4
        elif num_utilities_owned == 2:
            return dice_roll_sum * 10
        return 0

    def land_on(self, player, board):
        super().land_on(player, board)
        if self.owner is None:
            affordable = player.money >= self.cost
            board.game.pending_purchase = {"player": player, "property": self, "affordable": affordable}
            if affordable:
                print(f"  {player.name} may buy {self.name} for ${self.cost}.")
            else:
                print(f"  {player.name} cannot afford {self.name} (${self.cost}).")
            return
        elif self.owner != player:
            # Utility is owned by another player, pay rent
            last_roll_sum = board.game.dice.die1_value + board.game.dice.die2_value # Get the sum of the last roll
            num_owned = self.owner.count_utilities()
            rent_amount = self.calculate_rent(last_roll_sum, num_owned)
            if rent_amount > 0:
                board.game.pending_rent = {
                    "player": player,
                    "owner": self.owner,
                    "property": self,
                    "amount": rent_amount
                }
                print(f"  {player.name} landed on {self.name} (owned by {self.owner.name}) and pays ${rent_amount} rent.")
                # player.pay_money(rent_amount)
                # self.owner.collect_money(rent_amount)
            else:
                print(f"  {self.name} is mortgaged, no rent due.")
        else:
            print(f"  {player.name} landed on their own utility, {self.name}.")


    def can_mortgage(self, owner, board=None):
        if self.owner != owner: return (False, "Not owner")
        if self.is_mortgaged:   return (False, "Already mortgaged")
        return (True, "")

    def can_unmortgage(self, owner):
        if self.owner != owner:     return (False, "Not owner")
        if not self.is_mortgaged:   return (False, "Not mortgaged")
        payoff = int(round(self.mortgage_value * 1.10))
        if owner.money < payoff:    return (False, f"Need ${payoff}")
        return (True, "")

    def mortgage(self, owner):
        self.is_mortgaged = True
        owner.collect_money(self.mortgage_value)
        print(f"{owner.name} mortgaged {self.name} for ${self.mortgage_value}.")

    def unmortgage(self, owner):
        payoff = int(round(self.mortgage_value * 1.10))
        self.is_mortgaged = False
        owner.pay_money(payoff)
        print(f"{owner.name} unmortgaged {self.name} by paying ${payoff}.")

class TaxSpace(Space):
    def __init__(self, name: str, index: int, tax_amount: int):
        super().__init__(name, index, "Tax")
        self.tax_amount = tax_amount

    def land_on(self, player, board):
        super().land_on(player, board)
        board.game.pending_tax = {
            "player": player,
            "amount": self.tax_amount,
            "name": self.name
        }
        print(f"  {player.name} pays ${self.tax_amount} for {self.name}.")

class ChanceSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "Chance")

    def land_on(self, player, board):
        super().land_on(player, board)
        # Draw and execute a Chance card
        if board.game.chance_cards:
            card = board.game.chance_cards.pop(0) # Take card from top
            board.game.last_drawn_card = card
            board.game.pending_card ={
                "type": "Chance",
                "card": card,
                "player": player
            }
        else:
            print("  Chance deck is empty!")

class CommunityChestSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "Community Chest")

    def land_on(self, player, board):
        super().land_on(player, board)
        # Draw and execute a Community Chest card
        if board.game.community_chest_cards:
            card = board.game.community_chest_cards.pop(0) # Take card from top
            board.game.last_drawn_card = card
            board.game.pending_card ={
                "type": "Community Chest",
                "card": card,
                "player": player
            }        
        else:
            print("  Community Chest deck is empty!")

class GoToJailSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "GoToJail")

    def land_on(self, player, board):
        super().land_on(player, board)
        print(f"  {player.name} sent to Jail!")
        # player.in_jail = True
        # player.position = board.jail_space_index # Move to Jail space
        # player.jail_turns = 0 # Reset jail turns for entering via card
        board.game.pending_jail = {"player": player}

class JailSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "Jail")

    def land_on(self, player, board):
        super().land_on(player, board)
        # No special action for landing here if "just visiting"
        # The 'in_jail' status and related logic is handled by Game.handle_jail_turn

class FreeParkingSpace(Space):
    def __init__(self, name: str, index: int):
        super().__init__(name, index, "Free Parking")

    def land_on(self, player, board):
        super().land_on(player, board)
        print(f"  {player.name} is just visiting Free Parking.")
        # Default Monopoly rules: Free Parking does nothing.

class Board:
    def __init__(self, game_instance):
        self.spaces = []
        self.jail_space_index = 10
        self.go_space_index = 0 
        self.game = game_instance
        self.initialize_board()

    def initialize_board(self):
        
        # Brown Properties (House Cost: $50)
        self.spaces.append(GoSpace("GO", 0))
        self.spaces.append(Property("Mediterranean Avenue", 1, 60, (150, 75, 0), [2, 10, 30, 90, 160, 250], 50, 30))
        self.spaces.append(CommunityChestSpace("Community Chest", 2))
        self.spaces.append(Property("Baltic Avenue", 3, 60, (150, 75, 0), [4, 20, 60, 180, 320, 450], 50, 30))
        self.spaces.append(TaxSpace("Income Tax", 4, 200))
        
        # Railroads (Cost: $200, Mortgage: $100)
        self.spaces.append(Railroad("Reading Railroad", 5, 200, 100))

        # Light Blue Properties (House Cost: $50)
        self.spaces.append(Property("Oriental Avenue", 6, 100, (173, 216, 230), [6, 30, 90, 270, 400, 550], 50, 50))
        self.spaces.append(ChanceSpace("Chance", 7))
        self.spaces.append(Property("Vermont Avenue", 8, 100, (173, 216, 230), [6, 30, 90, 270, 400, 550], 50, 50))
        self.spaces.append(Property("Connecticut Avenue", 9, 120, (173, 216, 230), [8, 40, 100, 300, 450, 600], 50, 60))
        
        # Jail (Just Visiting)
        self.spaces.append(JailSpace("Jail / Just Visiting", 10))

        # Pink Properties (House Cost: $100)
        self.spaces.append(Property("St. Charles Place", 11, 140, (255, 0, 255), [10, 50, 150, 450, 625, 750], 100, 70))
        self.spaces.append(Utility("Electric Company", 12, 150, 75)) # Utility (Cost: $150, Mortgage: $75)
        self.spaces.append(Property("States Avenue", 13, 140, (255, 0, 255), [10, 50, 150, 450, 625, 750], 100, 70))
        self.spaces.append(Property("Virginia Avenue", 14, 160, (255, 0, 255), [12, 60, 180, 500, 700, 900], 100, 80))
        
        # Railroads
        self.spaces.append(Railroad("Pennsylvania Railroad", 15, 200, 100))

        # Orange Properties (House Cost: $100)
        self.spaces.append(Property("St. James Place", 16, 180, (255, 165, 0), [14, 70, 200, 550, 750, 950], 100, 90))
        self.spaces.append(CommunityChestSpace("Community Chest", 17))
        self.spaces.append(Property("Tennessee Avenue", 18, 180, (255, 165, 0), [14, 70, 200, 550, 750, 950], 100, 90))
        self.spaces.append(Property("New York Avenue", 19, 200, (255, 165, 0), [16, 80, 220, 600, 800, 1000], 100, 100))
        
        # Free Parking
        self.spaces.append(FreeParkingSpace("Free Parking", 20))

        # Red Properties (House Cost: $150)
        self.spaces.append(Property("Kentucky Avenue", 21, 220, (255, 0, 0), [18, 90, 250, 700, 875, 1050], 150, 110))
        self.spaces.append(ChanceSpace("Chance", 22))
        self.spaces.append(Property("Indiana Avenue", 23, 220, (255, 0, 0), [18, 90, 250, 700, 875, 1050], 150, 110))
        self.spaces.append(Property("Illinois Avenue", 24, 240, (255, 0, 0), [20, 100, 300, 750, 925, 1100], 150, 120))
        
        # Railroads
        self.spaces.append(Railroad("B. & O. Railroad", 25, 200, 100))

        # Yellow Properties (House Cost: $150)
        self.spaces.append(Property("Atlantic Avenue", 26, 260, (255, 255, 0), [22, 110, 330, 800, 975, 1150], 150, 130))
        self.spaces.append(Property("Ventnor Avenue", 27, 260, (255, 255, 0), [22, 110, 330, 800, 975, 1150], 150, 130))
        self.spaces.append(Utility("Water Works", 28, 150, 75)) # Utility
        self.spaces.append(Property("Marvin Gardens", 29, 280, (255, 255, 0), [24, 120, 360, 850, 1025, 1200], 150, 140))
        
        # Go To Jail
        self.spaces.append(GoToJailSpace("Go To Jail", 30))

        # Green Properties (House Cost: $200)
        self.spaces.append(Property("Pacific Avenue", 31, 300, (0, 255, 0), [26, 130, 390, 900, 1100, 1275], 200, 150))
        self.spaces.append(Property("North Carolina Avenue", 32, 300, (0, 255, 0), [26, 130, 390, 900, 1100, 1275], 200, 150))
        self.spaces.append(CommunityChestSpace("Community Chest", 33))
        self.spaces.append(Property("Pennsylvania Avenue", 34, 320, (0, 255, 0), [28, 150, 450, 1000, 1200, 1400], 200, 160))
        
        # Railroads
        self.spaces.append(Railroad("Short Line", 35, 200, 100))

        self.spaces.append(ChanceSpace("Chance", 36))

        # Dark Blue Properties (House Cost: $200)
        self.spaces.append(Property("Park Place", 37, 350, (0, 0, 139), [35, 175, 500, 1100, 1300, 1500], 200, 175))
        self.spaces.append(TaxSpace("Luxury Tax", 38, 100)) # Fixed tax of $100
        self.spaces.append(Property("Boardwalk", 39, 400, (0, 0, 139), [50, 200, 600, 1400, 1700, 2000], 200, 200))

class Game:
    def __init__(self, player_names: list):
        self.board = Board(self)
        self.players = [Player(name) for name in player_names]
        for p in self.players:
            p.board = self.board
        
        self.current_player_index = 0
        self.turn_number = 0
        self.game_over = False
        self.dice = Dice()
        self.chance_cards = self._initialize_cards("Chance")
        self.community_chest_cards = self._initialize_cards("Community Chest")
        self.pending_purchase = None
        self.last_drawn_card = None
        self.pending_card = None
        self.pending_build = None
        self.pending_rent = None
        self.pending_tax = None
        self.pending_jail = None
        self.pending_debt = None

        # Shuffle cards
        random.shuffle(self.chance_cards)
        random.shuffle(self.community_chest_cards)

    def _initialize_cards(self, card_type: str):
        cards = []
        if card_type == "Chance":
            cards.append(Card("Advance to GO (Collect $200)", "Chance", "move_to", target_space_index=0))
            cards.append(Card("Go to Jail. Go directly to Jail. Do not pass GO. Do not collect $200.", "Chance", "go_to_jail"))
            cards.append(Card("Bank pays you dividend of $50.", "Chance", "collect_money", value=50))
            cards.append(Card("Get Out of Jail Free Card.", "Chance", "get_out_of_jail"))
            cards.append(Card("Advance to Illinois Ave. If you pass GO, collect $200.", "Chance", "move_to", target_space_index=24))
            cards.append(Card("Advance to St. Charles Place. If you pass GO, collect $200.", "Chance", "move_to", target_space_index=11))
            cards.append(Card("Your building loan matures. Collect $150.", "Chance", "collect_money", value=150))
            cards.append(Card("Advance to Boardwalk.", "Chance", "move_to", target_space_index=39))
            cards.append(Card("Go Back 3 Spaces.", "Chance", "move_to", target_space_index=-3)) # Special handling for -3 in Card.execute
            cards.append(Card("Pay poor tax of $15.", "Chance", "pay_money", value=15))
    
        elif card_type == "Community Chest":
            cards.append(Card("Advance to GO (Collect $200)", "Community Chest", "move_to", target_space_index=0))
            cards.append(Card("Bank error in your favor. Collect $200.", "Community Chest", "collect_money", value=200))
            cards.append(Card("Go to Jail. Go directly to Jail. Do not pass GO. Do not collect $200.", "Community Chest", "go_to_jail"))
            cards.append(Card("Doctor's fee. Pay $50.", "Community Chest", "pay_money", value=50))
            cards.append(Card("From sale of stock you get $45.", "Community Chest", "collect_money", value=45))
            cards.append(Card("Get Out of Jail Free Card.", "Community Chest", "get_out_of_jail"))
            cards.append(Card("Holiday Fund matures. Collect $100.", "Community Chest", "collect_money", value=100))
            cards.append(Card("Income Tax Refund. Collect $20.", "Community Chest", "collect_money", value=20))
            cards.append(Card("It is your birthday. Collect $10 from each player.", "Community Chest", "it_is_your_birthday", value=10)) # Needs specific handling
            cards.append(Card("Life insurance matures. Collect $100.", "Community Chest", "collect_money", value=100))
            cards.append(Card("Pay Hospital $100.", "Community Chest", "pay_money", value=100))
            cards.append(Card("Pay School Tax of $150.", "Community Chest", "pay_money", value=150))
            cards.append(Card("Receive $25 consultancy fee.", "Community Chest", "collect_money", value=25))
            cards.append(Card("You are assessed for street repairs. Pay $40 per house, $115 per hotel.", "Community Chest", "street_repairs", value={"house":40, "hotel":115})) # Needs specific handling
            cards.append(Card("You have won a crossword competition. Collect $100.", "Community Chest", "collect_money", value=100))
            cards.append(Card("You inherit $100.", "Community Chest", "collect_money", value=100))

        return cards
    
    def declare_bankruptcy(self, debtor, creditor=None):
        """Remove debtor from the game, transfer assets to creditor (or bank)."""
        from game_test import Property  # safe in same file; ensures isinstance works

        # 1) Liquidate buildings to BANK at half price; give proceeds to creditor
        proceeds = 0
        for sp in list(debtor.properties_owned):
            if isinstance(sp, Property):
                # hotel (worth 5 half-house steps in our model), plus any remaining houses
                if sp.has_hotel:
                    proceeds += (sp.house_cost // 2) * 5
                    sp.has_hotel = False
                    sp.num_houses = 0
                else:
                    proceeds += (sp.house_cost // 2) * sp.num_houses
                    sp.num_houses = 0

            # 2) Transfer title to creditor or back to bank
            if creditor:
                sp.owner = creditor
                creditor.properties_owned.append(sp)
            else:
                sp.owner = None
        debtor.properties_owned.clear()

        # 3) Transfer GOJF cards
        if creditor and debtor.get_out_of_jail_free_cards > 0:
            creditor.get_out_of_jail_free_cards += debtor.get_out_of_jail_free_cards
        debtor.get_out_of_jail_free_cards = 0

        # 4) Give liquidation proceeds to creditor
        if creditor and proceeds > 0:
            creditor.collect_money(proceeds)

        # 5) Clear any pending items involving debtor
        if self.pending_rent and (self.pending_rent.get("player") is debtor or self.pending_rent.get("owner") is debtor):
            self.pending_rent = None
        if self.pending_purchase and self.pending_purchase.get("player") is debtor:
            self.pending_purchase = None
        if self.pending_build and self.pending_build.get("player") is debtor:
            self.pending_build = None
        if self.pending_tax and self.pending_tax.get("player") is debtor:
            self.pending_tax = None
        if self.pending_jail and self.pending_jail.get("player") is debtor:
            self.pending_jail = None
        if self.pending_debt and self.pending_debt.get("player") is debtor:
            self.pending_debt = None

        # 6) Remove player from the game
        if debtor in self.players:
            self.players.remove(debtor)

        # 7) Win check
        if len(self.players) == 1:
            self.game_over = True
            print(f"\n--- Game Over! {self.players[0].name} is the winner! ---")

    def start_debt(self, player, amount, creditor=None, reason=""):
        self.pending_debt = {"player": player, "amount": amount, "creditor": creditor, "reason": reason}
    def clear_debt(self):
        self.pending_debt = None


    def _transfer_property(self, prop, giver, receiver):
        """Move prop from giver to receiver, keeping houses/hotel state intact."""
        if prop in giver.properties_owned:
            giver.properties_owned.remove(prop)
            receiver.properties_owned.append(prop)
            prop.owner = receiver
    
    def execute_trade(self, p_left, p_right, offer_left, offer_right):
        """
        offer_left/right: dict like {"cash":int, "gojf":int, "props": list[Space]}
        Deduct/add cash, transfer GOJF, and move property titles.
        Returns (ok:bool, msg:str)
        """
        # Basic validations (cash/gojf availability, ownership)
        if offer_left["cash"] > p_left.money or offer_right["cash"] > p_right.money:
            return False, "One side doesn't have enough cash."

        if offer_left["gojf"] > p_left.get_out_of_jail_free_cards or offer_right["gojf"] > p_right.get_out_of_jail_free_cards:
            return False, "One side doesn't have enough Get Out of Jail Free cards."

        for sp in offer_left["props"]:
            if getattr(sp, "owner", None) != p_left:
                return False, f"{p_left.name} does not own {getattr(sp,'name','a property')}."
        for sp in offer_right["props"]:
            if getattr(sp, "owner", None) != p_right:
                return False, f"{p_right.name} does not own {getattr(sp,'name','a property')}."

        # Cash
        if offer_left["cash"] > 0:
            p_left.pay_money(offer_left["cash"])
            p_right.collect_money(offer_left["cash"])
        if offer_right["cash"] > 0:
            p_right.pay_money(offer_right["cash"])
            p_left.collect_money(offer_right["cash"])

        # GOJF cards
        if offer_left["gojf"] > 0:
            p_left.get_out_of_jail_free_cards  -= offer_left["gojf"]
            p_right.get_out_of_jail_free_cards += offer_left["gojf"]
        if offer_right["gojf"] > 0:
            p_right.get_out_of_jail_free_cards -= offer_right["gojf"]
            p_left.get_out_of_jail_free_cards  += offer_right["gojf"]

        # Properties
        for sp in list(offer_left["props"]):
            self._transfer_property(sp, p_left, p_right)
        for sp in list(offer_right["props"]):
            self._transfer_property(sp, p_right, p_left)

        return True, "Trade complete."

    def confirm_purchase(self, accept: bool):
        """Finalize a pending purchase (called from UI)."""
        if not self.pending_purchase:
            return
        info = self.pending_purchase
        player = info["player"]
        prop = info["property"]

        if accept and getattr(prop, "owner", None) is None and hasattr(prop, "cost") and player.money >= prop.cost:
            player.pay_money(prop.cost)
            player.add_property(prop)
            print(f"{player.name} bought {prop.name} for ${prop.cost}.")
        else:
            print(f"{player.name} skipped buying {prop.name}.")

        self.pending_purchase = None

    def confirm_build(self, action: str):
        """action: 'house' | 'hotel' | 'skip' """
        info = getattr(self, "pending_build", None)
        if not info: return
        player = info["player"]
        prop   = info["property"]

        if action == "house" and info["can_house"]:
            prop.build_house(player)
        elif action == "hotel" and info["can_hotel"]:
            prop.build_hotel(player)
        elif action == "sell_house" and info.get("can_sell_house"):
            prop.sell_house(player)
        elif action == "sell_hotel" and info.get("can_sell_hotel"):
            prop.sell_hotel(player)
        elif action == "mortgage" and info.get("can_mortgage"):
            prop.mortgage(player)
        elif action == "unmortgage" and info.get("can_unmortgage"):
            prop.unmortgage(player)
        else:
            print(f"{player.name} skipped building on {prop.name}.")
        self.pending_build = None

    def confirm_tax(self):
        info = getattr(self, "pending_tax", None)
        if not info: return
        p = info["player"]; amt = info["amount"]
        if p.money >= amt:
            p.pay_money(amt)
        else:
            self.start_debt(p, amt, creditor=None, reason="Tax")
        self.pending_tax = None

    def settle_rent(self):
        info = self.pending_rent
        if not info: return
        p, o, amt = info["player"], info["owner"], info["amount"]
        if p.money >= amt:
            p.pay_money(amt)
            o.collect_money(amt)
        else:
            self.start_debt(p, amt, creditor=o, reason=f"Rent: {info['property'].name}")
        self.pending_rent = None


    def start_game(self):
        print("--- Monopoly Game Started! ---")
        print(f"Players: {[p.name for p in self.players]}")

        self._determine_first_player()

        while not self.game_over:
            self.turn_number += 1
            current_player = self.players[self.current_player_index]
            
            print(f"\n--- Turn {self.turn_number}: {current_player.name}'s Turn ---")
            print(f"  Current money: ${current_player.money}")
            print(f"  Properties owned: {[p.name for p in current_player.properties_owned]}")
            print(f"  Current position: {self.board.spaces[current_player.position].name}")

            self.take_turn(current_player)

            # For this basic version, we'll just have a turn limit
            if self.turn_number >= 30: #ends after 30 turns
                self.game_over = True
                print("\n--- Game Over (Turn Limit Reached)! ---")
                for player in self.players:
                    print(f"{player.name} finished with ${player.money}")
                break # Exit the game loop

            # Move to the next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            input("\nPress Enter to continue to next player's turn...") # Pause for user

    def _determine_first_player(self):
        print("\n--- Determining First Player ---")
        highest_roll = -1
        first_player_candidates = []

        # Keep rolling until a clear first player is determined
        active_players_for_roll = list(self.players) # Start with all players
        
        while True:
            current_rolls = {}
            print("\nPlayers rolling for turn order:")
            for player in active_players_for_roll:
                input(f"  {player.name}, press Enter to roll for turn order...")
                roll_sum, _ = self.dice.roll()
                current_rolls[player] = roll_sum
                print(f"  {player.name} rolled a {roll_sum}.")

            max_roll_this_round = max(current_rolls.values())
            tied_players = [player for player, roll_sum in current_rolls.items() if roll_sum == max_roll_this_round]

            if len(tied_players) == 1:
                first_player = tied_players[0]
                self.current_player_index = self.players.index(first_player)
                print(f"\n--- {first_player.name} rolled the highest ({max_roll_this_round}) and goes first! ---")
                break # Exit the loop, first player determined
            else:
                print(f"\nTie! Players {[p.name for p in tied_players]} all rolled {max_roll_this_round}. They will re-roll.")
                active_players_for_roll = tied_players # Only tied players re-roll

    def take_turn(self, player):
        #handles a single player's turn.
        if player.in_jail:
            self.handle_jail_turn(player)
            if player.in_jail: # If still in jail after handling, turn ends
                return 

        doubles_count = 0
        while True: # Loop for rolling doubles
            roll_sum, is_double = self.dice.roll()
            
            if is_double:
                doubles_count += 1
                player.doubles_rolled_consecutive += 1
                print(f"  {player.name} rolled DOUBLES! ({player.doubles_rolled_consecutive} consecutive)")
                if player.doubles_rolled_consecutive == 3:
                    print(f"  {player.name} rolled 3 doubles in a row! Go to Jail!")
                    player.in_jail = True
                    player.position = self.board.jail_space_index
                    player.jail_turns = 0 # Reset jail turns for entering via 3 doubles
                    player.doubles_rolled_consecutive = 0 # Reset for next time
                    return # Turn ends after going to jail
            else:
                player.doubles_rolled_consecutive = 0 # Reset if no doubles

            player.move(roll_sum, self.board)

            if not is_double:
                break # End turn if no doubles

            print(f"  {player.name} gets another roll for rolling doubles!")

    def handle_jail_turn(self, player):
        """Handles a player's turn while they are in Jail."""
        print(f"  {player.name} is in Jail. Turn {player.jail_turns + 1} of 3.")
        player.jail_turns += 1

        #Use Get Out of Jail Free Card
        if player.get_out_of_jail_free_cards > 0:
            choice = 'y' #input(f"  {player.name}, use Get Out of Jail Free card? (y/n): ").lower()
            if choice == 'y':
                player.get_out_of_jail_free_cards -= 1
                player.in_jail = False
                player.jail_turns = 0
                print(f"  {player.name} used a Get Out of Jail Free card and is now out of Jail.")
                roll_sum, is_double = self.dice.roll()
                player.move(roll_sum, self.board)
                return

        # #Pay $50 Fine (available on first 3 turns)
        # if player.jail_turns <= 3:
        #     if player.money >= 50:
        #         choice = input(f"  {player.name}, pay $50 to get out of Jail? (y/n): ").lower()
        #         if choice == 'y':
        #             player.pay_money(50)
        #             player.in_jail = False
        #             player.jail_turns = 0
        #             print(f"  {player.name} paid $50 to get out of Jail.")
        #             roll_sum, is_double = self.dice.roll()
        #             player.move(roll_sum, self.board)
        #             return 
        #     else:
            print(f"  {player.name} does not have enough money to pay $50 fine.")

        #Roll for Doubles
        print(f"  {player.name} attempts to roll for doubles to get out of Jail...")
        roll_sum, is_double = self.dice.roll()
        if is_double:
            player.in_jail = False
            player.jail_turns = 0
            print(f"  {player.name} rolled doubles and is now out of Jail!")
            player.move(roll_sum, self.board)
        elif player.jail_turns >= 3:
            # If on 3rd turn and no doubles, must pay $50 (if able) or declare bankruptcy
            print(f"  {player.name} could not roll doubles on 3rd attempt. Must pay $50.")
            if player.money >= 50:
                player.pay_money(50)
                player.in_jail = False
                player.jail_turns = 0
                print(f"  {player.name} paid $50 and is now out of Jail.")
                player.move(roll_sum, self.board)
            else:
                print(f"  {player.name} cannot pay $50 and is bankrupt! Game Over for {player.name}.")
                self.players.remove(player) # Remove bankrupt player
                if len(self.players) == 1:
                    self.game_over = True
                    print(f"\n--- Game Over! {self.players[0].name} is the winner! ---")
        else:
            print(f"  {player.name} could not roll doubles and remains in Jail.")

if __name__ == "__main__":

    game = Game(player_names=["Player 1", "Player 2"])

    game.start_game()