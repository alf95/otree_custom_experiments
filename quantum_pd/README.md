# quantum_pd — Quantum Prisoner's Dilemma app

Implements a single-player-vs-bot **Quantum Prisoner's Dilemma** using the
**EWL (Eisert–Wilkens–Lewenstein)** protocol.

## Game flow

| Page             | Purpose                                                        |
|------------------|----------------------------------------------------------------|
| `DecisionPage`   | Human picks θ ∈ [0, π] and φ ∈ [0, π/2] via sliders            |
| `ResultsWaitPage`| Runs `simulate()`: bot move + EWL simulation + payoff          |
| `ResultsPage`    | Shows strategies, outcome probabilities, sampled outcome, points |

The bot is virtual: `PLAYERS_PER_GROUP = 1`, so each group contains only the
human. The bot move and the quantum simulation run in `simulate()` (the
WaitPage's `after_all_players_arrive` hook).

## Quantum protocol (EWL)

A single-qubit strategy is the SU(2) matrix

```
U(θ, φ) = | e^{iφ}·cos(θ/2)       sin(θ/2)   |
          | -sin(θ/2)      e^{-iφ}·cos(θ/2)  |
```

Special moves:

| Move            | Angles     | Matrix `U`            |
|-----------------|------------|-----------------------|
| Cooperate (C)   | θ=0, φ=0   | `I` (identity)        |
| Defect (D)      | θ=π, φ=0   | `[[0,1],[-1,0]]`      |
| Quantum (Q)     | θ=0, φ=π/2 | `[[i,0],[0,-i]]`      |

The entangling operator is built from the *same* defect operator `D = U(π, 0)`:

```
J = cos(γ/2)·I⊗I  +  i·sin(γ/2)·D⊗D        (γ = π/2 → Bell state)
```

The circuit is:

```
|ψ_f⟩ = J† · (U_h ⊗ U_b) · J · |00⟩
```

with `U_h` the human's strategy (first qubit) and `U_b` the bot's (second
qubit). Measuring `|ψ_f⟩` in the computational basis gives the probabilities
`P_CC, P_CD, P_DC, P_DD`. This convention reproduces the classical PD and the
quantum "miracle move": `(Q, Q) → |CC⟩` with payoff `(3, 3)`.

## Payoff matrix (classical PD)

First qubit = human, second = bot; `0` = cooperate, `1` = defect.

| Outcome   | Human | Bot |
|-----------|-------|-----|
| `CC` (00) | 3     | 3   |
| `CD` (01) | 0     | 5   |
| `DC` (10) | 5     | 0   |
| `DD` (11) | 1     | 1   |

The backend computes both the **expected payoff** (weighted average over the
four probabilities) and the **actual round payoff** (from a single outcome
sampled with `random.choices` using the four probabilities as weights).

## Bot strategies

Selected via `session.config['bot_strategy']`.

| Strategy                     | Behaviour                                             |
|------------------------------|-------------------------------------------------------|
| `always_classical_cooperate` | `U(0, 0)` every round                                  |
| `always_classical_defect`    | `U(π, 0)` every round                                  |
| `always_quantum`             | `Q = U(0, π/2)` every round                            |
| `random`                     | θ ~ U(0, π), φ ~ U(0, π/2) each round                  |
| `tit_for_tat`                | Copies previous-round human θ, φ; cooperates in round 1 |

## Data model

`Player` fields (exported in the oTree data):

| Field                | Type    | Meaning                                          |
|----------------------|---------|--------------------------------------------------|
| `theta`, `phi`       | Float   | Human's chosen angles (form inputs)              |
| `bot_strategy`       | String  | Bot strategy key from the session config         |
| `bot_theta`, `bot_phi` | Float | Bot's angles for the round                       |
| `prob_cc` … `prob_dd` | Float  | Probabilities of the four classical outcomes     |
| `outcome`            | String  | Sampled outcome (`CC`, `CD`, `DC`, `DD`)         |
| `payoff_round`       | Float   | Human's points this round                        |
| `bot_payoff`         | Float   | Bot's points this round                          |
| `expected_payoff`    | Float   | Human's expected payoff                          |
| `expected_bot_payoff`| Float   | Bot's expected payoff                            |

## Constants (`C`)

| Constant        | Value    | Meaning                            |
|-----------------|----------|------------------------------------|
| `NUM_ROUNDS`    | 5        | Rounds per session                 |
| `PLAYERS_PER_GROUP` | 1    | Human only (bot is virtual)        |
| `GAMMA`         | π/2      | Entanglement parameter (maximal)   |
| `PAYOFF_CC` … `PAYOFF_DD` | 3, 0, 5, 1 | Classical payoff values   |
