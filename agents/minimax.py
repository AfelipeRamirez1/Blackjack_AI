import sys
import os
import math
from typing import List, Dict, Tuple

# --- Hack para importar desde carpetas 'env' y 'agents' ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from env.blackjack_env import hand_value
    # Importamos nuestra heurística
    from agents.evaluation import get_stand_value
except ImportError:
    print("Error: No se pudo encontrar blackjack_env.py o evaluation.py.")
    print("Asegúrate de que la estructura de carpetas es correcta.")
    sys.exit(1)
# -------------------------------------------------

DEFAULT_MAX_DEPTH = 4

def find_best_move(state: Dict, max_depth: int = DEFAULT_MAX_DEPTH) -> str:
    """
    Función principal que inicia la búsqueda Minimax (versión simple, SIN poda).
    """
    player_hand = state["player"]
    dealer_hand = state["dealer"]
    
    # --- No hay inicialización de alpha y beta ---

    # --- 1. Evaluar la acción "stand" ---
    stand_eval = get_stand_value(player_hand, dealer_hand)
    
    # --- 2. Evaluar la acción "hit" ---
    # Llamamos a _min_value sin alpha y beta
    hit_eval = _min_value(player_hand, dealer_hand, max_depth - 1)

    # --- 3. Decisión Final ---
    if stand_eval >= hit_eval:
        return "stand"
    else:
        return "hit"

def _max_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el turno del jugador (Agente Max).
    Versión simple SIN poda alfa-beta.
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

    # 1. Evaluar "stand"
    stand_eval = get_stand_value(player_hand, dealer_hand)

    # 2. Evaluar "hit"
    # Llamamos a _min_value (sin alpha/beta)
    hit_eval = _min_value(player_hand, dealer_hand, depth - 1)

    # Max simplemente elige el MÁXIMO de sus dos opciones
    return max(stand_eval, hit_eval)

def _min_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el turno del "Mazo Malicioso" (Agente Min).
    Versión simple SIN poda alfa-beta.
    """
    
    min_eval = math.inf

    # Iteramos sobre *todos* los 13 rangos de cartas posibles
    # ¡NUNCA podremos "podar" o detenernos antes de tiempo!
    for new_rank in range(1, 14):
        new_player_hand = player_hand + [new_rank]
        
        # Llamamos a _max_value (sin alpha/beta)
        eval = _max_value(new_player_hand, dealer_hand, depth)
        
        min_eval = min(min_eval, eval)
        
        # --- No hay actualización de beta ---
        # --- No hay "if beta <= alpha: break" ---

    return min_eval

# --- Bloque de prueba ---
if __name__ == "__main__":
    from env.blackjack_env import BlackjackEnv, hand_value

    print("--- Probando Agente Minimax SIMPLE (Sin Poda) ---")

    # Prueba 1: Jugador 19 vs Dealer 18
    print("--- Prueba 1: Jugador 19 vs Dealer 18 ---")
    state1 = {
        "player": [10, 9],
        "dealer": [10, 8],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action1 = find_best_move(state1)
    print(f"Decisión: {action1}") # Debería ser "stand"
    print("-" * 20)

    # Prueba 2: Jugador 11 vs Dealer 17
    print("--- Prueba 2: Jugador 11 vs Dealer 17 ---")
    state2 = {
        "player": [5, 6],
        "dealer": [10, 7],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action2 = find_best_move(state2)
    print(f"Decisión: {action2}") # Debería ser "stand"
    print("-" * 20)

    # Prueba 3: Jugador 12 vs Dealer 4
    print("--- Prueba 3: Jugador 12 vs Dealer 4 ---")
    state3 = {
        "player": [2, 10],
        "dealer": [2, 2],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action3 = find_best_move(state3)
    print(f"Decisión: {action3}") # Debería ser "stand"
    print("-" * 20)