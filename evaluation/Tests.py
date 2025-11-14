import sys
import os
import time
from collections import defaultdict

sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Error: La biblioteca 'matplotlib' no está instalada.")
    print("Por favor, instálala ejecutando: pip install matplotlib")
    sys.exit(1)

try:
    from env.blackjack_env import BlackjackEnv
    from agents.minimax_agent_poda import find_best_move as find_minimax_poda_move
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
    games_per_second = num_games / total_time if total_time > 0 else float('inf')
    print("\n--- 📊 Resultados ---")
    print(f"Victorias: {wins} ({win_rate:.2f}%)")
    print(f"Empates:   {pushes} ({push_rate:.2f}%)")
    print(f"Derrotas:  {losses} ({loss_rate:.2f}%)")
    print(f"\nJuegos por segundo: {num_games / total_time:.2f}")
    print(f"Tiempo total: {total_time:.2f} segundos")
    print("-" * 30)
    return {
            "wins": wins, 
            "pushes": pushes, 
            "losses": losses, 
            "win_rate": win_rate,
            "total_time": total_time, 
            "games_per_second": games_per_second
        }
def plot_strategy_comparison(results_dict):
    """
    Genera una gráfica de barras comparando la tasa de victorias
    del agente Minimax (con poda) vs. Expectimax.
    """
    print("\nGenerando gráfica de estrategia (victorias)...")
    
    # Nombres de los agentes para la gráfica
    agents = ['Minimax (Con Poda A-B)', 'Expectimax']
    
    # Extraer las tasas de victoria
    try:
        win_rates = [
            results_dict['Minimax (Paranoico, Con Poda A-B)']['win_rate'],
            results_dict['Expectimax (Racional)']['win_rate']
        ]
    except KeyError as e:
        print(f"Error: No se encontró la clave {e} en los resultados. Asegúrate de que los agentes se ejecutaron.")
        return
        
    colors = ['salmon', 'lightblue']
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(agents, win_rates, color=colors)
    plt.ylabel('Tasa de Victorias (%)')
    plt.title('Comparación de Estrategia: Minimax vs. Expectimax')
    plt.ylim(0, 50) # Asumimos que no superará el 50%
    
    # Añadir etiquetas de valor
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval:.2f}%', ha='center', va='bottom')

    # Guardar la gráfica como un archivo PNG
    try:
        plt.savefig('grafica_comparacion_estrategia.png')
        print("Gráfica guardada como 'grafica_comparacion_estrategia.png'")
    except Exception as e:
        print(f"Error al guardar la gráfica de estrategia: {e}")

def plot_efficiency_comparison(results_dict):
    """
    Genera una gráfica de barras comparando la eficiencia (Juegos por Segundo)
    del Minimax Simple vs. Minimax con Poda.
    """
    print("\nGenerando gráfica de eficiencia (velocidad)...")
    
    # Nombres de los agentes para la gráfica
    agents = ['Minimax SIMPLE (Sin Poda)', 'Minimax (Con Poda A-B)']
    
    # Extraer los juegos por segundo
    try:
        games_per_sec = [
            results_dict['Minimax SIMPLE (Sin Poda)']['games_per_second'],
            results_dict['Minimax (Paranoico, Con Poda A-B)']['games_per_second']
        ]
    except KeyError as e:
        print(f"Error: No se encontró la clave {e} en los resultados. Asegúrate de que los agentes se ejecutaron.")
        return
        
    colors = ['firebrick', 'forestgreen']
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(agents, games_per_sec, color=colors)
    plt.ylabel('Juegos por Segundo (Más es mejor)')
    plt.title('Comparación de Eficiencia: Poda Alfa-Beta')
    
    # Usar escala logarítmica si la diferencia es muy grande
    try:
        if games_per_sec[1] / games_per_sec[0] > 10:
            plt.yscale('log')
            plt.ylabel('Juegos por Segundo (Escala Logarítmica)')
    except ZeroDivisionError:
        pass # Evitar error si el simple es extremadamente lento (0 g/s)

    # Añadir etiquetas de valor
    for bar in bars:
        yval = bar.get_height()
        # Ajuste para escala logarítmica
        if plt.gca().get_yscale() == 'log':
            plt.text(bar.get_x() + bar.get_width()/2.0, yval * 1.1, f'{yval:.2f}', ha='center', va='bottom')
        else:
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + (yval * 0.05), f'{yval:.2f}', ha='center', va='bottom')

    # Guardar la gráfica como un archivo PNG
    try:
        plt.savefig('grafica_comparacion_eficiencia.png')
        print("Gráfica guardada como 'grafica_comparacion_eficiencia.png'")
    except Exception as e:
        print(f"Error al guardar la gráfica de eficiencia: {e}")


if __name__ == "__main__":

    N_GAMES_SIMPLE = 10000 

    N_GAMES_FAST = 10000 

    MAX_DEPTH = 4   

    environment = BlackjackEnv()

    # --- Diccionario para guardar todos los resultados ---
    all_results = {}

    # --- Prueba 1: El Agente Simple (Lento) ---
    print("\n*** COMPARACIÓN DE EFICIENCIA (Tiempo) ***")
    all_results["Minimax SIMPLE (Sin Poda)"] = run_evaluation(
    agent_name="Minimax SIMPLE (Sin Poda)",
    agent_function=find_minimax_simple_move,
    env=environment,
    num_games=N_GAMES_SIMPLE, # <-- Nivel de juegos BAJO
    depth=MAX_DEPTH
    )

    # --- Prueba 2: El Agente con Poda (Rápido) ---
    all_results["Minimax (Paranoico, Con Poda A-B)"] = run_evaluation(
    agent_name="Minimax (Paranoico, Con Poda A-B)",
    agent_function=find_minimax_poda_move,
    env=environment,
    num_games=N_GAMES_FAST, # <-- Nivel de juegos ALTO
    depth=MAX_DEPTH
    )

    # --- Prueba 3: El Agente Racional ---
    print("\n*** COMPARACIÓN DE ESTRATEGIA (Victorias) ***")
    all_results["Expectimax (Racional)"] = run_evaluation(
    agent_name="Expectimax (Racional)",
    agent_function=find_expectimax_move,
    env=environment,
    num_games=N_GAMES_FAST, # <-- Nivel de juegos ALTO
    depth=MAX_DEPTH
    )

    print("\n\n*** Generando Gráficas del Reporte ***")
    plot_strategy_comparison(all_results)
    plot_efficiency_comparison(all_results)
    print("\n¡Evaluación completada! Revisa los archivos .png generados.")