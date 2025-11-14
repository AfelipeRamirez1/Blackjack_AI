# Proyecto 2: Búsqueda Multiagente
## Minimax vs. Expectimax en Blackjack

Este proyecto implementa y compara dos algoritmos de búsqueda multiagente (Minimax y Expectimax) para tomar decisiones en un entorno simulado del juego de cartas **Blackjack**.

El objetivo es analizar cómo cada algoritmo modela la **incertidumbre** (la siguiente carta del mazo) y cómo ese modelo (adversario vs. estocástico) afecta fundamentalmente la estrategia de juego.

---

### 🃏 El Problema: Blackjack

El Blackjack es un juego de cartas donde el objetivo es obtener una puntuación lo más cercana posible a 21, sin pasarse, y superar la puntuación del *dealer* (la casa).

#### Reglas del Entorno

Este proyecto utiliza un entorno simplificado con las siguientes reglas:
* **Juego:** 1 jugador (el agente) vs. 1 *dealer*.
* **Mazo:** Se utiliza un **mazo infinito**. Esto significa que la probabilidad de robar cualquier carta (ej. un As o un 10) es siempre la misma, sin importar cuántas se hayan repartido.
* **Acciones del Jugador:** El agente solo puede elegir entre "hit" (pedir una carta más) o "stand" (plantarse con su mano actual).
* **Reglas del Dealer:** El *dealer* sigue una política fija y no es un agente inteligente. Siempre pide carta (`hit`) si su mano suma 16 o menos, y siempre se planta (`stand`) si suma 17 o más.



---

### 🧠 Los Agentes: Modelando la Incertidumbre

El núcleo del proyecto es comparar dos "cerebros" (agentes) que abordan el azar de formas opuestas.

#### 1. Agente Minimax

Este agente trata el juego como una batalla de 2 jugadores adversarios:
* **Agente Max:** Es nuestro jugador, que intenta **maximizar** su puntuación.
* **Agente Min:** Es el **mazo de cartas**. Modelamos el mazo como un oponente malicioso que intenta **minimizar** la puntuación del jugador.

**La Lógica:** Cuando el jugador (Max) considera pedir "hit", el algoritmo asume que el mazo (Min) elegirá, de entre las 13 cartas posibles, aquella que le dé el **peor resultado posible** al jugador. Este agente juega asumiendo que el universo está activamente en su contra.

#### 2. Agente Expectimax

Este agente trata el juego como lo que es: un jugador contra el azar.
* **Agente Max:** Es nuestro jugador, que intenta **maximizar** su puntuación.
* **Nodo de Azar (Chance):** Es el **mazo de cartas**. No es un oponente, sino un evento probabilístico.

**La Lógica:** Cuando el jugador (Max) considera pedir "hit", el algoritmo no asume lo peor. En su lugar, calcula el **valor esperado** de la jugada. Suma los resultados de *todas* las 13 posibles cartas, pero pondera cada resultado por su probabilidad real (ej. P(Valor 10) = 4/13, P(As) = 1/13, etc.). Este agente juega usando estadística.

---

### 📁 Estructura del Repositorio

El proyecto está organizado de la siguiente manera:

```
├── agents/
│   ├── evaluation.py         # Heurística (cálculo de P(Win) vs dealer)
│   ├── minimax.py            # Agente Minimax SIMPLE (sin poda)
│   ├── minimax_agent_poda.py # Agente Minimax (con poda Alfa-Beta)
│   └── expectimax_agent.py   # Agente Racional (Expectimax)
│
├── env/
│   └── blackjack_env.py      # El entorno del juego (reglas, estado, mazo infinito)
│
├── evaluation/
│   └── Tests.py              # Script principal para correr simulaciones
│
└── README.md               
```

---

