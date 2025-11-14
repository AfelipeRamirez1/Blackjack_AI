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
    print("Asegúrate de que la estructura de carpetas es correcta y estás ejecutando desde la raíz.")
    sys.exit(1)


def find_best_move(state: Dict, max_depth: int = DEFAULT_MAX_DEPTH) -> str:
    """
    Función principal que inicia la búsqueda Minimax con Poda Alfa-Beta.
    Decide entre 'hit' y 'stand' en el nodo raíz.
    """
    player_hand = state["player"]
    dealer_hand = state["dealer"]
    
    alpha = -math.inf
    beta = math.inf

    # --- 1. Evaluar la acción "stand" ---
    stand_eval = get_stand_value(player_hand, dealer_hand)
    
    # Actualizamos 'alpha' (lo mejor que Max puede conseguir) con este valor.
    alpha = max(alpha, stand_eval)
    
    # --- 2. Evaluar la acción "hit" ---
    hit_eval = _min_value(player_hand, dealer_hand, max_depth - 1, alpha, beta)

    # --- 3. Decisión Final ---
    if stand_eval >= hit_eval:
        return "stand"
    else:
        return "hit"

def _max_value(player_hand: List[int], dealer_hand: List[int], depth: int, alpha: float, beta: float) -> float:
    """
    Representa el turno del jugador (Agente Max).
    El jugador acaba de recibir una carta del "mazo malicioso" y debe
    decidir de nuevo entre "hit" y "stand".
    """
    
    # --- Casos Base (Terminales) ---
    player_total, _ = hand_value(player_hand)

    # 1. El jugador se pasó (Bust)
    if player_total > 21:
        return -1.0
    
    # 2. Se alcanzó la profundidad máxima de búsqueda
    if depth == 0:
        return get_stand_value(player_hand, dealer_hand)

    # --- Búsqueda Recursiva (Turno de Max) ---
    max_eval = -math.inf

    # 1. Evaluar "stand"
    stand_eval = get_stand_value(player_hand, dealer_hand)
    max_eval = max(max_eval, stand_eval)
    alpha = max(alpha, max_eval) # Actualizar alpha

    # 2. Evaluar "hit" (si no hemos sido podados)
    # Solo exploramos "hit" si beta (lo peor para Min) es aún
    # mayor que alpha (lo mejor para Max).
    if beta > alpha:
        # Llamamos a _min_value, el "mazo malicioso"
        hit_eval = _min_value(player_hand, dealer_hand, depth - 1, alpha, beta)
        max_eval = max(max_eval, hit_eval)
        alpha = max(alpha, max_eval) # Actualizar alpha

    return max_eval

def _min_value(player_hand: List[int], dealer_hand: List[int], depth: int, alpha: float, beta: float) -> float:
    """
    Representa el turno del "Mazo Malicioso" (Agente Min).
    El jugador acaba de elegir "hit". El mazo ahora elige la PEOR carta
    (de las 13 posibles) para dársela al jugador.
    """
    
    # --- Búsqueda Recursiva (Turno de Min) ---
    min_eval = math.inf

    for new_rank in range(1, 14):
        new_player_hand = player_hand + [new_rank]
        
        eval = _max_value(new_player_hand, dealer_hand, depth, alpha, beta)
        
        min_eval = min(min_eval, eval)
        beta = min(beta, min_eval) # Actualizar beta
        if beta <= alpha:
            break

    return min_eval

# --- Bloque de prueba ---
if __name__ == "__main__":
    from env.blackjack_env import BlackjackEnv, hand_value
    print("--- Prueba 1: Jugador 19 vs Dealer 18 ---")
    state1 = {
        "player": [10, 9],
        "dealer": [10, 8],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action1 = find_best_move(state1)
    print(f"Mano Jugador: {state1['player']} (Total: {hand_value(state1['player'])[0]})")
    print(f"Mano Dealer: {state1['dealer']} (Total: {hand_value(state1['dealer'])[0]})")
    print(f"Acción Minimax (Paranoica): {action1}") # Debería ser "stand"
    print("-" * 20)

    print("--- Prueba 2: Jugador 11 vs Dealer 17 ---")
    state2 = {
        "player": [5, 6, 7],
        "dealer": [10, 7],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action2 = find_best_move(state2)
    print(f"Mano Jugador: {state2['player']} (Total: {hand_value(state2['player'])[0]})")
    print(f"Mano Dealer: {state2['dealer']} (Total: {hand_value(state2['dealer'])[0]})")
    print(f"Acción Minimax (Paranoica): {action2}") 
    print("-" * 20)

    print("--- Prueba 3: Paranoia (Jugador 12 vs Dealer 4) ---")
    state3 = {
        "player": [2, 8],
        "dealer": [2, 8],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action3 = find_best_move(state3)
    print(f"Mano Jugador: {state3['player']} (Total: {hand_value(state3['player'])[0]})")
    print(f"Mano Dealer: {state3['dealer']} (Total: {hand_value(state3['dealer'])[0]})")
    print(f"Acción Minimax (Paranoica): {action3}") # Debería ser "stand"
    print("-" * 20)
    for i in range(21):
        for x in range(21):
            statex={
                "player": [i+x],
                "dealer": [x],
                "turn": "PLAYER", "done": False, "reward": 0
                }
            actionx = find_best_move(statex)
            if actionx!="stand":
                print("ola k ase?")