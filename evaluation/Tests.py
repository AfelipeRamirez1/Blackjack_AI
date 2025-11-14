import sys
import os
import time
from collections import defaultdict

sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

try:
    from env.blackjack_env import BlackjackEnv
    from agents.minimax_agent_poda import find_best_move as find_minimax_move
    from agents.expectimax_agent import find_best_move as find_expectimax_move
    from agents.minimax import find_best_move as find_minimax_simple_move

except ImportError:
    print("Error: No se pudieron encontrar los módulos.")
    print("Asegúrate de que 'agents/minimax_simple_agent.py' existe.")
    print("Asegúrate de ejecutar desde la carpeta raíz del proyecto.")
    sys.exit(1)

def play_game(agent_move_function, env: BlackjackEnv, max_depth: int) -> int:
    """
    Simula una partida completa de Blackjack usando la función del agente dada.
    Retorna la recompensa final: +1 (gana), 0 (empate), -1 (pierde).
    """
    state = env.reset()
    done = False
    
    while not done:
        done = state["done"]
        
        if state["turn"] == "PLAYER":
            current_state_dict = env.get_state()
            
            action = agent_move_function(current_state_dict, max_depth)
            
            state, reward, done = env.step(action)
        
        elif state["turn"] == "DEALER" or state["turn"] == "TERMINAL":
            done = True
            
    return state["reward"]

def run_evaluation(agent_name: str, agent_function, env: BlackjackEnv, num_games: int, depth: int):
    """
    Ejecuta N partidas para un agente y reporta las estadísticas.
    """
    print(f"\n--- 🚀 Evaluando al Agente: {agent_name} ---")
    print(f"Número de partidas: {num_games} | Profundidad de búsqueda: {depth}")
    
    results = defaultdict(int) 
    start_time = time.time()
    print_every = max(1, num_games // 10)
    
    for i in range(num_games):
        if (i + 1) % print_every == 0:
            print(f"  ...partida {i + 1}/{num_games}")
            
        reward = play_game(agent_function, env, depth)
        results[reward] += 1

    end_time = time.time()
    total_time = end_time - start_time

    wins = results[1]
    pushes = results[0]
    losses = results[-1]
    
    win_rate = (wins / num_games) * 100
    push_rate = (pushes / num_games) * 100
    loss_rate = (losses / num_games) * 100

    print("\n--- 📊 Resultados ---")
    print(f"Victorias: {wins} ({win_rate:.2f}%)")
    print(f"Empates:   {pushes} ({push_rate:.2f}%)")
    print(f"Derrotas:  {losses} ({loss_rate:.2f}%)")
    print(f"\nJuegos por segundo: {num_games / total_time:.2f}")
    print(f"Tiempo total: {total_time:.2f} segundos")
    print("-" * 30)
    return {"wins": wins, "pushes": pushes, "losses": losses}


if __name__ == "__main__":

    N_GAMES_SIMPLE = 1000 
    N_GAMES_FAST = 10000 
    
    MAX_DEPTH = 4   
    # Inicializa el entorno una vez
    environment = BlackjackEnv()

    # --- Prueba 1: El Agente Simple (Lento) ---
    print("\n*** COMPARACIÓN DE EFICIENCIA (Tiempo) ***")
    run_evaluation(
        agent_name="Minimax SIMPLE (Sin Poda)",
        agent_function=find_minimax_simple_move,
        env=environment,
        num_games=N_GAMES_FAST, 
        depth=MAX_DEPTH
    )

    # --- Prueba 2: El Agente con Poda (Rápido) ---
    run_evaluation(
        agent_name="Minimax (Paranoico, Con Poda A-B)",
        agent_function=find_minimax_move,
        env=environment,
        num_games=N_GAMES_FAST, 
        depth=MAX_DEPTH
    )
    # --- Prueba 3: El Agente Racional ---
    print("\n*** COMPARACIÓN DE ESTRATEGIA (Victorias) ***")
    run_evaluation(
        agent_name="Expectimax (Racional)",
        agent_function=find_expectimax_move,
        env=environment,
        num_games=N_GAMES_FAST,
        depth=MAX_DEPTH
    )