import numpy as np
from abc import ABC

from LLM import LLM

def roll_dice(sides):
    return np.random.randint([1 for i in sides], sides, size=(len(sides)))

class entity(ABC):
    
    def __init__(self, health, strength, dexterity, constitution, intelligence, wisdom, charisma, name) -> None:
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
            print("Missed")
            damage = 0
        elif hit_roll == 20:
            print("Critical Hit")
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

class Player(entity):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.inventory = {}

    def set_weapon(self, weapon):
        self.inventory["weapon"] = weapon
    
    def get_weapon(self):
        return self.inventory["weapon"]

    def get_damage_dice(self):
        if "weapon" in self.inventory:
            return self.inventory["weapon"].get_dice()
        else: #bare-handed
            return [6]
            

class Weapon(ABC):
    def __init__(self, name, weapon_type, damage_dice) -> None:
        self.weapon_type = weapon_type
        self.name = name
        self.damage_dice = damage_dice
    
    def get_dice(self):
        return self.damage_dice

    def __repr__(self):
        return self.weapon_type
    

class Monster(entity):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.damage_dice_sides = [6]

slime = Monster(
        health=100,
        strength=8,
        dexterity=8,
        constitution=8,
        intelligence=8,
        wisdom=8,
        charisma=8,
        name="Slime"
    )

clown = Monster(
        health=200,
        strength=20,
        dexterity=8,
        constitution=8,
        intelligence=8,
        wisdom=8,
        charisma=1000,
        name="Clown"
    )

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
        return NotImplementedError
    
    def enemy_turn(self, player):
        self.enemy.attack_enemy(player)
        
    def is_encounter_over(self) -> bool:
        return not (self.player.is_alive() and self.enemy.is_alive())
            

system_message_dict = {
    "start": """You are a D&D 5e dungeonmaster. Start a new text-based rpg adventure. Describe the setting and the player character. Also fill in the blanks in the python dictionary below:
    player = { 
        name= ,
        level= ,
        strength= ,
        dexterity= ,
        constitution= ,
        intelligence= ,
        wisdom= ,
        charisma= ,
    }
    """,
    "combat": """ You are a D&D 5e dungeon master. The player is in a combat encounter with an enemy. The player stats are 
    {player_stats}, the enemy stats are {enemy_stats}. 
    """,
    "general": """You are the dungeonmaster in a text-based rpg adventure. Format your responses as follows:
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
}

'''Human
You find a slime in the dungeon
'''

'''Code
start encounter
'''

class Game():
    
    def __init__(self) -> None:
        self.llm = LLM()

        system_message = system_message_dict["start"]
        session_id = 1
        start_text = self.llm.answer("", system_message, session_id)
        print(start_text)
        self.combat = False
        while(True):
            human_input = input('> ')
            if self.combat:
                system_message = system_message_dict["combat"]
            else: 
                system_message = system_message_dict["general"]
            text = self.llm.answer(human_input, system_message, session_id)
            print(text + '\n')
    
    def start_encounter(self):
        self.combat = True

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
    p = Player(
        health=100,
        strength=8,
        dexterity=8,
        constitution=8,
        intelligence=8,
        wisdom=8,
        charisma=8,
        name="Pipo"
    )
    e = Monster(
        health=100,
        strength=8,
        dexterity=8,
        constitution=8,
        intelligence=8,
        wisdom=8,
        charisma=8,
        name="Slime"
    )

    g = Game()