import sys
import os
import math
from typing import List, Dict, Tuple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from env.blackjack_env import hand_value
    from agents.evaluation import get_stand_value
except ImportError:
    print("Error: No se pudo encontrar blackjack_env.py o evaluation.py.")
    print("Asegúrate de que la estructura de carpetas es correcta.")
    sys.exit(1)
DEFAULT_MAX_DEPTH = 4
CARD_PROBABILITIES = [(rank, 1/13) for rank in range(1, 14)]

def find_best_move(state: Dict, max_depth: int = DEFAULT_MAX_DEPTH) -> str:
    """
    Función principal que inicia la búsqueda Expectimax.
    Decide entre 'hit' y 'stand'.
    """
    player_hand = state["player"]
    dealer_hand = state["dealer"]

    stand_eval = get_stand_value(player_hand, dealer_hand)
    
    hit_eval = _expected_value(player_hand, dealer_hand, max_depth - 1)

    if stand_eval >= hit_eval:
        return "stand"
    else:
        return "hit"

def _max_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el turno del jugador (Agente Max).
    Es idéntico al de Minimax, pero sin alpha/beta.
    """

    player_total, _ = hand_value(player_hand)

    if player_total > 21:
        return -1.0
    
    if depth == 0:
        return get_stand_value(player_hand, dealer_hand)


    # 1. Evaluar "stand"
    stand_eval = get_stand_value(player_hand, dealer_hand)

    # 2. Evaluar "hit"
    hit_eval = _expected_value(player_hand, dealer_hand, depth - 1)
        
    return max(stand_eval, hit_eval)

def _expected_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el nodo de AZAR (Chance Node).
    Esto REEMPLAZA a _min_value.
    Calcula el valor esperado (promedio ponderado) de pedir "hit".
    """
    
    total_expected_value = 0.0


    for rank, probability in CARD_PROBABILITIES:
        
        new_player_hand = player_hand + [rank]
        
        eval_of_this_branch = _max_value(new_player_hand, dealer_hand, depth)
        
        total_expected_value += (eval_of_this_branch * probability)

    return total_expected_value

if __name__ == "__main__":
    from env.blackjack_env import BlackjackEnv, hand_value

    print("--- Prueba 1: Jugador 19 vs Dealer 18 ---")
    state1 = {
        "player": [10, 10],
        "dealer": [10, 10],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action1 = find_best_move(state1)
    print(f"Mano Jugador: {state1['player']} (Total: {hand_value(state1['player'])[0]})")
    print(f"Mano Dealer: {state1['dealer']} (Total: {hand_value(state1['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action1}") 
    print("-" * 20)

    print("--- Prueba 2: ¡¡Jugador 11 vs Dealer 17!! ---")
    state2 = {
        "player": [5, 6],
        "dealer": [10, 7],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action2 = find_best_move(state2)
    print(f"Mano Jugador: {state2['player']} (Total: {hand_value(state2['player'])[0]})")
    print(f"Mano Dealer: {state2['dealer']} (Total: {hand_value(state2['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action2}") 
    print("-" * 20)

    print("--- Prueba 3: Jugador 12 vs Dealer 4 ---")
    state3 = {
        "player": [2, 10],
        "dealer": [2, 2],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action3 = find_best_move(state3)
    print(f"Mano Jugador: {state3['player']} (Total: {hand_value(state3['player'])[0]})")
    print(f"Mano Dealer: {state3['dealer']} (Total: {hand_value(state3['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action3}") 
    print("-" * 20)