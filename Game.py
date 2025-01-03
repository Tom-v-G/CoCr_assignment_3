from abc import ABC
import ast #string to dict conversion

from LLM import LLM

import numpy as np
from pydantic import BaseModel, Field
from typing import Dict
import re

#[6, 6]
def roll_dice(sides):
    return np.random.randint([1 for i in sides], sides, size=(len(sides)))

class entity(ABC):
    
    def __init__(self, health=100, name="test", strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=10, charisma=10) -> None:
        self.health = health

        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.actions = ["attack"] # Available to all entities

        self.name = name

        self.damage_dice_sides = [6] # 1 d6 die 

    def is_alive(self):
        """Check if the entity is still alive"""
        return self.health > 0

    def get_damage_dice(self):
        return [6]

    def get_ability_modifier(self, ability_score):
        #TODO
        return (ability_score - 10) // 2
    
    def get_armor_class(self):
        #TODO
        return 0

    def attack_enemy(self, enemy):
        AM = self.get_ability_modifier(self.strength)
        AC = enemy.get_armor_class()
        hit_roll = roll_dice([20])
        print(f"Rolled: {hit_roll}")
        damage_roll = np.sum(roll_dice(self.get_damage_dice()))
        print(f"Rolled damage: {damage_roll}")
        
        if hit_roll == 1 or (hit_roll + AM < AC) :
            print("Missed!")
            damage = 0
        elif hit_roll == 20:
            print("Critical Hit!")
            damage =  2* (damage_roll  + AM)
        else:
            damage = (damage_roll + AM)
        try: enemy.take_damage(damage)
        except: return False
        return True

    def take_damage(self, damage):
        """Reduce the entity's health by the damage amount"""
        self.health -= damage
        print(f"{self.name} has taken {damage} damage and now has {self.health} health")
        if not self.is_alive():
            return print(f"{self.name} has been defeated")

    def get_stats(self):
        stats = {
            "name": self.name,
            "health": self.health,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma
        }

        return stats

class Item(BaseModel):
    """
    Items the player can carry in their inventory. Items have a name and a description that the LLM can use to infer item effects
    """
    name: str = Field(description="Item name")
    description: str = Field(description="Description of the function of this item")

    def __hash__(self):
        return hash((self.name, self.description))

class Inventory(BaseModel):
    """
    The player inventory
    """
    inventory: Dict[Item, int] = Field(description='Character Inventory')

    def add_item(self, to_add: Item, amount: int) -> None:
        """
        Adds the specified amount of items to the inventory
        """
        for item in self.inventory.keys():
            if item == to_add:
                self.inventory[item] = self.inventory[item] + amount
                return True
        self.inventory[to_add] = amount
        return True

    def remove_item(self, to_remove: Item, amount: int):
        """
        Removes items from the inventory. returns False if the action fails (e.g. more items are requested to be removed than exist,
        item is not in inventory)
        """
        for item in self.inventory.keys():
            if item == to_remove:
                if amount > self.inventory[item]:
                    return False
                if amount == self.inventory[item]:
                    self.inventory.pop(item)
                else:
                    self.inventory[item] = self.inventory[item] - amount
                return True
        return False


class Weapon(ABC):
    def __init__(self, name=None, weapon_type=None, damage_dice=[6, 6, 6]) -> None:
        self.weapon_type = weapon_type
        self.name = name
        self.damage_dice = damage_dice
    
    def get_dice(self):
        return self.damage_dice

    def __repr__(self):
        return self.name
    

class Player(entity):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.inventory = Inventory(inventory={})
        self.weapon = None

    def set_weapon(self, weapon: Weapon):
        self.weapon = weapon
    
    def get_weapon(self):
        return self.weapon
    

    def get_damage_dice(self):
        if "weapon" in self.inventory:
            return self.inventory["weapon"].get_dice()
        else: #bare-handed
            return [6]
        
    def add_item(self, item: Item, amount: int) -> None:
        self.inventory.add_item(item, amount)
    
    def remove_item(self, item: Item, amount: int) -> None:
        self.inventory.remove_item(item, amount)

    def use_item(self, item: Item) -> None:
        self.inventory.remove_item(item, 1)
    
    def remove_item(self, item_name: str) -> None:
        for item in self.inventory:
            if item.name == item_name:
                self.inventory.remove(item) # TODO

    def get_stats(self):
        stats = {
            "name": self.name,
            "health": self.health,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "inventory": self.inventory.inventory,
            "weapon": self.weapon
        }

        return stats 


class Monster(entity):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.damage_dice_sides = [6]


class CombatEncounter():
    def __init__(self, player: Player, enemy: Monster) -> None:
        self.player = player
        self.enemy = enemy
        self.turn = 1

    def player_turn(self, action: str):
        """Handle player turn"""
        if action in self.player.actions:
            if action == "attack":
                self.player.attack_enemy(self.enemy)
            '''
            player.attack
            if enemy == dead:
                end encounter
            enemy attacks
            return dict{player stats, enemy stats}
            '''
    
    def enemy_turn(self, player):
        self.enemy.attack_enemy(player)
        
    def is_encounter_over(self) -> bool:
        return not (self.player.is_alive() and self.enemy.is_alive())
            

system_message_dict = {
    "create_setting": """You are a D&D 5e dungeonmaster. Start a new text-based rpg adventure. Describe only the setting of the adventure.""",
    "create_weapon": """You are a D&D 5e dungeonmaster, Based on the given text generate a starting weapon. Format your output as a JSON dictionary. Only return this dictionary. Fill in the blanks below
    weapon = {
        "weapon_type": ,
        "damage_dice": ,
        "name":
    }
    for the "damage_dice" in the dictionary define a list with integer values, each integer value represents the amount of sides a dice has.
    The amount of integers determines the amount of dice, e.g. [6, 6, 3], two six sided dice and one three sided.
    """,
    "create_character": """You are a D&D 5e dungeonmaster. Based on the given setting, create a character for the player. The player should not receive any starting bonusses. Format your output as a JSON dictionary. Only return this dictionary. Fill in the blanks below
    player = { 
        "name": "",
        "health": ,
        "strength": ,
        "dexterity": ,
        "constitution": ,
        "intelligence": ,
        "wisdom": ,
        "charisma": ,
    }
    """,
    "summarize": """You are a D&D 5e dungeonmaster playing a text based rpg with the user. Based on the conversation history, summarize the latest events of the game.""",
    "create_item": """You are a D&D 5e dungeonmaster. Based on the provided conversation history, create loot for the player to find. Format your output as a python dictionary.
    Only output this dictionary. Fill in the blanks below:
    item = {
        "name": "",
        "description": ""    
    }
    """,
    "use_item":""" """,
    "create_enemy": """You are a D&D 5e dungeonmaster. Based on the given setting and the supplied conversation history, fill in the dictionary below. 
    The player is allowed to attack anyone, even other humans. Format your output as a JSON dictionary. Only return this dictionary. Fill in the blanks below
    enemy = { 
        "name": "",
        "health": ,
        "strength": ,
        "dexterity": ,
        "constitution": ,
        "intelligence": ,
        "wisdom": ,
        "charisma": ,
    }
    """,
    "start": """You are a D&D 5e dungeonmaster. Start a new text-based rpg adventure. Based on the given setting and character text, describe the setting and the player character and start the adventure.""",
    "Choose response type": """You are the assistant of a D&D 5e dungeonmaster. Based on a the human input, choose which one of the following scenario's is happening. 
    The options are: 
    - Combat: The player is entering into a battle.
    - Exploration: The player is exploring their surroundings.
    - Conversation: The player is talking with someone.
    - Question: The player is asking you, the DM, a question about the adventure.
    Format your output as a single word. Example:
    ```
    Question
    ```
    Only return 'Combat' if you are absolutely sure the player is going to enter a battle.
    """,
    "question": """You are a D&D 5e dungeon master. Answer the player's question.""",
    "describe_combat_encounter": """You are a D&D 5e dungeon master. Based on the given conversation history create an enemy.and the given information about the enemy, write the setting of the combat encounter. 
    """,
    "combat": """You are a D&D 5e dungeon master. The player is in a combat encounter with an enemy. The player stats are 
    {player_stats}, the enemy stats are {enemy_stats}. 
    """,
    "exploration": """You are a D&D 5e dungeon master. Based on the conversation history and the player input describe what is happening. Keep the players intelligence and wisdom score in mind. 
    """,
    "conversation": """You are a D&D 5e dungeon master. Based on the conversation history and the player input describe what is happening. Keep the players charisma score in mind.""",
    "general": """You are the dungeonmaster in a text-based rpg adventure. Respond to the player input based on the conversation history."""
}

"""
    Format your responses as follows:
    '''human readable
    This part should be human readable text describing the current situation
    '''

    '''
    choose one of the following strings to return based on the current situation:
     - "start encounter"
     - "give item"
     - "exit game"
     - "charisma check"
     - "do nothing" 
    '''
"""

class Game():
    
    def __init__(self) -> None:
        self.llm = LLM()
        self.conversation_history = []
        session_id = 0
        self.combat_session_id = 100
        self.enemy_creation_id = 10000

        system_message = system_message_dict["create_setting"]
        setting_text = self.query_llm("", system_message, session_id)
        print(f"Setting text: \n {setting_text}")
        print("-"*50)
        
        # Player Initialisation
        session_id = 1
        system_message = system_message_dict["create_character"]
        not_done = True
        while(not_done):
            character_text = self.query_llm(setting_text, system_message, session_id)
            print(f"Character text: \n {character_text}")
            not_done = not self.parse_player(character_text)
        print("-"*50)

        session_id = 2
        system_message = system_message_dict["create_weapon"]
        not_done = True
        while(not_done):
            weapon_text = self.query_llm(character_text, system_message, session_id)
            print(weapon_text)
            weapon = self.parse_weapon(weapon_text)

            not_done = not isinstance(weapon, Weapon)
            
        self.player.set_weapon(weapon=weapon)

        print(self.player.get_stats())
        print("-"*50)
        session_id = 3
        # TODO: supply character and setting text  
        system_message = system_message_dict["start"]
        print(self.query_llm(f"""Setting description: \n {setting_text} \n Character description: \n {character_text}
                            \n Weapon description: \n {weapon_text}
                              """, system_message, session_id))

    def parse_human_input(self):
        print('-'*100)
        human_input = input('> ')
        self.conversation_history.append(human_input)
        return human_input

    def query_llm(self, human_input, system_message, session_id):
        text = self.llm.answer(human_input, system_message, session_id)
        self.conversation_history.append(text)
        return text

    def main_loop(self):
        
        while(True):
            # Allow for human input
            human_input = self.parse_human_input()

            # Let LLM choose the response type
            session_id = 3
            not_done = True
            counter = 0
            while(not_done):
                system_message = system_message_dict["Choose response type"]
                llm_response_type = self.query_llm(human_input, system_message=system_message, session_id=session_id)
                print(llm_response_type)
                llm_response_type = self.parse_response_type(llm_response_type)
                # print(llm_response_type)
                if llm_response_type !='general':
                    not_done = False
                counter += 1
                if counter > 2:
                    break
            system_message = llm_response_type

            if system_message == "combat":
                self.run_combat()
                self.combat_session_id += 1
            else:    
                # Let the LLM repond
                text= self.query_llm("", system_message_dict[llm_response_type], session_id=session_id)
                print(text + '\n')
                print('-'*50)

    def parse_weapon(self, weapon_string: str) -> Weapon:
        """
        Tries to parse LLM text to a Weapon class instance and sets the player weapon. Returns false if unsuccesfull
        """
            
        try: 
            weapon_dict = ast.literal_eval(weapon_string)
            weapon = Weapon(**weapon_dict)
        except Exception as e:
            # print(e)
            try: 
                # Try finding the dictionary string in the LLM output
                weapon_string = re.search('\{(.|\n)*\}', weapon_string).group()
                weapon_dict = ast.literal_eval(weapon_string)
                weapon = Weapon(**weapon_dict)
            except Exception as e2:
                print(e2)
                return False
        return weapon

    def parse_player(self, player_string: str) -> Player:
        """
        Tries to parse LLM text to a Player class instance. Returns false if unsuccesfull
        """
        try:
            player_dict = ast.literal_eval(player_string)
            self.player = Player(**player_dict)
        except Exception as e:
            # print(e)
            try: 
                # Try finding the dictionary string in the LLM output
                player_string = re.search('\{(.|\n)*\}', player_string).group()
                player_dict = ast.literal_eval(player_string)
                self.player = Player(**player_dict)
            except Exception as e2:
                print(e2)
                return False
        
        return True
    
    def parse_response_type(self, text: str) -> str:
        """
        Parses LLM output to corresponding entry in the system_message dictionary.
        """
        match text.lower():
            case 'combat':  return 'combat'
            case 'exploration': return 'exploration'
            case 'conversation': return 'conversation'
            case 'question': return 'question'
        return 'general'

    def run_combat(self):
        
        # systemmessage: LLM creeert monster
        # systemmessage: gebasseerd op monster, schrijf begin van encounter
        # -> inject character, weapon and conversation history
        # initiative roll: -> monster eerst of player eerst
        # systemmessage: parse player input: attack, gebruik item uit inventory, question, of run away (gebasseerd op dexterity roll oid)
        #   
        enemy = self.create_enemy()
        print(enemy.get_stats())
        text = self.query_llm(f"Conversation history: {self.conversation_history[-5:]} \n Enemy: {enemy.get_stats()}", 
                       system_message_dict["describe_combat_encounter"], 
                       session_id=self.combat_session_id)
        print(text)
        while(True):
            human_input =  self.parse_human_input()

            print(self.query_llm(human_input, 
                       system_message_dict["parse_combat_input"], 
                       session_id=self.combat_session_id))

        # combat = CombatEncounter(player=self.player, enemy=enemy)
        # return combat
        

    def create_enemy(self):
        '''

        '''

        system_message = system_message_dict["create_enemy"]
        # Cap recent history_input
        history_length = 10
        history_input = self.conversation_history[-history_length:] if len(self.conversation_history) > history_length else self.conversation_history
        print(history_input)

        while(True):
            enemy_text = self.query_llm(history_input, system_message, session_id=self.enemy_creation_id)
            print(enemy_text)
            try: 
                enemy = Monster(**ast.literal_eval(enemy_text))
                break
            except:
                continue
            
        self.enemy_creation_id += 1
        return enemy

    # self.llm 
    # llm_input_string:
    #     player stats 
    #     player inventory: {}
    #     the player is in an encounter:
    #         enemy: 


    # llm output: {"Text op het scherm", gamefunction}

    # Chat example
    # llm: you have encountered a slime: yadaya slime stats
    # llm: what would you like to do?

    # player: I attack

    # llm_response = {human readable text: "You swing at the slime with your sword", combatencouter.turn()}
    # print(llm_response["human_readable"])
    # game.process(llm_response:["function"])

    # system_prompt: process the input from the player: return a text and a function, this is the list of possible functions:
    # ... 

if __name__ == "__main__":
    # p = Player(
    #     health=100,
    #     strength=8,
    #     dexterity=8,
    #     constitution=8,
    #     intelligence=8,
    #     wisdom=8,
    #     charisma=8,
    #     name="Pipo"
    # )
    # e = Monster(
    #     health=100,
    #     strength=8,
    #     dexterity=8,
    #     constitution=8,
    #     intelligence=8,
    #     wisdom=8,
    #     charisma=8,
    #     name="Slime"
    # )
    text = """{
        "name": "Test",
        "health": 100,
        "strength": 10,
        "dexterity": 12,
        "constitution": 13,
        "intelligence": 14,
        "wisdom": 15,
        "charisma": 16
    }"""

    weapon = """{
        "weapon_type": "Staff",
        "damage_dice": [20, 6, 3],
        "name": "Giga staff"
    }"""

    # player_dict = ast.literal_eval(text)
    # player = Player(**player_dict)

    # weapon_dict = ast.literal_eval(weapon)
    # player_weapon = Weapon(**weapon_dict)
    # player.weapon = player_weapon
    
    # print(player.get_stats())
    # player.add_item(Item(name='health potion', description='gives health'), 2)
    # print(player.get_stats())

    g = Game()
    g.main_loop()