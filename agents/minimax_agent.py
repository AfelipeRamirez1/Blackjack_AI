import sys
import os
import math
from typing import List, Dict, Tuple

# --- Hack para importar desde carpetas 'env' y 'agents' ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from env.blackjack_env import hand_value
    # Importamos nuestra heurística desde el archivo 'evaluation' en esta misma carpeta
    from agents.evaluation import get_stand_value
except ImportError:
    print("Error: No se pudo encontrar blackjack_env.py o evaluation.py.")
    print("Asegúrate de que la estructura de carpetas es correcta y estás ejecutando desde la raíz.")
    sys.exit(1)
# -------------------------------------------------

# Definimos una profundidad máxima de búsqueda para que el algoritmo termine.
# Esto representa cuántas cartas "hit" está dispuesto a simular.
# Un valor de 3-5 es razonable para este problema.
DEFAULT_MAX_DEPTH = 4

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
    # El valor de "stand" es determinista: usamos nuestra heurística.
    stand_eval = get_stand_value(player_hand, dealer_hand)
    
    # Actualizamos 'alpha' (lo mejor que Max puede conseguir) con este valor.
    alpha = max(alpha, stand_eval)
    
    # --- 2. Evaluar la acción "hit" ---
    # El valor de "hit" es incierto. Llamamos a _min_value para ver qué
    # haría el "mazo malicioso" si pedimos carta.
    # Restamos 1 a la profundidad porque estamos usando una acción "hit".
    hit_eval = _min_value(player_hand, dealer_hand, max_depth - 1, alpha, beta)

    # --- 3. Decisión Final ---
    # Compara el valor garantizado de "stand" vs. el valor "paranoico" de "hit"
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
    # El "mazo" nos dio una carta que nos hizo perder. Valor -1.
    if player_total > 21:
        return -1.0
    
    # 2. Se alcanzó la profundidad máxima de búsqueda
    # Ya no simulamos más "hits". Forzamos un "stand" y usamos la heurística.
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

    # Iteramos sobre *todos* los 13 rangos de cartas posibles (As... Rey)
    # El mazo paranoico asumirá que puede elegir CUALQUIERA de ellas.
    for new_rank in range(1, 14):
        new_player_hand = player_hand + [new_rank]
        
        # Llamamos a _max_value para ver qué haría el jugador DESPUÉS
        # de recibir esta carta maliciosa.
        eval = _max_value(new_player_hand, dealer_hand, depth, alpha, beta)
        
        min_eval = min(min_eval, eval)
        beta = min(beta, min_eval) # Actualizar beta

        # --- Poda Alfa-Beta ---
        # Si beta (lo peor que Min puede forzar) es menor o igual
        # que alpha (lo mejor que Max ya tiene asegurado en otra rama),
        # Max NUNCA elegirá esta rama. Dejamos de buscar.
        if beta <= alpha:
            break

    return min_eval

# --- Bloque de prueba ---
if __name__ == "__main__":
    # Importamos el entorno para poder crear estados de prueba
    from env.blackjack_env import BlackjackEnv, hand_value

    # Prueba 1: Situación muy arriesgada
    # Jugador: 19 (ej. [10, 9]), Dealer: 18 (ej. [10, 8])
    # El agente "paranoico" teme que si pide "hit", el mazo le dará un 3+
    # (y lo hará perder o empatar en el mejor caso). Debería "stand".
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

    # Prueba 2: Situación clara para pedir
    # Jugador: 11 (ej. [5, 6]), Dealer: 17 (ej. [10, 7])
    # Es imposible pasarse (bust). El agente sabe que "hit" no puede
    # ser peor que "stand" (que perdería).
    print("--- Prueba 2: Jugador 11 vs Dealer 17 ---")
    state2 = {
        "player": [5, 6, 7],
        "dealer": [10, 7],
        "turn": "PLAYER", "done": False, "reward": 0
    }
    action2 = find_best_move(state2)
    print(f"Mano Jugador: {state2['player']} (Total: {hand_value(state2['player'])[0]})")
    print(f"Mano Dealer: {state2['dealer']} (Total: {hand_value(state2['dealer'])[0]})")
    print(f"Acción Minimax (Paranoica): {action2}") # Debería ser "hit"
    print("-" * 20)

    # Prueba 3: La prueba de fuego de la "paranoia"
    # Jugador: 12 (ej. [2, 10]), Dealer: 4 (ej. [2, 2])
    # Estrategia básica: "stand".
    # Agente paranoico: Si pido "hit", el mazo ME DARÁ un 10 (total 22) y pierdo.
    # Por lo tanto, el valor de "hit" es -1.
    # El valor de "stand" (según la heurística) será mucho mejor que -1.
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