from otree.api import *

import math
import random

import numpy as np


doc = """
Dilemma del Prigioniero Quantistico (protocollo EWL - Eisert/Wilkens/Lewenstein).

Un singolo partecipante umano gioca contro un bot. Il partecipante sceglie due
parametri continui, Theta (0..pi) e Phi (0..pi/2), che definiscono la strategia
unitaria U(theta, phi) applicata al suo qubit. La strategia del bot e' configurata
tramite la chiave `bot_strategy` della configurazione di sessione.

Il sistema a due qubit parte in |00>, viene entangled con l'operatore J, ogni
giocatore applica la propria unitaria, si applica J^dagger e lo stato viene
misurato nella base computazionale per ottenere le probabilita' dei quattro
esiti classici |CC>, |CD>, |DC>, |DD>.
"""


class C(BaseConstants):
    NAME_IN_URL = 'quantum_pd'
    PLAYERS_PER_GROUP = None

    # -------------------------------------------------------------------------
    # IMPOSTAZIONI MODIFICABILI DALLO SPERIMENTATORE (senza conoscere la fisica)
    # -------------------------------------------------------------------------
    # NUM_ROUNDS .... quanti round gioca ogni partecipante.
    NUM_ROUNDS = 5

    # Payoff classici del Dilemma del Prigioniero (in punti): quanto guadagna il
    # partecipante nelle quattro combinazioni possibili.
    #   PAYOFF_CC -> entrambi cooperano
    #   PAYOFF_CD -> il partecipante coopera e il bot tradisce (caso peggiore)
    #   PAYOFF_DC -> il partecipante tradisce e il bot coopera (caso migliore)
    #   PAYOFF_DD -> entrambi tradiscono
    PAYOFF_CC = 3   # entrambi cooperano
    PAYOFF_CD = 0   # umano coopera, bot tradisce
    PAYOFF_DC = 5   # umano tradisce, bot coopera
    PAYOFF_DD = 1   # entrambi tradiscono

    # "Intensita'" della correlazione quantistica tra le due scelte.
    # NON modificare se non sai cosa stai facendo: pi/2 e' il valore standard.
    GAMMA = math.pi / 2

    # Angoli delle mosse speciali.
    THETA_COOPERATE = 0.0
    PHI_COOPERATE = 0.0
    THETA_DEFECT = math.pi
    PHI_DEFECT = 0.0
    THETA_QUANTUM = 0.0
    PHI_QUANTUM = math.pi / 2

    # Strategie bot supportate (chiavi valide per session.config['bot_strategy']).
    BOT_STRATEGIES = [
        'always_classical_cooperate',
        'always_classical_defect',
        'always_quantum',
        'random',
        'tit_for_tat',
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- Input dell'umano (form della DecisionPage) ---
    theta = models.FloatField(
        min=0, max=math.pi, initial=math.pi / 2,
        label="Quanto cooperi (0) o tradisci (pi)",
    )
    phi = models.FloatField(
        min=0, max=math.pi / 2, initial=math.pi / 4,
        label="Quanto usi la mossa speciale (0 = no, pi/2 = si)",
    )

    # --- Strategia e mossa del bot ---
    bot_strategy = models.StringField()
    bot_theta = models.FloatField()
    bot_phi = models.FloatField()

    # --- Esiti della simulazione quantistica ---
    prob_cc = models.FloatField()
    prob_cd = models.FloatField()
    prob_dc = models.FloatField()
    prob_dd = models.FloatField()
    outcome = models.StringField()
    payoff_round = models.FloatField()
    bot_payoff = models.FloatField()
    expected_payoff = models.FloatField()
    expected_bot_payoff = models.FloatField()


# ---------------------------------------------------------------------------
# MATEMATICA EWL
# ---------------------------------------------------------------------------

def unitary(theta, phi):
    """Strategia unitaria U(theta, phi) per un singolo qubit.

    U = [[ e^{i*phi}*cos(theta/2),            sin(theta/2)      ],
         [ -sin(theta/2),           e^{-i*phi}*cos(theta/2) ]]
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([
        [np.exp(1j * phi) * c, s],
        [-s, np.exp(-1j * phi) * c],
    ], dtype=complex)


def entanglement_operator(gamma):
    """Operatore di entanglement J.

    J = cos(gamma/2) * I (x) I  +  i*sin(gamma/2) * D (x) D

    dove D = U(pi, 0) = [[0, 1], [-1, 0]] e' l'operatore di "tradimento" classico.
    Per gamma = pi/2 si ottiene lo stato di Bell massimamente entangled.
    Usare lo stesso D della parametrizzazione garantisce che il protocollo
    riproduca il Dilemma del Prigioniero classico e la "mossa miracolo" Q.
    """
    I = np.eye(2, dtype=complex)
    D = unitary(math.pi, 0.0)  # operatore di defezione classica
    return (
        np.cos(gamma / 2) * np.kron(I, I)
        + 1j * np.sin(gamma / 2) * np.kron(D, D)
    )


def ewl_probabilities(theta_h, phi_h, theta_b, phi_b, gamma):
    """Simula il protocollo EWL e restituisce le probabilita' dei 4 esiti.

    |psi_f> = J^dagger * (U_h (x) U_b) * J * |00>

    Restituisce una lista [P_CC, P_CD, P_DC, P_DD] dove il primo qubit
    e' quello dell'umano e il secondo del bot (0 = coopera, 1 = tradisce).
    """
    J = entanglement_operator(gamma)
    U_h = unitary(theta_h, phi_h)
    U_b = unitary(theta_b, phi_b)
    U_total = np.kron(U_h, U_b)

    psi0 = np.zeros(4, dtype=complex)
    psi0[0] = 1.0  # |00>

    psi_final = J.conj().T @ U_total @ J @ psi0
    probs = np.real(psi_final * np.conj(psi_final))
    # Normalizzazione per rimuovere eventuali residui numerici.
    probs = probs / probs.sum()
    return [float(probs[0]), float(probs[1]), float(probs[2]), float(probs[3])]


# ---------------------------------------------------------------------------
# MOSSA DEL BOT
# ---------------------------------------------------------------------------

def get_bot_angles(player):
    """Restituisce gli angoli (theta, phi) del bot in base alla sua strategia."""
    strategy = player.bot_strategy

    if strategy == 'always_classical_cooperate':
        return C.THETA_COOPERATE, C.PHI_COOPERATE

    if strategy == 'always_classical_defect':
        return C.THETA_DEFECT, C.PHI_DEFECT

    if strategy == 'always_quantum':
        return C.THETA_QUANTUM, C.PHI_QUANTUM

    if strategy == 'random':
        return random.uniform(0, math.pi), random.uniform(0, math.pi / 2)

    if strategy == 'tit_for_tat':
        # Nel primo round non c'e' una mossa precedente da copiare:
        # il bot coopera classicamente.
        if player.round_number == 1:
            return C.THETA_COOPERATE, C.PHI_COOPERATE
        prev = player.in_round(player.round_number - 1)
        return prev.theta, prev.phi

    # Fallback sicuro nel caso di strategia sconosciuta.
    return C.THETA_COOPERATE, C.PHI_COOPERATE


# ---------------------------------------------------------------------------
# PAYOFF
# ---------------------------------------------------------------------------

# Ordine degli esiti: indice 0 -> |00> = CC, 1 -> |01> = CD, 2 -> |10> = DC, 3 -> |11> = DD.
OUTCOMES = ['CC', 'CD', 'DC', 'DD']

OUTCOME_LABELS = {
    'CC': 'Entrambi cooperano',
    'CD': 'Tu cooperi, il computer tradisce',
    'DC': 'Tu tradisci, il computer coopera',
    'DD': 'Entrambi tradite',
}

BOT_STRATEGY_LABELS = {
    'always_classical_cooperate': 'Coopera sempre',
    'always_classical_defect': 'Tradisce sempre',
    'always_quantum': 'Mossa speciale',
    'random': 'Scelta casuale',
    'tit_for_tat': 'Imita la tua scelta precedente',
}


def describe_move(theta, phi, eps=0.01):
    """Traduce la scelta (theta, phi) in una descrizione in linguaggio semplice."""
    if abs(theta - math.pi) < eps:
        return 'Tradimento'
    if abs(theta) < eps and abs(phi) < eps:
        return 'Cooperazione'
    if abs(theta) < eps and abs(phi - math.pi / 2) < eps:
        return 'Mossa speciale'
    return 'Mossa mista'


def payoffs_for_outcome(outcome):
    """Restituisce (payoff umano, payoff bot) per un esito 'XY' (X = umano)."""
    if outcome == 'CC':
        return C.PAYOFF_CC, C.PAYOFF_CC
    if outcome == 'CD':
        return C.PAYOFF_CD, C.PAYOFF_DC
    if outcome == 'DC':
        return C.PAYOFF_DC, C.PAYOFF_CD
    return C.PAYOFF_DD, C.PAYOFF_DD


def simulate(group):
    """Esegue la logica quantistica e determina i punti del round."""
    for player in group.get_players():
        player.bot_strategy = group.session.config.get(
            'bot_strategy', 'always_classical_cooperate'
        )
        bot_theta, bot_phi = get_bot_angles(player)
        player.bot_theta = bot_theta
        player.bot_phi = bot_phi

        probs = ewl_probabilities(
            player.theta, player.phi, bot_theta, bot_phi, C.GAMMA
        )
        player.prob_cc, player.prob_cd, player.prob_dc, player.prob_dd = probs

        # Payoff attesi (valore atteso sulle quattro probabilita').
        player.expected_payoff = (
            probs[0] * C.PAYOFF_CC
            + probs[1] * C.PAYOFF_CD
            + probs[2] * C.PAYOFF_DC
            + probs[3] * C.PAYOFF_DD
        )
        player.expected_bot_payoff = (
            probs[0] * C.PAYOFF_CC
            + probs[1] * C.PAYOFF_DC
            + probs[2] * C.PAYOFF_CD
            + probs[3] * C.PAYOFF_DD
        )

        # Estrazione probabilistica dell'esito finale del round.
        player.outcome = random.choices(OUTCOMES, weights=probs, k=1)[0]
        human_payoff, bot_payoff = payoffs_for_outcome(player.outcome)
        player.payoff_round = human_payoff
        player.bot_payoff = bot_payoff
        player.payoff = human_payoff


# ---------------------------------------------------------------------------
# PAGINE
# ---------------------------------------------------------------------------

class DecisionPage(Page):
    form_model = 'player'
    form_fields = ['theta', 'phi']

    @staticmethod
    def vars_for_template(player):
        return dict(
            theta_value=player.theta if player.theta is not None else math.pi / 2,
            phi_value=player.phi if player.phi is not None else math.pi / 4,
            theta_max=math.pi,
            phi_max=math.pi / 2,
            payoff_cc=C.PAYOFF_CC,
            payoff_cd=C.PAYOFF_CD,
            payoff_dc=C.PAYOFF_DC,
            payoff_dd=C.PAYOFF_DD,
            num_rounds=C.NUM_ROUNDS,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = simulate


class ResultsPage(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            human_move_label=describe_move(player.theta, player.phi),
            bot_strategy_label=BOT_STRATEGY_LABELS.get(
                player.bot_strategy, player.bot_strategy
            ),
            outcome_label=OUTCOME_LABELS.get(player.outcome, player.outcome),
            prob_cc_pct=round(player.prob_cc * 100, 1),
            prob_cd_pct=round(player.prob_cd * 100, 1),
            prob_dc_pct=round(player.prob_dc * 100, 1),
            prob_dd_pct=round(player.prob_dd * 100, 1),
            payoff_round=round(player.payoff_round, 2),
            bot_payoff=round(player.bot_payoff, 2),
            expected_payoff=round(player.expected_payoff, 2),
        )


page_sequence = [DecisionPage, ResultsWaitPage, ResultsPage]
