from typing import Mapping

# Data pokemon vote yang akan dimanipulasi. 
# Karena kita definisikan sebagai variable,
# maka data ini akan disimpan di RAM dan akan lenyap saat program dimatikan
pokemon_vote_result: Mapping[str, str] = {
    'bulbasaur': 0,
    'charmender': 0,
    'squirtle': 0,
}

def vote_pokemon(pokemon_name: str):
    global pokemon_vote_result
    if pokemon_name not in pokemon_vote_result:
        pokemon_vote_result[pokemon_name] = 0
    pokemon_vote_result[pokemon_name] += 1

def get_vote_result():
    results = []
    for pokemon_name, vote in pokemon_vote_result.items():
        results.append('{pokemon_name}\t: {vote}'.format(pokemon_name=pokemon_name, vote=vote))
    return '\n'.join(results)

while True:
    print('== POKEMON VOTER')
    print('1. Show Vote')
    print('2. Vote Pokemon')
    print('3. Exit')
    user_choice = input('Choose action: ')
    print("Your action choice was: {}".format(user_choice))
    if user_choice == '1':
        print(get_vote_result())
    elif user_choice == '2':
        pokemon_name = input('Pokemon name: ')
        vote_pokemon(pokemon_name)
    elif user_choice == '3':
        print('Exiting program')
        break
    else:
        print('Invalid action choice')