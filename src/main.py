# src/main.py

import json
from character import Character # Importa nossa classe Character do arquivo character.py

def load_game_data(file_path):
    """
    Carrega os dados de um arquivo JSON.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo de dados {file_path} não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {file_path} não é um JSON válido.")
        return None

def main():
    """
    Função principal do nosso programa.
    """
    print("Bem-vindo ao Gerador de Personagens de Vampiro: A Máscara!")
    
    # Carrega os dados dos clãs
    clans_data = load_game_data('data/clans.json')
    if not clans_data:
        return # Encerra o programa se os dados não puderem ser carregados

    # Por enquanto, vamos criar um personagem com dados fixos para testar
    # No futuro, pediremos essas informações ao usuário
    
    player_character = Character("Lestat")
    player_character.set_clan("Ventrue", clans_data)
    player_character.show_sheet()

    # Vamos criar outro para ver a flexibilidade
    npc_character = Character("Lily")
    npc_character.set_clan("Toreador", clans_data)
    npc_character.show_sheet()

if __name__ == "__main__":
    # Esta linha garante que a função main() só será executada
    # quando rodarmos o arquivo main.py diretamente.
    main()