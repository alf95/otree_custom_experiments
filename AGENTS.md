# AGENTS.md

oTree 5+ experiment implementing the EWL Quantum Prisoner's Dilemma (human vs bot).

## Commands

- `pip install -r requirements.txt` — deps are `otree` + `numpy`.
- `otree devserver` — run locally; opens http://localhost:8000.
- No tests/lint/typecheck exist in this repo.

## Architecture (non-obvious)

- Single app `quantum_pd/`; project root holds only `settings.py` + `requirements.txt`.
- Bot is **virtual**: `PLAYERS_PER_GROUP = 1` (each group = one human). The bot's
  move and the whole EWL simulation run in `simulate()` in `__init__.py`, wired as
  `ResultsWaitPage.after_all_players_arrive`. There is no oTree bot framework here.
- Bot behaviour is selected by the custom `bot_strategy` key in each
  `SESSION_CONFIGS` entry in `settings.py`; read via `session.config['bot_strategy']`.
- `tit_for_tat` reads the human's previous-round angles with `player.in_round(...)`
  and cooperates on round 1.

## oTree 5+ "lite" conventions (get these wrong and it breaks)

- Templates live **directly in the app folder**, named exactly `<PageName>.html`
  (no `templates/app/` nesting, no `models.py`/`pages.py`).
- Templates use `{{ extends "global/Page.html" }}`, `{{ block content }}…{{ endblock }}`,
  `{{ next_button }}`, `{{ formfield_errors 'field' }}` — no `{% %}` tags or `{% load otree %}`.
- Constants are UPPER_CASE in `class C(BaseConstants)` (`NUM_ROUNDS`, `PLAYERS_PER_GROUP`).
- Pages use `form_model = 'player'` + `form_fields = [...]`; `vars_for_template`,
  `is_displayed`, `before_next_page` are `@staticmethod` methods taking `player`.
- The Theta/Phi sliders are **raw HTML** `<input type="range" name="theta" ...>`;
  they bind to the model only because the `name` matches a `form_fields` entry.

## EWL physics (critical)

- `J` MUST be built from the **same defect operator** `D = U(π, 0) = [[0,1],[-1,0]]`
  used by the strategy parametrization (`entanglement_operator()` does this):
  `J = cos(γ/2)·I⊗I + i·sin(γ/2)·D⊗D`. Using `σx` instead silently breaks the
  "miracle move" — `(Q, Q)` would yield `DD` instead of `CC` (payoff `(3,3)`).
- Verified outcomes: `(C,C)→CC`, `(C,D)→CD`, `(D,C)→DC`, `(D,D)→DD`, `(Q,Q)→CC`.
- `ewl_probabilities()` returns `[P_CC, P_CD, P_DC, P_DD]`; qubit order is
  human-then-bot, so `P_CD` means human cooperates / bot defects.
- Cast numpy results to Python `float` before assigning to model fields (oTree 5.x
  had a bug with numpy dtypes stored in fields).

## Gotchas

- `numpy` is **not installed** in this dev environment — `python -c "import numpy"`
  fails. Physics was verified with a pure-Python script; `otree devserver` has not
  been run here. To verify math without numpy, replicate the circuit with `cmath`.
