"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate
an entire playthrough of the self._game. Please consult the project handout for
instructions and details.

You can copy/paste your code from Assignment 1 into this file, and modify it as
needed to work with your self._game.

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
from event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # Hint: self._game.get_location() gives you back the current location
        current_location = self._game.get_location()
        first_event = Event(current_location.id_num, current_location.long_description)
        self._events.add_event(first_event)

        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, current_location)

    def _find_item(self, item_name: str, item_list: list) -> str:
        """
        Find the matched item from the list
        """
        for item in item_list:
            if item.lower() == item_name:
                return item
        return ""

    def _remove_item(self, item_found: str) -> None:
        """
        Remove the item from the user's inventory
        """
        new_inventory = {}
        for item_name in self._game.inventory:
            if item_name != item_found:
                new_inventory[item_name] = self._game.inventory[item_name]
        self._game.inventory = new_inventory

    def _pick_up(self, command: str, current_location: Location) -> None:
        """
        The helper function for pick up command
        """
        item_name_input = command[8:]
        item_found = self._find_item(item_name_input, current_location.items)
        if item_found == "":
            print("Item is not here!")
        elif len(self._game.inventory) >= 2:
            print("Inventory is full!")
        else:
            item = self._game.get_item(item_found)
            if item is not None:
                self._game.inventory[item_found] = item
                current_location.items.remove(item_found)
                print("Picked up:", item_found)

                if item_found in ["USB Drive", "Laptop Charger", "Lucky Mug"]:
                    self._game.score = self._game.score + 0
                    print("Score:", self._game.score)

    def _drop(self, command: str, current_location: Location) -> None:
        """
        The helper function for drop
        """
        item_name_input = command[5:]
        item_found = self._find_item(item_name_input, list(self._game.inventory.keys()))
        if item_found != "":
            if item_found.lower() == "t-card" and current_location.id_num == 13:
                print("You cannot drop the T-card here! You need it to exit the library!")
            elif item_found.lower() == "dorm key" and current_location.id_num == 15:
                print("You cannot drop the Dorm Key here! You need it to enter Oak House again!")
            else:
                self._remove_item(item_found)
                current_location.items.append(item_found)
                print("Dropped:", item_found)
        else:
            print("You don't have that!")

    def _deposit(self, command: str, current_location: Location) -> None:
        """
        The helper function for deposit
        """
        item_name_input = command[8:]
        if current_location.id_num != 15:
            print("You can only deposit at Oak House!")
        else:
            item_found = self._find_item(item_name_input, list(self._game.inventory.keys()))
            if item_found != "":
                points = 0
                item = self._game.get_item(item_found)
                if item is not None and current_location.id_num == item.target_position:
                    points = item.target_points
                self._remove_item(item_found)
                self._game.deposited_items.add(item_found)
                print("Deposited:", item_found)

                if points > 0:
                    self._game.score = self._game.score + points
                    print("Earned", points, "points!")
                    print("Score:", self._game.score)
            else:
                print("You don't have that!")

    def _go(self, command: str, current_location: Location) -> Location:
        """
        The helper function for go
        """
        next_id = current_location.available_commands[command]
        can_enter = True
        if next_id == 13:
            if "T-card" not in self._game.inventory:
                print("Robarts is locked! You need a T-card!")
                can_enter = False
        if next_id == 15:
            if "Dorm Key" not in self._game.inventory:
                print("Oak House is locked! You need a Dorm Key!")
                can_enter = False
        if can_enter:
            self._game.current_location_id = next_id
            self._game.moves = self._game.moves + 1
            return self._game.get_location()
        return current_location

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """

        # Hint: current_location.available_commands[command] will return the next location ID
        # which executing <command> while in <current_location_id> leads to
        for command in commands:
            if "pick up " in command:
                self._pick_up(command, current_location)
            elif "drop " in command:
                self._drop(command, current_location)
            elif "deposit " in command:
                self._deposit(command, current_location)
            elif "go " in command:
                current_location = self._go(command, current_location)
            event = Event(current_location.id_num, current_location.long_description)
            self._events.add_event(event, command)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and log location descriptions.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    win_walkthrough = [
        "go south",
        "go south",
        "go east",
        "go east",
        "go east",
        "go north",
        "go north",
        "pick up lucky mug",
        "pick up t-card",
        "go south",
        "go south",
        "go west",
        "go west",
        "go south",
        "drop lucky mug",
        "go west",
        "pick up dorm key",
        "go east",
        "drop t-card",
        "pick up lucky mug",
        "go east",
        "deposit lucky mug",
        "go north",
        "pick up laptop charger",
        "go south",
        "deposit laptop charger",
        "go north",
        "pick up usb drive",
        "go south",
        "deposit usb drive"
    ]  # Create a list of all the commands needed to walk through your game to win it
    expected_log = [1, 5, 9, 10, 11, 12, 8, 4, 4, 4, 8, 12, 11, 10, 14, 14, 13, 13, 14, 14, 14, 15, 15,
                    11, 11, 15, 15, 11, 11, 15, 15]
    # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your walkthrough
    sim = AdventureGameSimulation('project1/game_data.json', 1, win_walkthrough)
    assert expected_log == sim.get_id_log()

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    lose_demo = [
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north",
        "go south",
        "go north"
    ]
    expected_log = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5,
                    1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your demo
    sim = AdventureGameSimulation('project1/game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()

    inventory_demo = [
        "go south",
        "go south",
        "go east",
        "go east",
        "pick up usb drive",
        "inventory"
    ]
    expected_log = [1, 5, 9, 10, 11, 11, 11]
    sim = AdventureGameSimulation('project1/game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()

    scores_demo = [
        "go south",
        "go south",
        "go east",
        "go east",
        "go east",
        "go north",
        "go north",
        "pick up lucky mug",
        "pick up t-card",
        "go south",
        "go south",
        "go west",
        "go west",
        "go south",
        "drop lucky mug",
        "go west",
        "pick up dorm key",
        "go east",
        "drop t-card",
        "pick up lucky mug",
        "go east",
        "deposit lucky mug"
    ]
    expected_log = [1, 5, 9, 10, 11, 12, 8, 4, 4, 4, 8, 12, 11, 10, 14, 14, 13, 13, 14, 14, 14, 15, 15]
    sim = AdventureGameSimulation('project1/game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()

    # Add more enhancement_demos if you have more enhancements
    # Showing the differences between drop and deposit (drop is just dropping the item,
    # while deposit is for the item to earn a score)
    enhancement1_demo = [
        "go south",
        "go south",
        "go east",
        "go east",
        "go east",
        "go north",
        "go north",
        "pick up lucky mug",
        "pick up t-card",
        "go south",
        "go south",
        "go west",
        "go west",
        "go south",
        "drop lucky mug",
        "go west",
        "pick up dorm key",
        "go east",
        "drop t-card",
        "pick up lucky mug",
        "go east",
        "deposit lucky mug"
    ]
    expected_log = [1, 5, 9, 10, 11, 12, 8, 4, 4, 4, 8, 12, 11, 10, 14, 14, 13, 13, 14, 14, 14, 15, 15]
    sim = AdventureGameSimulation('project1/game_data.json', 1, enhancement1_demo)
    assert expected_log == sim.get_id_log()

    # Enhancement2: Showing the locked and unlocked (only at the oak house and robarts library)
    enhancement2_demo = [
        "go south",
        "go south",
        "go east",
        "go east",
        "go east",
        "go north",
        "go north",
        "pick up lucky mug",
        "pick up t-card",
        "go south",
        "go south",
        "go south",
        "go west",
        "go north",
        "go west",
        "go west",
        "go south",
        "drop lucky mug",
        "go west",
        "pick up dorm key",
        "go east",
        "go east"
    ]
    expected_log = [1, 5, 9, 10, 11, 12, 8, 4, 4, 4, 8, 12, 16, 16, 12, 11, 10, 14, 14, 13, 13, 14, 15]
    sim = AdventureGameSimulation('project1/game_data.json', 1, enhancement2_demo)
    assert expected_log == sim.get_id_log()

    # Note: You can add more code below for your own testing purposes
