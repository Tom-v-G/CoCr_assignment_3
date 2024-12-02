Codebase:
Tier I
- Player Class
- Monster Class
- Combat Mechanics
- Link combat mechanics to LLM (only storytelling)

Functies waartoe de LLM toegang heeft:
    - get_stats
    - give_item {}
    - start encounter {"slime"} 

generate a enemy based on d&d 5e rulesets with the name ... 

# volgorde
1a. instantiate LLM die avontuur verzint -> schrijf uit naar txt file
1b. schrijf player stats uit naar file / variabele
2. instantiate LLM die txt file leest en lijst van monsters maakt -> schrijf uit naar txt file
3. instantiate LLM die DMed: opening message
3. Main loop:
    - player input
    - LLM return tekst en function header
    

Tier II
- Allow LLM to generate monsters :
LLM: {Verhaaltje: " je komt een slime tegen", functieheader: initalise_monster(type: slime, health: 100, attack: 50)}
"Return a json object with a story for the player and a function.."
- Allow LLM to initialise player 

Advanced:
- GUI
