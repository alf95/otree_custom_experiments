from otree.api import *

import random


doc = """
Public Goods Game (PGG) classico a 4 ruoli, tema "Ritorno al Futuro".

Un partecipante umano (Marty McFly) gioca contro tre bot:
    * Doc      -> "always cooperate": versa sempre 10 unita'
    * Biff     -> "always defect": versa sempre 0 unita'
    * Jennifer -> "random": versa un contributo casuale a ogni round

Regole: dotazione di 10 unita' di energia a testa; il fondo comune viene
moltiplicato per 1.6 e ridistribuito in parti uguali tra i 4 giocatori.
Payoff del round: 10 - contributo + (1.6 * fondo) / 4.

Se il fondo supera la soglia di 1.21 GW il viaggio nel tempo riesce
("88 MPH!"), altrimenti si innesca un paradosso temporale.

I tre bot sono VIRTUALI (coerente con AGENTS.md del progetto): ogni gruppo
contiene un solo umano (PLAYERS_PER_GROUP = None) e la simulazione dei bot gira
in simulate(). Marty come bot (sessioni/test automatici) usa "tit-for-tat".
"""


class C(BaseConstants):
    NAME_IN_URL = 'bttf_pgg'
    PLAYERS_PER_GROUP = None  # un solo gruppo con tutti i giocatori (i bot sono virtuali)

    NUM_ROUNDS = 5

    # --- Parametri economici del PGG ---
    N_PLAYERS = 4           # 1 umano (Marty) + 3 bot
    ENDOWMENT = 10          # unita' di energia iniziali per giocatore
    MULTIPLIER = 1.6        # fattore moltiplicativo del fondo comune

    # --- Narrativa "Ritorno al Futuro" ---
    FLUX_TARGET_GW = 1.21   # potenza necessaria al viaggio nel tempo
    # Contributo totale minimo (somma dei 4 contributi) per raggiungere 1.21 GW.
    # Il fondo moltiplicato di soglia vale THRESHOLD_POT * MULTIPLIER = 48 unita'
    # e corrisponde esattamente a 1.21 GW.
    THRESHOLD_POT = 30

    # Tit-for-tat (Marty bot): contributo del primo round.
    TFT_FIRST_ROUND = 5

    # Strategie valide per session.config['marty_strategy'].
    MARTY_STRATEGIES = ['human', 'tit_for_tat']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- Input del partecipante ---
    lang = models.StringField(
        choices=[['it', 'Italiano'], ['en', 'English']],
        initial='it',
    )
    contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT,
    )

    # --- Strategia di Marty (dalla configurazione di sessione) ---
    marty_strategy = models.StringField()

    # --- Contributi dei tre bot ---
    doc_contribution = models.IntegerField()
    biff_contribution = models.IntegerField()
    jennifer_contribution = models.IntegerField()

    # --- Risultati del round ---
    total_contribution = models.FloatField()
    fund_energy = models.FloatField()
    individual_share = models.FloatField()
    flux_power_gw = models.FloatField()
    goal_reached = models.BooleanField()

    marty_payoff = models.FloatField()
    doc_payoff = models.FloatField()
    biff_payoff = models.FloatField()
    jennifer_payoff = models.FloatField()


# ---------------------------------------------------------------------------
# INTERNAZIONALIZZAZIONE (italiano / inglese)
# ---------------------------------------------------------------------------

TEXTS = {
    'it': {
        'choose_lang': 'Scegli la lingua',
        'start': 'Inizia / Start',

        'intro_title': 'Benvenuto a Hill Valley, 1985!',
        'intro_1': (
            "Sei Marty McFly. La DeLorean e' ferma e il Flusso Canalizzatore e' "
            "scarico: per viaggiare nel tempo serve una potenza di almeno 1.21 GW. "
            "Insieme a te giocano altri tre abitanti di Hill Valley: Doc, Biff e Jennifer."
        ),
        'intro_2': (
            "In ogni round ciascun giocatore riceve 10 unita' di energia e decide "
            "quante versarne nel fondo comune, il Flusso Canalizzatore."
        ),
        'intro_rules_title': 'Come funziona il fondo comune',
        'rule_1': 'Ogni giocatore parte con 10 unita\' di energia.',
        'rule_2': 'Ogni giocatore versa una quota da 0 a 10 unita\' nel fondo.',
        'rule_3': 'Il fondo viene moltiplicato per 1.6.',
        'rule_4': 'Il fondo moltiplicato viene diviso in parti uguali tra i 4 giocatori.',
        'rule_5': 'Il tuo guadagno del round e\': 10 meno quota versata, piu\' la tua parte del fondo.',
        'intro_goal': (
            "Obiettivo: far superare al Flusso Canalizzatore la soglia di 1.21 GW. "
            "Se il fondo supera la soglia, il viaggio nel tempo riesce a 88 MPH. "
            "Altrimenti si innesca un paradosso temporale."
        ),
        'intro_rounds': 'Il gioco dura {n} round. Gli altri tre giocatori sono controllati dal computer.',
        'intro_start': 'Inizia il viaggio',

        'decision_header': 'ENERGIA PER IL FLUSSO CANALIZZATORE',
        'decision_title': 'Round {r} di {n} - La tua scelta',
        'decision_intro': (
            "Marty, hai 10 unita' di energia. Quante ne versi nel Flusso "
            "Canalizzatore? Il resto resta a te."
        ),
        'decision_slider_label': 'Unita\' versate nel fondo comune',
        'decision_min': '0 - tengo tutto',
        'decision_max': '10 - verso tutto',
        'decision_current': 'Unita\' versate',
        'decision_quick': 'Scelte rapide',
        'decision_quick_all': 'Tutto (10)',
        'decision_quick_half': 'Meta\' (5)',
        'decision_quick_none': 'Niente (0)',
        'decision_submit': 'Versa nel fondo',

        'wait_title': 'Calcolo in corso...',
        'wait_body': 'Doc sta alimentando il Flusso Canalizzatore...',

        'results_header': 'RISULTATI DEL ROUND',
        'results_title': 'Round {r} di {n} - Risultati',
        'col_player': 'Giocatore',
        'col_strategy': 'Strategia',
        'col_contribution': 'Versato',
        'col_payoff': 'Guadagno',
        'you_label': 'Tu (Marty)',
        'strategy_you': 'Scelta libera',
        'strategy_always_cooperate': 'Coopera sempre',
        'strategy_always_defect': 'Tradisce sempre',
        'strategy_random': 'Casuale',
        'results_flux_title': 'Energia del Flusso Canalizzatore',
        'results_flux_target': 'Obiettivo',
        'results_contrib_title': 'Contributi al fondo comune',
        'results_your_decision': 'La tua decisione',
        'results_summary_title': 'Riepilogo del fondo',
        'results_total': 'Fondo totale (prima della moltiplicazione)',
        'results_fund': 'Fondo moltiplicato (x 1.6)',
        'results_share': 'La tua quota (fondo / 4)',
        'results_payoff_you': 'Il tuo guadagno del round',
        'success_message': 'Viaggio nel tempo riuscito (88 MPH)!',
        'paradox_message': 'Paradosso Temporale Innescato!',
        'units': 'unita\'',
        'gw': 'GW',
        'results_continue': 'Prossimo round',
    },
    'en': {
        'choose_lang': 'Choose your language',
        'start': 'Inizia / Start',

        'intro_title': 'Welcome to Hill Valley, 1985!',
        'intro_1': (
            "You are Marty McFly. The DeLorean is stuck and the Flux Capacitor "
            "is drained: time travel requires at least 1.21 GW of power. Three "
            "other residents of Hill Valley are playing with you: Doc, Biff and Jennifer."
        ),
        'intro_2': (
            "In each round, every player receives 10 Energy Units and decides how "
            "many to contribute to the common fund, the Flux Capacitor."
        ),
        'intro_rules_title': 'How the common fund works',
        'rule_1': 'Each player starts with 10 Energy Units.',
        'rule_2': 'Each player contributes between 0 and 10 units to the fund.',
        'rule_3': 'The fund is multiplied by 1.6.',
        'rule_4': 'The multiplied fund is split equally among the 4 players.',
        'rule_5': 'Your round payoff is: 10 minus your contribution, plus your share of the fund.',
        'intro_goal': (
            "Goal: make the Flux Capacitor exceed the 1.21 GW threshold. If the "
            "fund clears the threshold, time travel succeeds at 88 MPH. Otherwise, "
            "a time paradox is triggered."
        ),
        'intro_rounds': 'The game lasts {n} rounds. The other three players are computer-controlled.',
        'intro_start': 'Start the trip',

        'decision_header': 'FLUX CAPACITOR POWER',
        'decision_title': 'Round {r} of {n} - Your choice',
        'decision_intro': (
            "Marty, you have 10 Energy Units. How many will you contribute to the "
            "Flux Capacitor? The rest stays with you."
        ),
        'decision_slider_label': 'Units contributed to the common fund',
        'decision_min': '0 - keep it all',
        'decision_max': '10 - contribute all',
        'decision_current': 'Units contributed',
        'decision_quick': 'Quick choices',
        'decision_quick_all': 'All (10)',
        'decision_quick_half': 'Half (5)',
        'decision_quick_none': 'None (0)',
        'decision_submit': 'Contribute',

        'wait_title': 'Computing...',
        'wait_body': 'Doc is powering up the Flux Capacitor...',

        'results_header': 'ROUND RESULTS',
        'results_title': 'Round {r} of {n} - Results',
        'col_player': 'Player',
        'col_strategy': 'Strategy',
        'col_contribution': 'Contributed',
        'col_payoff': 'Payoff',
        'you_label': 'You (Marty)',
        'strategy_you': 'Free choice',
        'strategy_always_cooperate': 'Always cooperates',
        'strategy_always_defect': 'Always defects',
        'strategy_random': 'Random',
        'results_flux_title': 'Flux Capacitor Power',
        'results_flux_target': 'Target',
        'results_contrib_title': 'Contributions to the common fund',
        'results_your_decision': 'Your decision',
        'results_summary_title': 'Fund summary',
        'results_total': 'Total fund (before multiplication)',
        'results_fund': 'Multiplied fund (x 1.6)',
        'results_share': 'Your share (fund / 4)',
        'results_payoff_you': 'Your round payoff',
        'success_message': 'Time travel successful (88 MPH)!',
        'paradox_message': 'Time Paradox Triggered!',
        'units': 'units',
        'gw': 'GW',
        'results_continue': 'Next round',
    },
}


def get_lang(player):
    """Lingua scelta dal partecipante (o default dalla configurazione di sessione)."""
    return (
        player.participant.vars.get('lang')
        or player.session.config.get('default_language', 'it')
    )


def get_texts(player):
    return TEXTS[get_lang(player)]


# ---------------------------------------------------------------------------
# STRATEGIE DEI BOT E LOGICA DEL PGG
# ---------------------------------------------------------------------------

def marty_tit_for_tat_contribution(player):
    """Tit-for-tat per Marty-bot.

    Round 1 -> C.TFT_FIRST_ROUND (5 unita').
    Dal round 2 -> media (arrotondata) dei contributi degli ALTRI tre giocatori
    (Doc, Biff, Jennifer) nel round precedente.
    """
    if player.round_number == 1:
        return C.TFT_FIRST_ROUND

    prev = player.in_round(player.round_number - 1)
    others = [
        prev.doc_contribution,
        prev.biff_contribution,
        prev.jennifer_contribution,
    ]
    return int(round(sum(others) / len(others)))


def bot_contributions(player):
    """Restituisce (doc, biff, jennifer) per il round corrente."""
    doc = C.ENDOWMENT                      # always cooperate
    biff = 0                               # always defect
    jennifer = random.randint(0, C.ENDOWMENT)  # random
    return doc, biff, jennifer


def simulate(group):
    """Calcola contributi dei bot, fondo comune e payoff del round."""
    for player in group.get_players():
        player.marty_strategy = group.session.config.get('marty_strategy', 'human')

        doc, biff, jennifer = bot_contributions(player)
        player.doc_contribution = doc
        player.biff_contribution = biff
        player.jennifer_contribution = jennifer

        # Contributo di Marty: dalla dashboard (umano) oppure tit-for-tat (auto).
        marty = player.field_maybe_none('contribution')
        if marty is None:
            marty = 0
        if player.marty_strategy != 'human':
            marty = marty_tit_for_tat_contribution(player)
            player.contribution = marty

        total = float(marty + doc + biff + jennifer)
        fund = total * C.MULTIPLIER
        share = fund / C.N_PLAYERS

        player.total_contribution = total
        player.fund_energy = fund
        player.individual_share = share

        gw_per_energy = C.FLUX_TARGET_GW / (C.THRESHOLD_POT * C.MULTIPLIER)
        player.flux_power_gw = round(fund * gw_per_energy, 3)
        player.goal_reached = total >= C.THRESHOLD_POT

        player.marty_payoff = round(C.ENDOWMENT - marty + share, 2)
        player.doc_payoff = round(C.ENDOWMENT - doc + share, 2)
        player.biff_payoff = round(C.ENDOWMENT - biff + share, 2)
        player.jennifer_payoff = round(C.ENDOWMENT - jennifer + share, 2)

        player.payoff = player.marty_payoff


# ---------------------------------------------------------------------------
# PAGINE
# ---------------------------------------------------------------------------

class LanguagePage(Page):
    form_model = 'player'
    form_fields = ['lang']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        lang = get_lang(player)
        return dict(
            lang_checked_it='checked' if lang == 'it' else '',
            lang_checked_en='checked' if lang == 'en' else '',
            button_label=TEXTS['it']['start'],
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['lang'] = player.lang


class IntroPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        t = get_texts(player)
        return dict(
            texts=t,
            title=t['intro_title'],
            intro_rounds=t['intro_rounds'].format(n=C.NUM_ROUNDS),
        )


class DecisionPage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player):
        t = get_texts(player)
        return dict(
            texts=t,
            title=t['decision_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            contribution_value=(
                player.field_maybe_none('contribution')
                if player.field_maybe_none('contribution') is not None else 0
            ),
            max_contribution=C.ENDOWMENT,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = simulate

    @staticmethod
    def vars_for_template(player):
        return dict(texts=get_texts(player))


class ResultsPage(Page):
    @staticmethod
    def vars_for_template(player):
        t = get_texts(player)
        return dict(
            texts=t,
            title=t['results_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            show_bot_results=player.session.config.get('show_bot_results', False),
            contribution=player.contribution,
            doc_contribution=player.doc_contribution,
            biff_contribution=player.biff_contribution,
            jennifer_contribution=player.jennifer_contribution,
            total_contribution=round(player.total_contribution, 2),
            fund_energy=round(player.fund_energy, 2),
            individual_share=round(player.individual_share, 2),
            flux_power_gw=player.flux_power_gw,
            flux_target_gw=C.FLUX_TARGET_GW,
            marty_payoff=player.marty_payoff,
            doc_payoff=player.doc_payoff,
            biff_payoff=player.biff_payoff,
            jennifer_payoff=player.jennifer_payoff,
            result_message=(
                t['success_message'] if player.goal_reached else t['paradox_message']
            ),
            result_banner_class=(
                'retro-success' if player.goal_reached else 'retro-danger'
            ),
        )


page_sequence = [LanguagePage, IntroPage, DecisionPage, ResultsWaitPage, ResultsPage]
