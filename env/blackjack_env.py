# blackjack_env.py
# Entorno simplificado de Blackjack (infinite deck) para uso con agentes minimax/expectimax.
# Configuración: 1 jugador vs 1 dealer, acciones: "hit" y "stand", dealer stands on 17+, push=0.

import random
from typing import List, Dict, Tuple, Optional

ACTIONS = ["hit", "stand"]

def card_value(rank: int) -> int:
    """Convierte rango 1..13 a valor de blackjack base (As inicial 11, figuras 10)."""
    if rank == 1:
        return 11
    if 2 <= rank <= 10:
        return rank
    return 10

def hand_value(cards: List[int]) -> Tuple[int, bool]:
    """
    Calcula el valor total de una mano aplicando la regla As tipo A:
    - Cada As cuenta como 11 inicialmente.
    - Si total > 21 y hay As, se convierte uno (por vez) de 11 -> 1 (resta 10) hasta dejar de bustear.
    Retorna (total, is_soft) donde is_soft indica que hay al menos un As contabilizado como 11.
    """
    original_total = sum(11 if r == 1 else (r if 2 <= r <= 10 else 10) for r in cards)
    total = original_total
    num_aces = sum(1 for r in cards if r == 1)

    # Ajustar ases mientras bust y queden ases que convertir
    conversions = 0
    while total > 21 and num_aces > 0:
        total -= 10
        num_aces -= 1
        conversions += 1

    # is_soft = había al menos un as originalmente y al menos uno sigue contando como 11
    had_aces = sum(1 for r in cards if r == 1) > 0
    is_soft = had_aces and conversions < sum(1 for r in cards if r == 1)
    return total, is_soft

def draw_card() -> int:
    """Modelo infinite deck: retorna un rank 1..13 con probabilidad uniforme 1/13."""
    return random.randint(1, 13)

class BlackjackEnv:
    """
    Entorno simplificado de Blackjack.
    Estado internamente: dict con keys 'player' (list ranks), 'dealer' (list ranks), 'done' (bool), 'reward' (int)
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.state: Dict = {}
        self.reset()

    def reset(self) -> Dict:
        """Reinicia el entorno: reparte 2 cartas a player y 2 al dealer. Devuelve estado inicial."""
        player = [draw_card(), draw_card()]
        dealer = [draw_card(), draw_card()]
        self.state = {
            "player": player,
            "dealer": dealer,
            "turn": "PLAYER",  # PLAYER | DEALER (dealer plays only after player stands or busts)
            "done": False,
            "reward": 0
        }
        # Si el jugador ya tiene blackjack natural (21 en dos cartas) podríamos tratarlo,
        # pero para simplicidad lo tratamos como mano normal en este entorno.
        return self.get_state()

    def get_state(self) -> Dict:
        """Devuelve una copia del estado actual (para que agentes lean sin modificar)."""
        # devuelve listas copiadas para evitar aliasing accidental
        return {
            "player": list(self.state["player"]),
            "dealer": list(self.state["dealer"]),
            "turn": self.state["turn"],
            "done": self.state["done"],
            "reward": self.state["reward"]
        }

    def legal_actions(self) -> List[str]:
        """Acciones legales si no está terminal y es turno del player."""
        if self.state["done"]:
            return []
        if self.state["turn"] == "PLAYER":
            return ACTIONS.copy()
        return []

    def step(self, action: str) -> Tuple[Dict, int, bool]:
        """
        Ejecuta la acción del jugador ('hit' o 'stand').
        Retorna: (next_state, reward, done)
        """
        assert not self.state["done"], "Episode already finished. Call reset()."
        assert self.state["turn"] == "PLAYER", "It's not player's turn."
        assert action in ACTIONS, f"Invalid action {action}"

        if action == "hit":
            self.state["player"].append(draw_card())
            total, _ = hand_value(self.state["player"])
            if total > 21:
                # player bust -> terminal, reward -1
                self.state["done"] = True
                self.state["reward"] = -1
                return self.get_state(), self.state["reward"], True
            else:
                # still player's turn
                return self.get_state(), 0, False

        elif action == "stand":
            # player stands -> dealer plays to completion, then resolve
            self.state["turn"] = "DEALER"
            self._dealer_play()
            self._resolve()
            return self.get_state(), self.state["reward"], self.state["done"]

    def _dealer_play(self):
        """Ejecuta la política fija del dealer: hit while total < 17, stand otherwise."""
        while True:
            total, _ = hand_value(self.state["dealer"])
            if total < 17:
                self.state["dealer"].append(draw_card())
            else:
                break

    def _resolve(self):
        """Compara manos y asigna reward y done."""
        player_total, _ = hand_value(self.state["player"])
        dealer_total, _ = hand_value(self.state["dealer"])

        # Si player bustearon ya se habría terminado antes; mantenemos la lógica robusta
        if player_total > 21:
            self.state["reward"] = -1
        elif dealer_total > 21:
            self.state["reward"] = +1
        else:
            if player_total > dealer_total:
                self.state["reward"] = +1
            elif player_total < dealer_total:
                self.state["reward"] = -1
            else:
                self.state["reward"] = 0  # push

        self.state["done"] = True
        self.state["turn"] = "TERMINAL"

    def render(self) -> None:
        """Imprime un resumen simple del estado (útil en debugging)."""
        p_total, p_soft = hand_value(self.state["player"])
        d_total, d_soft = hand_value(self.state["dealer"])
        print(f"PLAYER cards: {self.state['player']} -> total={p_total}{' (soft)' if p_soft else ''}")
        print(f"DEALER cards: {self.state['dealer']} -> total={d_total}{' (soft)' if d_soft else ''}")
        print(f"DONE: {self.state['done']}  REWARD: {self.state['reward']}  TURN: {self.state['turn']}")

if __name__ == "__main__":
    # Ejemplo de uso simple
    env = BlackjackEnv(seed=42)
    s = env.reset()
    print("Estado inicial:", s)
    # Ejemplo jugador pide una carta
    s, r, done = env.step("hit")
    print("Después hit:", s, r, done)
    if not done:
        # jugador decide plantarse
        s, r, done = env.step("stand")
        print("Después stand:", s, r, done)
    env.render()
