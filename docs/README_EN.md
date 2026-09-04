# Public Goods Game - "Back to the Future" (EN documentation)

An **oTree** app implementing a **classic 4-player Public Goods Game (PGG)** -
1 human + 3 bots - set in the **"Back to the Future"** narrative.

---

## 1. Overview and narrative

You are **Marty McFly**, in 1985. The **DeLorean** is stuck and the **Flux
Capacitor** is drained: time travel requires at least **1.21 GW** of power.
Three other residents of Hill Valley are playing with you:

| Player | Type | Strategy | Behavioral Role (Literature) |
|--------|------|----------|-------------------------------|
| **Marty** | Human (or bot in tests) | Free choice / Tit-for-Tat | Decision maker (pivotal) |
| **Doc**   | Bot  | Always Cooperate | Altruist / Target-Pacer (Milinski et al. 2008) |
| **Biff**  | Bot  | Always Defect | Pure Free Rider (Fischbacher et al. 2001) |
| **Jennifer** | Bot | Conditional Cooperator | Reactive/Reciprocal (Fischbacher et al. 2001) |

Across 5 rounds, all four players receive an endowment of **10 Energy Units**
(Plutonium) per round and decide how much to contribute to the common fund.
Energy accumulates round after round in the Flux Capacitor.
At the end of **Round 5 (game end)**, if the group's collective energy reaches at
least **100 units (equivalent to 1.21 GW)**, time travel succeeds:
**"88 MPH - Time travel successful!"** and Marty secures all accumulated earnings.
If the collective energy falls short of 1.21 GW, a **"Time Paradox"** is triggered:
the timeline collapses and all earnings are wiped out (*Collective-Risk failure*, Milinski et al. 2008).

---

## 2. PGG rules and mathematical values

This game combines a repeated linear public goods game with an intertemporal **Collective-Risk Social Dilemma (CRSD)**.

- **Round endowment** per player: `ENDOWMENT = 10` Energy Units (50 units total across 5 rounds).
- **Round multiplier**: `MULTIPLIER = 1.6`.
- **Number of players**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Number of rounds**: `NUM_ROUNDS = 5`.

Each player `i` chooses a contribution `c_i \in [0, 10]`.
The provisional round payoff for player `i` is:

```
payoff_i = 10 - c_i + (1.6 * (c_1 + c_2 + c_3 + c_4)) / 4
```

### Cumulative end-game threshold (1.21 GW)

- `FLUX_TARGET_GW = 1.21` (power required for time travel).
- `CUMULATIVE_TARGET_ENERGY = 100` (minimum sum of all 4 players' contributions across 5 rounds).
- Group maximum capacity over 5 rounds: `4 players * 10 units * 5 rounds = 200 units`.
- The 100-unit threshold corresponds exactly to **50% collective cooperation**.

Flux Capacitor power grows proportionally with accumulated energy:

```
power (GW) = (cumulative_energy / 100) * 1.21 GW
```

- **In Rounds 1–4 (charging phase)**: the results page shows real-time charging progression via a retro bar indicator without issuing premature verdicts.
- **At Round 5 (final verdict)**:
  - If `cumulative_energy >= 100` (at least 1.21 GW): **Time travel succeeds at 88 MPH**. Marty keeps 100% of accumulated round earnings.
  - If `cumulative_energy < 100`: **Time Paradox Triggered**. Final earnings are wiped out (`PARADOX_PAYOFF_RATIO = 0.0`).

---

## 3. Bot strategies (Scientific Foundations)

Bot strategies are grounded in experimental public goods literature (*Fischbacher, Gächter & Fehr 2001*; *Milinski et al. 2008*):

### Doc - *Altruistic Cooperator / Target-Pacer*
Contributes **10 units every round** to secure the DeLorean's baseline energy (50 units total).

### Biff - *Pure Free Rider*
Contributes **0 units every round**, exploiting others to maximize private account gains.

### Jennifer - *Conditional Cooperator*
Replaces random play with empirical conditional cooperation:
- **Round 1**: offers an initial benevolent contribution of **5 units**.
- **Rounds 2–5**: observes the contributions of the other three participants (Marty, Doc, Biff) in the previous round and matches their average.
  If Marty contributes generously (10), Jennifer responds with 7; if Marty defects (0), Jennifer drops to 3.

### Marty - human or bot (Tit-for-Tat)

- **Human Marty** (`marty_strategy = 'human'`): chooses the contribution through the interactive dashboard (0-10 slider).
- **Bot Marty** (`marty_strategy = 'tit_for_tat'`, automatic sessions/tests):
  - **Round 1**: contributes **5 units**.
  - **From round 2 on**: contributes the rounded mean of the contributions made by Doc, Biff, and Jennifer in the previous round.

---

## 4. Installation, running and session configuration

### Requirements

- Python 3.9+
- oTree 5+ (recommended: 5.10 or 6.0)

`requirements.txt` contains `otree` and `numpy` (the latter is used by the
`quantum_pd` app, not by the PGG).

### Installation

```bash
pip install -r requirements.txt
```

### Running the development server

```bash
otree devserver
```

Open <http://localhost:8000>. From the landing page, pick one of the sessions:

| Session | `marty_strategy` | Use |
|---------|------------------|-----|
| `bttf_pgg_human` | `human` | Marty played by a human (interactive dashboard) |
| `bttf_pgg_auto`  | `tit_for_tat` | Marty simulated (automatic sessions/tests) |

### Automated bot tests

```bash
otree test bttf_pgg_auto
```

In test mode Marty is a bot using **Tit-for-Tat** (5 in round 1, then the mean
of the other players' previous-round contributions).

### Session configuration

Each `SESSION_CONFIGS` entry in `settings.py` accepts three custom keys:

- `marty_strategy` - `'human'` (default) or `'tit_for_tat'`.
- `default_language` - initial language of the selector: `'it'` or `'en'`.
- `show_bot_results` - `False` (default, participant only sees their own choice and the aggregate fund, hiding individual bot strategies and contributions) or `True` (displays the detailed breakdown table with Doc, Biff, and Jennifer).

Example:

```python
dict(
    name='bttf_pgg_human',
    display_name='Public Goods Game - Back to the Future (Marty: human)',
    num_demo_participants=1,
    app_sequence=['bttf_pgg'],
    marty_strategy='human',
    default_language='it',
    show_bot_results=False,
)
```

### Tunable parameters (in `bttf_pgg/__init__.py`, class `C`)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `NUM_ROUNDS` | `5` | Number of rounds |
| `ENDOWMENT` | `10` | Initial endowment per player |
| `MULTIPLIER` | `1.6` | Common fund multiplier |
| `THRESHOLD_POT` | `30` | Minimum total contribution for 1.21 GW |
| `FLUX_TARGET_GW` | `1.21` | Target power (GW) |
| `TFT_FIRST_ROUND` | `5` | Tit-for-Tat contribution in round 1 |

---

## 5. Multilingual support (Italian / English)

The interface is fully bilingual. The first page is a **language selector**
([ IT ] Italiano / [ EN ] English); the choice is stored on the participant and
used by all subsequent pages.

All strings are centralized in the `TEXTS` dictionary (`'it'` and `'en'` keys)
in `bttf_pgg/__init__.py`.

---

## 6. Architecture (non-obvious notes)

- The three bots are **virtual**: `PLAYERS_PER_GROUP = 1` (each group = one
  human, Marty). The bot simulation and the whole PGG computation run in
  `simulate()`, wired to `ResultsWaitPage.after_all_players_arrive`. The oTree
  bot framework is used only for automated tests, not for the opponent bots.
- Templates follow the oTree 5+ **"lite" conventions**: files directly in the
  app folder, `{{ extends }}` / `{{ block }}` syntax, no `{% %}` tags.
- The visual theme is an **80s dashboard** (neon green/orange on a dark
  background), defined via inline CSS in the templates.

## 7. File structure

```
bttf_pgg/
??? __init__.py            # Models, TEXTS, bot strategies, simulate(), pages, PlayerBot
??? LanguagePage.html      # Language selector
??? IntroPage.html         # Instructions and narrative
??? DecisionPage.html      # Contribution slider dashboard
??? ResultsWaitPage.html   # "Computing..." wait page
??? ResultsPage.html       # Results, GW and payoffs
```
