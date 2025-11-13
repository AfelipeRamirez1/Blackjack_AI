import sys
import os
from typing import List, Dict, Tuple, Union


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from env.blackjack_env import hand_value
except ImportError:
    print("Error: No se pudo encontrar blackjack_env.py. Asegúrate de que la estructura de carpetas es correcta.")
    sys.exit(1)
# -------------------------------------------------


dealer_cache: Dict[Tuple[int, ...], Dict[Union[int, str], float]] = {}

def compute_dealer_probabilities(dealer_hand: List[int]) -> Dict[Union[int, str], float]:
    """
    Calcula recursivamente las probabilidades de todos los posibles resultados
    finales del dealer (puntuación 17-21 o "bust").
    Usa memoization (dealer_cache) para ser eficiente.
    """
    # Usar una tupla ordenada como clave para el caché
    hand_key = tuple(sorted(dealer_hand))
    
    # Si ya hemos calculado esto, devolverlo del caché
    if hand_key in dealer_cache:
        return dealer_cache[hand_key]

    total, _ = hand_value(dealer_hand)

    # --- Casos Base (Recursión termina) ---
    
    # 1. El dealer se pasa (Bust)
    if total > 21:
        return {"bust": 1.0}  # 100% de probabilidad de este resultado

    # 2. El dealer se planta (Stand)
    if total >= 17:
        # El dealer termina con esta puntuación
        return {total: 1.0}  # 100% de probabilidad de este resultado

    # --- Caso Recursivo (Dealer pide carta - Hit) ---
    # Si total < 17, el dealer DEBE pedir.
    
    # Este diccionario acumulará las probabilidades de los resultados finales
    # (ej. {17: 0.1, 18: 0.1, ..., "bust": 0.3})
    final_outcome_probs: Dict[Union[int, str], float] = {}

    # Iteramos sobre todas las 13 posibles cartas (rangos 1-13)
    for new_rank in range(1, 14): # De 1 (As) a 13 (Rey)
        prob_of_this_rank = 1/13
        
        new_hand = dealer_hand + [new_rank]
        
        # Llamada recursiva: ¿Qué pasa desde esa *nueva* mano?
        recursive_probs = compute_dealer_probabilities(new_hand)
        
        # Agregamos los resultados de esa rama, ponderados por su probabilidad
        for final_score, prob in recursive_probs.items():
            current_prob = final_outcome_probs.get(final_score, 0)
            final_outcome_probs[final_score] = current_prob + (prob * prob_of_this_rank)

    # Guardar en caché y devolver
    dealer_cache[hand_key] = final_outcome_probs
    return final_outcome_probs

def get_stand_value(player_hand: List[int], dealer_hand: List[int]) -> float:
    """
    Calcula el Valor Esperado (EV) de PLANTARSE (stand) en un estado dado.
    
    EV = (P(Win) * 1) + (P(Lose) * -1) + (P(Push) * 0)
    """
    player_total, _ = hand_value(player_hand)

    # Si el jugador ya se pasó, el valor de este estado es -1 (no debería pasar
    # si la heurística se llama desde "stand", pero es bueno manejarlo).
    if player_total > 21:
        return -1.0

    # 1. Obtener el diccionario de probabilidades de los finales del dealer
    dealer_final_probs = compute_dealer_probabilities(dealer_hand)

    # 2. Calcular el Valor Esperado (EV)
    expected_value = 0.0
    for final_score, prob in dealer_final_probs.items():
        
        if final_score == "bust":
            # Dealer se pasa, jugador gana
            expected_value += 1.0 * prob
        elif player_total > final_score:
            # Jugador tiene mejor puntuación, jugador gana
            expected_value += 1.0 * prob
        elif player_total < final_score:
            # Dealer tiene mejor puntuación, jugador pierde
            expected_value += -1.0 * prob
        else:
            # Empate (push), el valor es 0
            expected_value += 0.0 * prob
            
    return expected_value

# --- Bloque de prueba ---
if __name__ == "__main__":
    # Puedes ejecutar este archivo directamente (python agents/evaluation.py)
    # para probar la lógica.
    
    # Prueba 1: Jugador tiene 20. Dealer muestra un 8.
    # (El dealer tiene [8], pero para la simulación necesitamos una mano completa)
    # Asumamos que la carta visible del dealer es un 8, y la oculta un 10 (total 18).
    print("--- Prueba 1: Jugador 20 vs Dealer 18 (que se planta) ---")
    player_h = [10, 10]  # 20
    dealer_h = [10, 8]   # 18
    # Dealer tiene 18, se planta. P(18) = 1.0.
    # EV = P(player > dealer) * 1 = 1.0 * 1 = 1
    ev_1 = get_stand_value(player_h, dealer_h)
    print(f"Mano Jugador: {player_h} (Total: {hand_value(player_h)[0]})")
    print(f"Mano Dealer: {dealer_h} (Total: {hand_value(dealer_h)[0]})")
    print(f"Valor Esperado (EV) de plantarse: {ev_1:.4f}") # Debería ser 1.0
    print("-" * 20)

    # Prueba 2: Jugador tiene 18. Dealer muestra un 6 (y tiene 10 oculto, total 16).
    print("--- Prueba 2: Jugador 18 vs Dealer 16 (debe pedir) ---")
    # Limpiamos el caché para una prueba limpia
    dealer_cache = {} 
    player_h = [10, 8]  # 18
    dealer_h = [10, 6]   # 16
   
    ev_2 = get_stand_value(player_h, dealer_h)
    print(f"Mano Jugador: {player_h} (Total: {hand_value(player_h)[0]})")
    print(f"Mano Dealer: {dealer_h} (Total: {hand_value(dealer_h)[0]})")
    print(f"Probabilidades de resultado del Dealer (desde 16):")
    print(dealer_cache[tuple(sorted(dealer_h))])
    print(f"Valor Esperado (EV) de plantarse: {ev_2:.4f}") # Será un valor calculado
    print("-" * 20)