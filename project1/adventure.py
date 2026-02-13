"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from game_entities import Location, Item
from event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The ID of the location where the players currently is
        - score: The player's current score
        - moves: The number of moves that the player has made
        - inventory: Dictionary of items currently in player's possession
        - deposited_items: Set of item names that have been deposited at Oak House

    Representation Invariants:
        - current_location_id in self._locations
        - score >= 0
        - moves >= 0
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    score: int
    moves: int
    inventory: dict[str, Item]
    deposited_items: set[str]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.score = 0
        self.moves = 0
        self.inventory = {}
        self.deposited_items = set()

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'].copy(),
                                    loc_data['name'], loc_data['visited'])
            locations[loc_data['id']] = location_obj

        items = []

        for item_data in data['items']:
            item_obj = Item(item_data['name'], item_data['start_position'],
                            item_data['target_position'], item_data['target_points'], item_data['description'])
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        if loc_id is None:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def check_locked_door(self, destination_id: int) -> bool:
        """
        Check if the door is locked or not
        """
        if destination_id == 13:
            if "T-card" not in self.inventory:
                print("The library is locked! You need T-card in your inventory!")
                return False
            else:
                print("Library doors unlock!")
                return True
        if destination_id == 15:
            if "Dorm Key" not in self.inventory:
                print("The residence is locked, you need Dorm Key in you inventory!")
                return False
            else:
                print("The residence is unlock!")
                print("This is Oak House, use deposit command to earn points!")
                return True
        return True

    def check_inventory_full(self) -> bool:
        """
        Check if inventory is full (max 2)
        """
        return len(self.inventory) >= 2

    def check_win(self) -> bool:
        """
        Check if the player won the game
        Win condition: All 3 required items are deposited at Oak House
        """
        required_items = {"USB Drive", "Laptop Charger", "Lucky Mug"}
        return all(item in self.deposited_items for item in required_items)

    def check_lose(self) -> bool:
        """
        Check if the player lost the game.
        Lost condition: Player used all available moves which is 50
        """
        return self.moves >= 50

    def calculate_deposit_points(self, deposited_item_name: str) -> int:
        """
        Calculate points for depositing an item at the current location
        Returns points that the user earned (if the item is already deposited then
        0 points)
        """
        if deposited_item_name in self.deposited_items:
            return 0
        for items in self._items:
            if items.name == deposited_item_name:
                if self.current_location_id == items.target_position:
                    return items.target_points
                return 0
        return 0

    def get_item(self, name: str) -> Optional[Item]:
        """
        Return the object Item with the given name, or None if no such item exists
        """
        for items in self._items:
            if items.name == name:
                return items
        return None


def listed_items(commands: dict, words: str) -> set[str]:
    """
    Return a set of item names from command that start with the given words
    """
    results = set()
    word_len = len(words)
    for command in commands:
        if command[:word_len] == words:
            results.add(command[word_len:])
    return results


def get_available_actions(loc: Location, inventory: dict) -> list:
    """
    Return filtered list of available actions based on current inventory and location's items
    """
    actions = []
    for act in loc.available_commands:
        if act[:3] == "go ":
            actions.append(act)
        elif act[:8] == "pick up ":
            items_name = act[8:]
            if any(name.lower() == items_name for name in loc.items):
                actions.append(act)
        elif act[:5] == "drop ":
            items_name = act[5:]
            if any(name.lower() == items_name for name in inventory):
                actions.append(act)
        elif act[:8] == "deposit ":
            items_name = act[8:]
            if any(name.lower() == items_name for name in inventory):
                actions.append(act)

    listed_pickups = listed_items(loc.available_commands, "pick up ")

    for loc_item in loc.items:
        if loc_item.lower() not in listed_pickups:
            actions.append("pick up " + loc_item.lower())

    listed_drops = listed_items(loc.available_commands, "drop ")

    for inv_item in inventory:
        if inv_item.lower() not in listed_drops:
            actions.append("drop " + inv_item.lower())

    return actions


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('project1/game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "log", "quit"]  # Regular menu options available at each location
    choice = None

    print("You wake up in a panic. Your CS project is due at 1pm today, \n but you are missing critical items!")
    print("MISSION: Find and Deposit these items at Oak House:")
    print("     1. USB Drive")
    print("     2. Laptop Charger")
    print("     3. Lucky Mug")
    print("\n*** You can only carry 2 items at a time! ***")
    print("\nCommands:")
    print("     1. drop: Leave items on ground (can pick up later, no points)")
    print("     2. deposit: Deliver items at Oak House (you can earn points)")
    print("\nLocked Locations:")
    print("     1. Robarts Library requires T-card")
    print("     2. Oak House requires Dorm Key")
    print("*** Keys never expire! Just keep them in inventory to enter those locations")
    print("*** HINT! Dorm key at Robarts library, T-card at Cafe ***")

    ongoing = True
    while ongoing:

        location = game.get_location()

        event = Event(location.id_num, location.long_description)
        game_log.add_event(event, choice)

        if location.visited:
            print(location.brief_description)
        else:
            descrip = location.long_description
            if location.id_num == 13 and "T-card" in game.inventory:
                descrip = descrip.replace("(LOCKED)", "(UNLOCKED)")
            elif location.id_num == 15 and "Dorm Key" in game.inventory:
                descrip = descrip.replace("(LOCKED)", "(UNLOCKED)")
            print(descrip)
            location.visited = True

        if location.id_num == 13:
            if "T-card" in game.inventory:
                print("[Robarts Library: UNLOCKED - T-card in your inventory]")
            else:
                print("[Robarts Library: LOCKED - T-card required to enter]")
        elif location.id_num == 15:
            if "Dorm Key" in game.inventory:
                print("[Oak House: UNLOCKED - Dorm Key in your inventory]")
            else:
                print("[Oak House: LOCKED - Dorm Key required to enter]")

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, log, quit")
        print("At this location, you can also:")
        for action in get_available_actions(location, game.inventory):
            print("-", action)

        def is_valid_drop(comm: str) -> bool:
            """
            Check if the user can drop the item
            """
            if comm[:5] == "drop ":
                items_name = comm[5:]
                for name in game.inventory:
                    if name.lower() == items_name:
                        return True
            return False

        def is_valid_pickup(comm: str) -> bool:
            """
            Check if the user can pick up the item at the current location
            """
            if comm[:8] == "pick up ":
                items_name = comm[8:]
                for name in location.items:
                    if name.lower() == items_name:
                        return True
            return False

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while not any([
            choice in location.available_commands,
            choice in menu,
            is_valid_drop(choice),
            is_valid_pickup(choice)
        ]):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("=================================================")
        print("You decided to:", choice)

        if choice in menu:
            if choice == "log":
                game_log.display_events()
            elif choice == "look":
                print(location.long_description)
            elif choice == "inventory":
                print("Your inventory:", len(game.inventory), "/", 2)
                for item_name in game.inventory:
                    print(" - ", item_name)
            elif choice == "score":
                print("Score:", game.score)
                print("Moves:", game.moves, "/", 50)
                print("Deposited:", len(game.deposited_items), "/3")
            elif choice == "quit":
                print("Game Over!")
                ongoing = False

        else:
            # Handle non-menu actions
            if choice in location.available_commands:
                result = location.available_commands[choice]
            else:
                result = None

            if "pick up " in choice:
                item_name_input = choice[8:]
                item_found = ""
                for item_name in location.items:
                    if item_name.lower() == item_name_input:
                        item_found = item_name
                if item_found != "":
                    if len(game.inventory) >= 2:
                        print("Inventory is full!")
                    else:
                        item = game.get_item(item_found)
                        if item is not None:
                            game.inventory[item_found] = item
                            location.items.remove(item_found)
                            print("Picked up:", item_found)

                            if item_found in ["USB Drive", "Laptop Charger", "Lucky Mug"]:
                                game.score = game.score + 0
                                print("Score:", game.score)
                else:
                    print("Item is not here!")

            elif "drop " in choice:
                item_name_input = choice[5:]
                item_found = ""
                for item_name in game.inventory:
                    if item_name.lower() == item_name_input:
                        item_found = item_name
                if item_found != "":
                    if item_found.lower() == "t-card" and location.id_num == 13:
                        print("You cannot drop the T-card here!")
                    elif item_found.lower() == "dorm key" and location.id_num == 15:
                        print("You cannot drop the Dorm Key here!")
                    else:
                        new_inventory = {}
                        for item_name in game.inventory:
                            if item_name != item_found:
                                new_inventory[item_name] = game.inventory[item_name]
                        game.inventory = new_inventory
                        location.items.append(item_found)
                        print("Dropped:", item_found)
                else:
                    print("You don't have that!")

            elif "deposit " in choice:
                item_name_input = choice[8:]
                if location.id_num != 15:
                    print("You can only deposit at Oak House!")
                else:
                    item_found = ""
                    for item_name in game.inventory:
                        if item_name.lower() == item_name_input:
                            item_found = item_name
                    if item_found != "":
                        points = 0
                        item = game.get_item(item_found)
                        if item is not None and location.id_num == item.target_position:
                            points = item.target_points
                        new_inventory = {}
                        for item_name in game.inventory:
                            if item_name != item_found:
                                new_inventory[item_name] = game.inventory[item_name]
                        game.inventory = new_inventory
                        game.deposited_items.add(item_found)
                        print("Deposited:", item_found)

                        if points > 0:
                            game.score = game.score + points
                            print("Earned", points, "points!")
                            print("Score:", game.score)
                    else:
                        print("You don't have that!")

            elif "go " in choice:
                next_id = location.available_commands[choice]
                can_enter = True
                if next_id == 13:
                    if "T-card" not in game.inventory:
                        print("Robarts is locked! You need a T-card!")
                        can_enter = False
                if next_id == 15:
                    if "Dorm Key" not in game.inventory:
                        print("Oak House is locked! You need a Dorm Key!")
                        can_enter = False
                if can_enter:
                    game.current_location_id = next_id
                    game.moves = game.moves + 1

        win = True
        if "USB Drive" not in game.deposited_items:
            win = False
        if "Laptop Charger" not in game.deposited_items:
            win = False
        if "Lucky Mug" not in game.deposited_items:
            win = False

        if win:
            print("You win!")
            print("Final Score:", game.score)
            ongoing = False

        if game.moves >= 50:
            print("Game Over!")
            print("Final Score:", game.score)
            ongoing = False
