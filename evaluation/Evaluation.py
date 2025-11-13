import sys
import os
import time
from collections import defaultdict

# --- Hack para importar desde las carpetas del proyecto ---
sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

try:
    from env.blackjack_env import BlackjackEnv
    # Importamos las funciones "find_best_move" de cada agente
    # y les cambiamos el nombre para que no choquen.
    from agents.minimax_agent import find_best_move as find_minimax_move
    from agents.expectimax_agent import find_best_move as find_expectimax_move
except ImportError:
    print("Error: No se pudieron encontrar los módulos.")
    print("Asegúrate de ejecutar desde la carpeta raíz del proyecto.")
    sys.exit(1)
# -------------------------------------------------

def play_game(agent_move_function, env: BlackjackEnv, max_depth: int) -> int:
    """
    Simula una partida completa de Blackjack usando la función del agente dada.
    Retorna la recompensa final: +1 (gana), 0 (empate), -1 (pierde).
    """
    state = env.reset()
    done = False
    
    while not done:
        # El estado nos dice si el juego ha terminado
        done = state["done"]
        
        if state["turn"] == "PLAYER":
            # 1. Obtener el estado actual
            current_state_dict = env.get_state()
            
            # 2. Pedir al agente que decida la acción
            action = agent_move_function(current_state_dict, max_depth)
            
            # 3. Ejecutar la acción en el entorno
            state, reward, done = env.step(action)
        
        elif state["turn"] == "DEALER" or state["turn"] == "TERMINAL":
            # El turno del dealer se maneja automáticamente dentro de
            # env.step("stand") o si el jugador se pasa.
            # Así que si llegamos aquí, el juego ya terminó.
            done = True
            
    # Devuelve la recompensa final de la partida
    return state["reward"]

def run_evaluation(agent_name: str, agent_function, env: BlackjackEnv, num_games: int, depth: int):
    """
    Ejecuta N partidas para un agente y reporta las estadísticas.
    """
    print(f"\n--- 🚀 Evaluando al Agente: {agent_name} ---")
    print(f"Número de partidas: {num_games} | Profundidad de búsqueda: {depth}")
    
    results = defaultdict(int) # {1: 0, 0: 0, -1: 0}
    start_time = time.time()

    for i in range(num_games):
        if (i + 1) % (num_games // 10) == 0:
            print(f"  ...partida {i + 1}/{num_games}")
            
        reward = play_game(agent_function, env, depth)
        results[reward] += 1

    end_time = time.time()
    total_time = end_time - start_time

    # Calcular estadísticas
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
    
    # Esto es para tu reporte
    return {"wins": wins, "pushes": pushes, "losses": losses}


if __name__ == "__main__":
    
    N_GAMES = 10000  # Empieza con 1000, luego súbelo a 10,000 o más para el reporte
    MAX_DEPTH = 4   # La profundidad que definiste en tus agentes
    
    # Inicializa el entorno una vez
    environment = BlackjackEnv()

    # --- Prueba 1: El Agente Paranoico ---
    # (Esperamos ver un rendimiento... interesante)
    run_evaluation(
        agent_name="Minimax (Paranoico)",
        agent_function=find_minimax_move,
        env=environment,
        num_games=N_GAMES,
        depth=MAX_DEPTH
    )

    # --- Prueba 2: El Agente Racional ---
    # (Esperamos ver un rendimiento mucho mejor)
    run_evaluation(
        agent_name="Expectimax (Racional)",
        agent_function=find_expectimax_move,
        env=environment,
        num_games=N_GAMES,
        depth=MAX_DEPTH
    )