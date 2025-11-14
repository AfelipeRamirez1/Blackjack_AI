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
    hand_key = tuple(sorted(dealer_hand))
    
    if hand_key in dealer_cache:
        return dealer_cache[hand_key]

    total, _ = hand_value(dealer_hand)

    if total > 21:
        return {"bust": 1.0} 

    if total >= 17:
        return {total: 1.0} 

    final_outcome_probs: Dict[Union[int, str], float] = {}

    for new_rank in range(1, 14): 
        prob_of_this_rank = 1/13
        
        new_hand = dealer_hand + [new_rank]
        recursive_probs = compute_dealer_probabilities(new_hand)
        
        for final_score, prob in recursive_probs.items():
            current_prob = final_outcome_probs.get(final_score, 0)
            final_outcome_probs[final_score] = current_prob + (prob * prob_of_this_rank)

    dealer_cache[hand_key] = final_outcome_probs
    return final_outcome_probs

def get_stand_value(player_hand: List[int], dealer_hand: List[int]) -> float:
    """
    Calcula el Valor Esperado (EV) de PLANTARSE (stand) en un estado dado.
    
    EV = (P(Win) * 1) + (P(Lose) * -1) + (P(Push) * 0)
    """
    player_total, _ = hand_value(player_hand)

    if player_total > 21:
        return -1.0

    dealer_final_probs = compute_dealer_probabilities(dealer_hand)
    expected_value = 0.0
    for final_score, prob in dealer_final_probs.items():
        
        if final_score == "bust":

            expected_value += 1.0 * prob
        elif player_total > final_score:
 
            expected_value += 1.0 * prob
        elif player_total < final_score:
 
            expected_value += -1.0 * prob
        else:
            expected_value += 0.0 * prob
            
    return expected_value

# --- Bloque de prueba ---
if __name__ == "__main__":

    print("--- Prueba 1: Jugador 20 vs Dealer 18 (que se planta) ---")
    player_h = [10, 10]  
    dealer_h = [10, 8]   

    ev_1 = get_stand_value(player_h, dealer_h)
    print(f"Mano Jugador: {player_h} (Total: {hand_value(player_h)[0]})")
    print(f"Mano Dealer: {dealer_h} (Total: {hand_value(dealer_h)[0]})")
    print(f"Valor Esperado (EV) de plantarse: {ev_1:.4f}") # Debería ser 1.0
    print("-" * 20)

    print("--- Prueba 2: Jugador 18 vs Dealer 16 (debe pedir) ---")
    dealer_cache = {} 
    player_h = [10, 8]  
    dealer_h = [10, 6]   

    ev_2 = get_stand_value(player_h, dealer_h)
    print(f"Mano Jugador: {player_h} (Total: {hand_value(player_h)[0]})")
    print(f"Mano Dealer: {dealer_h} (Total: {hand_value(dealer_h)[0]})")
    print(f"Probabilidades de resultado del Dealer (desde 16):")
    print(dealer_cache[tuple(sorted(dealer_h))])
    print(f"Valor Esperado (EV) de plantarse: {ev_2:.4f}") 
    print("-" * 20)