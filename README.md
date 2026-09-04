# Quantum Prisoner's Dilemma (EWL protocol)

An [oTree](https://www.otree.org/) experiment implementing the **Quantum
Prisoner's Dilemma** based on the **Eisert–Wilkens–Lewenstein (EWL) protocol**.

A single human participant plays against a configurable **bot** (computer).
The human chooses two continuous parameters — **Theta (θ)** and **Phi (φ)** —
that define a unitary strategy `U(θ, φ)` applied to their qubit. The two qubits
are maximally entangled and measured, yielding the classical outcomes
`|CC⟩, |CD⟩, |DC⟩, |DD⟩` with quantum probabilities.

## Guida per lo sperimentatore (nessuna fisica richiesta)

L'esperimento fa giocare una persona contro un **bot** (avversario controllato
dal computer) al **Dilemma del Prigioniero**: in ogni round il partecipante e il
bot possono "cooperare" o "tradire", e i punti dipendono dalla combinazione
delle due scelte.

### Come si avvia

```bash
pip install -r requirements.txt
otree devserver
```

Apri <http://localhost:8000>: nella pagina iniziale trovi le 5 condizioni
sperimentali gia' pronte. Scegline una in base al comportamento del bot:

| Sessione (condizione)              | Cosa fa il bot                                    |
|------------------------------------|---------------------------------------------------|
| Bot: coopera sempre                | Non tradisce mai                                  |
| Bot: tradisce sempre               | Tradisce a ogni round                             |
| Bot: mossa speciale                | Usa la strategia ottimale del gioco quantistico   |
| Bot: casuale                       | Sceglie a caso a ogni round                       |
| Bot: tit-for-tat (imita)           | Copia la scelta del round precedente              |

> Non devi spiegare ai partecipanti nulla di fisica: le istruzioni a schermo
> sono gia' in italiano e il partecipante muove semplicemente due cursori.

### Consigli pratici

- Assegna ogni partecipante a **una sola** condizione (una sola sessione).
- Per confrontare le condizioni, crea una sessione per ciascuna e confronta i
  risultati: trovi i dati nella scheda **Data** (export CSV/Excel) del pannello
  di amministrazione.
- Le variabili esportate piu' utili sono `payoff` (punti totali del
  partecipante) e `outcome` (esito di ogni round: `CC`, `CD`, `DC`, `DD`).
- Per cambiare il numero di round o i punti delle quattro combinazioni, apri
  `quantum_pd/__init__.py` e modifica i valori nella classe `C` (trovi i
  commenti in italiano). Non toccare `GAMMA`.

## Requirements

- Python 3.9+
- oTree 5+ (recommended: 5.10 or 6.0)
- numpy

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
otree devserver
```

Then open <http://localhost:8000> and pick one of the session configurations
from the demo page, or create a session from the **Sessions** tab.

## Project structure

```
quantum_pgg/
├── settings.py              # Session configurations (one per bot strategy)
├── requirements.txt         # otree, numpy
└── quantum_pd/              # The experiment app
    ├── __init__.py          # Models, EWL math, bot logic, pages
    ├── DecisionePage.html   # Theta/Phi sliders with live preview
    └── ResultsPage.html     # Outcome probabilities and round payoffs
```

## Session configurations

Each session config sets the `bot_strategy` custom key, read in the backend via
`session.config['bot_strategy']`.

| `bot_strategy`               | Bot behaviour                                          |
|------------------------------|--------------------------------------------------------|
| `always_classical_cooperate` | Always plays the classical cooperate move `U(0, 0)`    |
| `always_classical_defect`    | Always plays the classical defect move `U(π, 0)`       |
| `always_quantum`             | Always plays the quantum move `Q = U(0, π/2)`          |
| `random`                     | Draws θ ∈ [0, π] and φ ∈ [0, π/2] uniformly each round |
| `tit_for_tat`                | Copies the human's previous-round angles (round 1 = cooperate) |

## The game

1. The human picks **θ ∈ [0, π]** and **φ ∈ [0, π/2]** on the decision page.
2. The bot plays its strategy; both strategies are applied to the entangled pair.
3. The system is measured, an outcome is sampled, and round payoffs are computed.
4. The result page shows the four outcome probabilities, the sampled outcome,
   and the points earned.

For the full protocol math and data model, see
[`quantum_pd/README.md`](quantum_pd/README.md).

---

# Public Goods Game - "Back to the Future"

The same project also ships a second app, `bttf_pgg/`: a **classic 4-player
Public Goods Game** (1 human **Marty** + 3 bots **Doc**, **Biff** and
**Jennifer**), themed after *Back to the Future*.

- Endowment: **10 Energy Units** per player per round (5 rounds).
- Multiplier of each round's common fund: **1.6x**, split equally among 4 players.
- **Collective-Risk Threshold**: Energy accumulates across 5 rounds toward **1.21 GW** (100 units total).
- Final outcome at **Round 5**: **"88 MPH - Time travel successful!"** (keep all earnings) vs **"Time Paradox Triggered!"** (earnings wiped out if threshold is missed).
- **Behavioral bots**: Doc (Altruist/Target-Pacer), Biff (Pure Free Rider), Jennifer (Conditional Cooperator).
- Fully **bilingual (IT/EN)** with a language selector, 80s neon-dashboard theme.
- Two session configs: `bttf_pgg_human` (Marty human) and `bttf_pgg_auto`
  (Marty simulated with Tit-for-Tat).

```bash
otree devserver          # then pick a bttf_pgg session
otree test bttf_pgg_auto # automated test (Marty = Tit-for-Tat bot)
```

Full documentation (rules, math, bot strategies, setup):

- Italiano: [`docs/README_IT.md`](docs/README_IT.md)
- English: [`docs/README_EN.md`](docs/README_EN.md)
