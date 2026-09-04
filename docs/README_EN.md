# Public Goods Game - "Back to the Future" (EN documentation)

An **oTree** app implementing a **classic 4-player Public Goods Game (PGG)** -
1 human + 3 bots - set in the **"Back to the Future"** narrative.

---

## 1. Overview and narrative

You are **Marty McFly**, in 1985. The **DeLorean** is stuck and the **Flux
Capacitor** is drained: time travel requires at least **1.21 GW** of power.
Three other residents of Hill Valley are playing with you:

| Player | Type | Strategy |
|--------|------|----------|
| **Marty** | Human (or bot in tests) | Free choice / Tit-for-Tat |
| **Doc**   | Bot  | Always Cooperate |
| **Biff**  | Bot  | Always Defect |
| **Jennifer** | Bot | Random |

Each round, the four players receive an endowment of **10 Energy Units**
(Plutonium) and decide how much to contribute to the common fund. If the fund
clears the **1.21 GW** threshold, time travel succeeds - **"Time travel
successful (88 MPH)!"** - otherwise a **"Time Paradox Triggered!"** occurs.

---

## 2. PGG rules and mathematical values

This is a standard linear public goods game.

- **Initial endowment** per player: `ENDOWMENT = 10` Energy Units.
- **Multiplier** of the common fund: `MULTIPLIER = 1.6`.
- **Number of players**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Number of rounds**: `NUM_ROUNDS = 5` (configurable in `C`).

Each player `i` chooses a contribution `c_i` between `0` and `10`.
The round payoff for player `i` is:

```
payoff_i = 10 - c_i + (1.6 * (c_1 + c_2 + c_3 + c_4)) / 4
```

Step by step:

1. Sum the 4 contributions: `fund = c_marty + c_doc + c_biff + c_jennifer`.
2. Multiply the fund by `1.6`.
3. Split the multiplied fund into **4 equal shares**.
4. Each player's payoff is: *10 - own contribution + own share*.

**Example**: if everyone contributes 10 -> fund `40 x 1.6 = 64`, share `16`
each, payoff `10 - 10 + 16 = 16` each.

### Narrative threshold (1.21 GW)

- `FLUX_TARGET_GW = 1.21` (power required for time travel).
- `THRESHOLD_POT = 30` (minimum total contribution to reach 1.21 GW).

Flux Capacitor power is computed as:

```
power (GW) = (1.6 * fund) * (1.21 / (30 * 1.6))
```

The threshold multiplied fund is `30 x 1.6 = 48` units, which corresponds
exactly to **1.21 GW**. Time travel succeeds when
`total fund >= THRESHOLD_POT` (at least 30 units contributed in total).

---

## 3. Bot strategies

Strategies are implemented in `bttf_pgg/__init__.py`.

### Doc - *Always Cooperate*
Contributes **10 units every round**.

```python
doc = C.ENDOWMENT  # 10
```

### Biff - *Always Defect*
Contributes **0 units every round**.

```python
biff = 0
```

### Jennifer - *Random*
Contributes a **random amount** (uniform integer in `[0, 10]`) each round.

```python
jennifer = random.randint(0, C.ENDOWMENT)
```

### Marty - human or bot (Tit-for-Tat)

- **Human Marty** (`marty_strategy = 'human'`): chooses the contribution through
  the **interactive dashboard** (0-10 slider).
- **Bot Marty** (`marty_strategy = 'tit_for_tat'`, automatic sessions/tests):
  - **Round 1**: contributes **5 units** (`TFT_FIRST_ROUND = 5`).
  - **From round 2 on**: contributes the **rounded mean of the contributions
    made by the other three players (Doc, Biff, Jennifer) in the previous round**.

```python
def marty_tit_for_tat_contribution(player):
    if player.round_number == 1:
        return C.TFT_FIRST_ROUND
    prev = player.in_round(player.round_number - 1)
    others = [prev.doc_contribution, prev.biff_contribution, prev.jennifer_contribution]
    return int(round(sum(others) / len(others)))
```

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
