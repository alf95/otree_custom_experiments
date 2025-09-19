# oTree Custom Experiments

A collection of custom experimental games and surveys built using **oTree**, designed for behavioral and experimental economics studies. Includes canonical games such as **Public Goods**, **Ultimatum Game**, **Dictator**, and many others.

---

## Table of Contents

- [Features](#features)
- [Included Experiments](#included-experiments)
- [Key Experiments](#key-experiments)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Experiments](#running-the-experiments)
- [Configuration](#configuration)
- [Structure](#structure)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Features

- Ready-to-run canonical behavioral experiments.
- Modular app structure — mix & match experiments.
- Reusable templates and shared utilities.
- Simple deployment on local servers or platforms like Heroku.
- Compatible with the latest oTree versions.

---

## Included Experiments

| Experiment | Description |
|------------|-------------|
| **dictator** | Dictator game (player allocates endowment). |
| **ultimatum_game** | Two-player bargaining with accept/reject stage. |
| **public_goods_simple** | Multi-player public goods contribution game. |
| **prisoner** | Classic prisoner’s dilemma. |
| **matching_pennies** | Zero-sum matching pennies. |
| **guess_two_thirds** | Guess 2/3 of the group average. |
| **trust**, **trust_simple** | Trust games in different formats. |
| **traveler_dilemma**, **cournot**, **bertrand** | More complex strategic games. |
| **survey** | Survey/questionnaire app. |
| **payment_info** | Payment handling screens. |

---

## Key Experiments

### Public Goods Game (`public_goods_simple`)

Implements a **basic public goods experiment**:

- Each participant receives an endowment per round.
- Participants choose how much to contribute to a shared pool.
- The total pool is multiplied by a factor (> 1 but < group size) and divided equally among all.
- Payoffs encourage free-riding but group optimum is full contribution.

**Why It’s Important:** Useful for studying cooperation, social dilemmas, punishment/reward mechanisms.

### Ultimatum Game (`ultimatum_game`)

Implements a **classic ultimatum bargaining game**:

- Player A proposes a split of an endowment.
- Player B either **accepts** (split is implemented) or **rejects** (both get 0).

**Why It’s Important:** Used to study fairness, bargaining power, and rejection thresholds.

### Linking Public Goods and Ultimatum Game

These two apps can be linked in a session configuration (`settings.py`) so that participants:

- First play a **public goods** round (revealing cooperative behavior).
- Then play the **ultimatum game** (revealing fairness preferences).

This sequencing allows researchers to examine how cooperative behavior impacts bargaining decisions — or vice versa. Cumulative payoffs are automatically tracked across apps.

---

## Getting Started

### Prerequisites

- Python 3.x
- [oTree](https://otree.readthedocs.io/) installed.
- Packages listed in `requirements.txt`.

### Installation

```bash
git clone https://github.com/alf95/otree_custom_experiments.git
cd otree_custom_experiments

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Running the Experiments

```bash
otree devserver
```

Then open `http://localhost:8000` in your browser and start a session from the admin panel.

---

## Configuration

- **settings.py** — Session configs, room configs, and oTree parameters.
- **requirements.txt** — Python dependencies.
- **Procfile**, **runtime.txt** — Deployment support for Heroku.

To run public goods followed by ultimatum:

```python
SESSION_CONFIGS = [
    dict(
        name='pg_and_ultimatum',
        display_name="Public Goods + Ultimatum",
        num_demo_participants=4,
        app_sequence=['public_goods_simple', 'ultimatum_game'],
    ),
]
```

---

## Structure

```
otree_custom_experiments/
├── public_goods_simple/
├── ultimatum_game/
├── dictator/
├── prisoner/
├── matching_pennies/
├── trust/
├── traveler_dilemma/
├── ...
├── settings.py
├── requirements.txt
└── Procfile
```

Each folder contains an independent oTree app with `models.py`, `pages.py`, `templates/`, and tests.

---

## License

See [LICENSE](LICENSE) for details.

If you use this code for research, please cite:

> Chen, Daniel L., Martin Schonger, and Chris Wickens. “oTree – An open-source platform for laboratory, online, and field experiments.” *Journal of Behavioral and Experimental Finance*, Vol. 9, 2016, 88‑97.

---

## Contributing

Pull requests are welcome! Please fork the repo, create a feature branch, and submit a PR with clear documentation.

---

## Contact

For questions or issues, open a GitHub Issue in this repository.

