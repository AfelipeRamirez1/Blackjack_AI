import sys
import os
import math
from typing import List, Dict, Tuple

# --- Hack para importar desde carpetas 'env' y 'agents' ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from env.blackjack_env import hand_value
    # Importamos nuestra misma heurística
    from agents.evaluation import get_stand_value
except ImportError:
    print("Error: No se pudo encontrar blackjack_env.py o evaluation.py.")
    print("Asegúrate de que la estructura de carpetas es correcta.")
    sys.exit(1)
# -------------------------------------------------

# Profundidad de búsqueda. Expectimax es más costoso, 
# así que una profundidad de 3-5 sigue siendo razonable.
DEFAULT_MAX_DEPTH = 4

# --- ¡LA CLAVE! ---
# Definimos las probabilidades de cada VALOR de carta
# OJO: RANGOS (1-13) vs VALORES (1-10)
# Rango 1 (As) -> Valor 1 (As) -> Prob 1/13
# Rango 2 -> Valor 2 -> Prob 1/13
# ...
# Rango 9 -> Valor 9 -> Prob 1/13
# Rango 10 -> Valor 10 -> Prob 1/13
# Rango 11 (J) -> Valor 10 -> Prob 1/13
# Rango 12 (Q) -> Valor 10 -> Prob 1/13
# Rango 13 (K) -> Valor 10 -> Prob 1/13
#
# En total, P(Valor 10) = 4/13
#
# Para la simulación, es más fácil iterar por RANGO (1-13)
# y asignar la probabilidad correcta a cada rango.

# (Rango, Probabilidad)
# Iteraremos por rangos 1-13
CARD_PROBABILITIES = [(rank, 1/13) for rank in range(1, 14)]
# (Esto es (1, 1/13), (2, 1/13), ..., (13, 1/13))


def find_best_move(state: Dict, max_depth: int = DEFAULT_MAX_DEPTH) -> str:
    """
    Función principal que inicia la búsqueda Expectimax.
    Decide entre 'hit' y 'stand'.
    """
    player_hand = state["player"]
    dealer_hand = state["dealer"]

    # --- 1. Evaluar la acción "stand" ---
    # El valor de "stand" es determinista, igual que antes.
    stand_eval = get_stand_value(player_hand, dealer_hand)
    
    # --- 2. Evaluar la acción "hit" ---
    # Llamamos a _expected_value para ver cuál es el valor
    # PROMEDIO de pedir carta.
    hit_eval = _expected_value(player_hand, dealer_hand, max_depth - 1)

    # --- 3. Decisión Final (Racional) ---
    # Compara el valor de plantarse vs el valor esperado de pedir
    if stand_eval >= hit_eval:
        return "stand"
    else:
        return "hit"

def _max_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el turno del jugador (Agente Max).
    Es idéntico al de Minimax, pero sin alpha/beta.
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
    # Llamamos a _expected_value, el "mazo estadístico"
    hit_eval = _expected_value(player_hand, dealer_hand, depth - 1)
        
    # Max elige el MÁXIMO de sus dos opciones
    return max(stand_eval, hit_eval)

def _expected_value(player_hand: List[int], dealer_hand: List[int], depth: int) -> float:
    """
    Representa el nodo de AZAR (Chance Node).
    Esto REEMPLAZA a _min_value.
    Calcula el valor esperado (promedio ponderado) de pedir "hit".
    """
    
    total_expected_value = 0.0

    # Iteramos sobre todas las 13 posibles cartas (As... Rey)
    # y su probabilidad asociada (1/13 para cada una).
    for rank, probability in CARD_PROBABILITIES:
        
        new_player_hand = player_hand + [rank]
        
        # Llamamos a _max_value para ver qué haría el jugador DESPUÉS
        # de recibir ESTA carta.
        # 'eval_of_this_branch' será el valor que Max obtenga de esa rama
        # (ej. si esta carta lo hace ganar, será +1.0)
        eval_of_this_branch = _max_value(new_player_hand, dealer_hand, depth)
        
        # Sumamos al total, ponderado por la probabilidad de esta carta
        total_expected_value += (eval_of_this_branch * probability)

    # El valor de este nodo es el promedio ponderado de todas sus ramas
    return total_expected_value

# --- Bloque de prueba ---
if __name__ == "__main__":
    from env.blackjack_env import BlackjackEnv, hand_value

    # ¡Usemos exactamente las mismas pruebas que en Minimax!

    # Prueba 1: Situación arriesgada
    # Jugador: 19 ([10, 9]), Dealer: 18 ([10, 8])
    # Agente Racional: "Stand" (+1.0) es mucho mejor que "Hit"
    # (que tiene alta prob. de pasarse). Debería "stand".
    print("--- Prueba 1: Jugador 19 vs Dealer 18 ---")
    state1 = {
        "player": [10, 10],
        "dealer": [10, 10],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action1 = find_best_move(state1)
    print(f"Mano Jugador: {state1['player']} (Total: {hand_value(state1['player'])[0]})")
    print(f"Mano Dealer: {state1['dealer']} (Total: {hand_value(state1['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action1}") # Debería ser "stand"
    print("-" * 20)

    # Prueba 2: ¡EL CASO CLAVE!
    # Jugador: 11 ([5, 6]), Dealer: 17 ([10, 7])
    # Minimax: Eligió "stand" (valor -1.0) porque temía un -1.0 de "hit".
    # Expectimax: "Stand" es -1.0. "Hit" es un promedio de
    # (4/13 * (+1)) + (1/13 * (+1)) ... (prob de As, etc)
    # El valor esperado de "hit" será MUY positivo. Debería "hit".
    print("--- Prueba 2: ¡¡Jugador 11 vs Dealer 17!! ---")
    state2 = {
        "player": [5, 6],
        "dealer": [10, 7],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action2 = find_best_move(state2)
    print(f"Mano Jugador: {state2['player']} (Total: {hand_value(state2['player'])[0]})")
    print(f"Mano Dealer: {state2['dealer']} (Total: {hand_value(state2['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action2}") # ¡¡Debería ser "hit"!!
    print("-" * 20)

    # Prueba 3: La prueba de fuego "paranoica"
    # Jugador: 12 ([2, 10]), Dealer: 4 ([2, 2])
    # Minimax: Eligió "stand" porque temía un 10 (valor -1.0).
    # Expectimax: "Stand" (valor > -1.0) vs "Hit" (un promedio).
    # "Hit" tiene 4/13 de prob de sacar un 10 (bust, -1.0), 
    # pero 9/13 de prob de mejorar (As-9).
    # El agente calculará si (4/13 * -1) + (9/13 * (valor_mejorado)) > stand_eval
    print("--- Prueba 3: Jugador 12 vs Dealer 4 ---")
    state3 = {
        "player": [2, 10],
        "dealer": [2, 2],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action3 = find_best_move(state3)
    print(f"Mano Jugador: {state3['player']} (Total: {hand_value(state3['player'])[0]})")
    print(f"Mano Dealer: {state3['dealer']} (Total: {hand_value(state3['dealer'])[0]})")
    print(f"Acción Expectimax (Racional): {action3}") # La estrategia básica es "hit"
    print("-" * 20)