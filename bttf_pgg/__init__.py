from otree.api import *

import random


doc = """
Public Goods Game (PGG) a 4 ruoli, tema "Ritorno al Futuro", strutturato come
Collective-Risk Social Dilemma (Milinski et al., 2008, Nature).

Un partecipante umano (Marty McFly) gioca contro tre bot comportamentali
(ispirati a Fischbacher, Gächter & Fehr, 2001):
    * Doc      -> "Altruistic / Target-Pacer": versa sempre 10 unita'
    * Biff     -> "Pure Free Rider": versa sempre 0 unita'
    * Jennifer -> "Conditional Cooperator": al Round 1 versa 5 unita',
                  poi risponde alla media dei contributi degli altri partecipanti.

Regole: dotazione di 10 unita' di energia a testa per 5 round.
In ogni round il fondo comune viene moltiplicato per 1.6 e ridistribuito in parti
uguali tra i 4 giocatori: Payoff = 10 - contributo + (1.6 * fondo) / 4.

VERDETTO DEL VIAGGIO NEL TEMPO (fine gioco):
L'energia versata da tutti i partecipanti si accumula round dopo round nel Flusso
Canalizzatore verso l'obiettivo finale di 1.21 GW (soglia cumulativa di 100 unita').
- Al termine del 5° round, se la carica complessiva >= 1.21 GW, il viaggio nel
  tempo riesce ("88 MPH!") e Marty conserva tutti i guadagni accumulati.
- Se la carica e' inferiore a 1.21 GW, si innesca il Paradosso Temporale: la linea
  temporale collassa e i guadagni vengono azzerati (Collective-Risk failure).
"""


class C(BaseConstants):
    NAME_IN_URL = 'bttf_pgg'
    PLAYERS_PER_GROUP = None  # un solo gruppo con tutti i giocatori (i bot sono virtuali)

    NUM_ROUNDS = 5

    # --- Parametri economici del PGG ---
    N_PLAYERS = 4           # 1 umano (Marty) + 3 bot
    ENDOWMENT = 10          # unita' di energia iniziali per giocatore a round
    MULTIPLIER = 1.6        # fattore moltiplicativo del fondo comune di round

    # --- Narrativa "Ritorno al Futuro" & Collective-Risk Threshold ---
    FLUX_TARGET_GW = 1.21   # potenza necessaria al viaggio nel tempo
    # Contributo cumulativo minimo su 5 round da parte dell'intero gruppo (4x10x5 = 200 max)
    # per raggiungere 1.21 GW. 100 unita' corrisponde al 50% di cooperazione complessiva.
    CUMULATIVE_TARGET_ENERGY = 100

    # Percentuale del payoff conservata in caso di paradosso temporale (0.0 = collasso totale)
    PARADOX_PAYOFF_RATIO = 0.0

    # Tit-for-tat (Marty bot per test automatici): contributo del primo round.
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

    # --- Risultati del singolo round ---
    total_contribution = models.FloatField()
    fund_energy = models.FloatField()
    individual_share = models.FloatField()
    round_flux_gw = models.FloatField()

    marty_payoff = models.FloatField()
    doc_payoff = models.FloatField()
    biff_payoff = models.FloatField()
    jennifer_payoff = models.FloatField()

    # --- Monitoraggio cumulativo (intertemporale) ---
    cumulative_energy = models.FloatField()
    cumulative_gw = models.FloatField()
    energy_progress_pct = models.FloatField()
    cumulative_marty_payoff = models.FloatField()

    # --- Esito a fine gioco (Round 5) ---
    is_final_round = models.BooleanField()
    game_success = models.BooleanField()
    goal_reached = models.BooleanField()  # retrocompatibilita'
    final_game_payoff = models.FloatField()


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
            "scarico: per viaggiare nel tempo e tornare al futuro serve una potenza di almeno 1.21 GW. "
            "Insieme a te giocano altri tre abitanti di Hill Valley: Doc, Biff e Jennifer."
        ),
        'intro_2': (
            "In ciascuno dei {n} round ogni giocatore riceve 10 unita' di energia e decide "
            "quante versarne nel fondo comune per caricare il Flusso Canalizzatore."
        ),
        'intro_rules_title': 'Regole economiche e ricarica cumulativa',
        'rule_1': 'Ogni giocatore riceve 10 unita\' di energia per round (totale 50 unita\' a testa nei 5 round).',
        'rule_2': 'In ogni round puoi versare da 0 a 10 unita\' nel Flusso Canalizzatore; il resto resta nel tuo conto privato.',
        'rule_3': 'Il fondo di ciascun round viene moltiplicato per 1.6 e diviso in parti uguali tra i 4 giocatori.',
        'rule_4': 'Il tuo guadagno del round e\': 10 meno quota versata, piu\' la tua quota del fondo comune.',
        'rule_5': 'L\'energia versata da tutti si accumula round dopo round verso l\'obiettivo finale di 1.21 GW.',
        'intro_goal': (
            "Obiettivo finale: accumulare complessivamente almeno {target} unita' di energia (pari a 1.21 GW) "
            "entro il 5° round. Se a fine gioco la soglia e' raggiunta, il viaggio riesce a 88 MPH e conservi tutti "
            "i guadagni accumulati. Se la soglia non viene raggiunta, si innesca il Paradosso Temporale: la linea "
            "temporale collassa e tutti i guadagni vengono azzerati!"
        ),
        'intro_rounds': 'Il gioco dura {n} round. Gli altri tre giocatori sono controllati dal computer.',
        'intro_start': 'Inizia la missione',

        'decision_header': 'ENERGIA PER IL FLUSSO CANALIZZATORE',
        'decision_title': 'Round {r} di {n} - La tua scelta',
        'decision_intro': (
            "Marty, hai 10 unita' di energia per questo round. Quante ne versi nel Flusso "
            "Canalizzatore? Il resto va nel tuo conto privato."
        ),
        'decision_charge_status': 'Carica attuale Flusso Canalizzatore: {gw} GW / 1.21 GW ({pct}%)',
        'decision_slider_label': 'Unita\' versate nel fondo comune questo round',
        'decision_min': '0 - tengo tutto',
        'decision_max': '10 - verso tutto',
        'decision_current': 'Unita\' versate',
        'decision_quick': 'Scelte rapide',
        'decision_quick_all': 'Tutto (10)',
        'decision_quick_half': 'Meta\' (5)',
        'decision_quick_none': 'Niente (0)',
        'decision_submit': 'Versa nel fondo',

        'wait_title': 'Calcolo in corso...',
        'wait_body': 'Doc sta incanalando l\'energia nel Flusso Canalizzatore...',

        'results_header': 'RISULTATI DEL ROUND {r} DI {n}',
        'results_title': 'Round {r} di {n} - Risultati',
        'col_player': 'Giocatore',
        'col_strategy': 'Profilo',
        'col_contribution': 'Versato',
        'col_payoff': 'Guadagno round',
        'you_label': 'Tu (Marty)',
        'strategy_you': 'Scelta libera',
        'strategy_doc': 'Coopera sempre (Altruista)',
        'strategy_biff': 'Tradisce sempre (Free Rider)',
        'strategy_jennifer': 'Cooperatore Condizionato',
        'results_flux_title': 'Accumulo Energetico verso 1.21 GW',
        'results_flux_target': 'Obiettivo finale',
        'results_contrib_title': 'Contributi al fondo comune in questo round',
        'results_your_decision': 'La tua decisione di questo round',
        'results_summary_title': 'Riepilogo del round corrente',
        'results_total': 'Fondo del round (prima della moltiplicazione)',
        'results_fund': 'Fondo moltiplicato (x 1.6)',
        'results_share': 'La tua quota del fondo (diviso 4)',
        'results_payoff_you': 'Il tuo guadagno in questo round',
        'results_cumulative_payoff': 'Guadagno totale provvisorio (somma dei round)',
        'results_progress_label': 'Carica Flusso Canalizzatore:',
        'results_energy_accumulated': 'Energia totale accumulata dal gruppo: {cumul} / {target} unita\'',
        'results_interim_status': 'Doc e Marty stanno caricando il Flusso Canalizzatore. Mancano {rem_rounds} round per raggiungere 1.21 GW.',
        'results_continue': 'Prossimo round',

        # Fine gioco (Round 5)
        'final_header': 'VERDETTO FINALE DEL VIAGGIO NEL TEMPO',
        'final_success_badge': '88 MPH - VIAGGIO NEL TEMPO RIUSCITO!',
        'final_paradox_badge': 'PARADOSSO TEMPORALE INNESCATO!',
        'final_success_desc': (
            "Grande Giove! Il Flusso Canalizzatore ha raggiunto e superato la soglia di 1.21 GW! "
            "La DeLorean ha raggiunto le 88 miglia orarie e siete tornati sani e salvi nel 1985. "
            "Tutti i tuoi punti accumulati sono confermati!"
        ),
        'final_paradox_desc': (
            "Energia insufficiente! Il Flusso Canalizzatore non ha raggiunto la soglia di 1.21 GW ({gw} GW ottenuti). "
            "La DeLorean e' rimasta bloccata, la linea temporale e' collassata e i tuoi guadagni sono stati cancellati!"
        ),
        'final_total_power': 'Potenza finale raggiunta',
        'final_total_energy': 'Energia totale raccolta dal gruppo',
        'final_provisional_earnings': 'Punti accumulati nei 5 round',
        'final_actual_earnings': 'Punti finali effettivi incassati',
        'final_round_history_title': 'Cronologia completa dei 5 round',
        'col_round': 'Round',
        'col_marty_contrib': 'Tuo contributo',
        'col_group_contrib': 'Totale gruppo',
        'col_marty_round_payoff': 'Tuo payoff round',
        'final_finish_btn': 'Concludi esperimento',

        'units': 'unita\'',
        'gw': 'GW',
    },
    'en': {
        'choose_lang': 'Choose your language',
        'start': 'Inizia / Start',

        'intro_title': 'Welcome to Hill Valley, 1985!',
        'intro_1': (
            "You are Marty McFly. The DeLorean is stuck and the Flux Capacitor "
            "is drained: time travel requires at least 1.21 GW of power to return to the future. "
            "Three other residents of Hill Valley are playing with you: Doc, Biff and Jennifer."
        ),
        'intro_2': (
            "In each of the {n} rounds, every player receives 10 Energy Units and decides how "
            "many to contribute to the common fund to charge the Flux Capacitor."
        ),
        'intro_rules_title': 'Economic rules and cumulative charging',
        'rule_1': 'Each player receives 10 Energy Units per round (50 units total across 5 rounds).',
        'rule_2': 'Each round you can contribute between 0 and 10 units to the Flux Capacitor; the rest stays in your private account.',
        'rule_3': 'Each round\'s fund is multiplied by 1.6 and divided equally among the 4 players.',
        'rule_4': 'Your round payoff is: 10 minus your contribution, plus your equal share of the common fund.',
        'rule_5': 'The energy contributed by everyone accumulates round after round towards the 1.21 GW goal.',
        'intro_goal': (
            "Final Goal: collectively accumulate at least {target} Energy Units (equivalent to 1.21 GW) "
            "by the end of Round 5. If the threshold is reached, time travel succeeds at 88 MPH and you keep all "
            "your accumulated earnings. If the threshold is missed, a Time Paradox is triggered: the timeline "
            "collapses and all your earnings are wiped out!"
        ),
        'intro_rounds': 'The game lasts {n} rounds. The other three players are computer-controlled.',
        'intro_start': 'Start the mission',

        'decision_header': 'FLUX CAPACITOR POWER',
        'decision_title': 'Round {r} of {n} - Your choice',
        'decision_intro': (
            "Marty, you have 10 Energy Units for this round. How many will you contribute to the "
            "Flux Capacitor? The rest stays in your private account."
        ),
        'decision_charge_status': 'Current Flux Capacitor charge: {gw} GW / 1.21 GW ({pct}%)',
        'decision_slider_label': 'Units contributed to the common fund this round',
        'decision_min': '0 - keep all',
        'decision_max': '10 - contribute all',
        'decision_current': 'Units contributed',
        'decision_quick': 'Quick choices',
        'decision_quick_all': 'All (10)',
        'decision_quick_half': 'Half (5)',
        'decision_quick_none': 'None (0)',
        'decision_submit': 'Contribute to fund',

        'wait_title': 'Computing...',
        'wait_body': 'Doc is channeling energy into the Flux Capacitor...',

        'results_header': 'ROUND {r} OF {n} RESULTS',
        'results_title': 'Round {r} of {n} - Results',
        'col_player': 'Player',
        'col_strategy': 'Profile',
        'col_contribution': 'Contributed',
        'col_payoff': 'Round Payoff',
        'you_label': 'You (Marty)',
        'strategy_you': 'Free choice',
        'strategy_doc': 'Always Cooperate (Altruist)',
        'strategy_biff': 'Always Defect (Free Rider)',
        'strategy_jennifer': 'Conditional Cooperator',
        'results_flux_title': 'Energy Accumulation towards 1.21 GW',
        'results_flux_target': 'Final Target',
        'results_contrib_title': 'Contributions to the common fund this round',
        'results_your_decision': 'Your decision this round',
        'results_summary_title': 'Current round summary',
        'results_total': 'Round fund (before multiplication)',
        'results_fund': 'Multiplied fund (x 1.6)',
        'results_share': 'Your share of the fund (divided by 4)',
        'results_payoff_you': 'Your payoff this round',
        'results_cumulative_payoff': 'Provisional total payoff (sum of rounds)',
        'results_progress_label': 'Flux Capacitor Charge:',
        'results_energy_accumulated': 'Total group energy accumulated: {cumul} / {target} units',
        'results_interim_status': 'Doc and Marty are charging the Flux Capacitor. {rem_rounds} rounds remaining to reach 1.21 GW.',
        'results_continue': 'Next round',

        # End of game (Round 5)
        'final_header': 'FINAL TIME TRAVEL VERDICT',
        'final_success_badge': '88 MPH - TIME TRAVEL SUCCESSFUL!',
        'final_paradox_badge': 'TIME PARADOX TRIGGERED!',
        'final_success_desc': (
            "Great Scott! The Flux Capacitor reached and exceeded the 1.21 GW threshold! "
            "The DeLorean hit 88 MPH and you made it safely back to 1985. "
            "All your accumulated earnings are safely preserved!"
        ),
        'final_paradox_desc': (
            "Insufficient energy! The Flux Capacitor did not reach the 1.21 GW threshold ({gw} GW attained). "
            "The DeLorean remains stranded, the timeline collapsed, and your earnings have been wiped out!"
        ),
        'final_total_power': 'Final power reached',
        'final_total_energy': 'Total group energy collected',
        'final_provisional_earnings': 'Points accumulated over 5 rounds',
        'final_actual_earnings': 'Final actual points received',
        'final_round_history_title': 'Complete history of the 5 rounds',
        'col_round': 'Round',
        'col_marty_contrib': 'Your contribution',
        'col_group_contrib': 'Group total',
        'col_marty_round_payoff': 'Your round payoff',
        'final_finish_btn': 'Finish experiment',

        'units': 'units',
        'gw': 'GW',
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
# STRATEGIE COMPORTAMENTALI DEI BOT (Letteratura Sperimentale)
# ---------------------------------------------------------------------------

def doc_contribution(player):
    """Doc: Altruistic Cooperator / Target-Pacer (Milinski et al. 2008).
    Versa costantemente 10 unita' per assicurare la base energetica della DeLorean."""
    return C.ENDOWMENT


def biff_contribution(player):
    """Biff: Pure Free Rider (Fischbacher et al. 2001).
    Versa costantemente 0 unita' per massimizzare il proprio tornaconto privato."""
    return 0


def jennifer_conditional_contribution(player):
    """Jennifer: Conditional Cooperator (Fischbacher, Gächter & Fehr 2001).

    Round 1 -> 5 unita' (cooperazione iniziale benevola).
    Dal round 2 -> osserva i contributi degli altri partecipanti (Marty, Doc, Biff)
    nel round precedente e risponde alla media dei loro contributi.
    """
    if player.round_number == 1:
        return 5

    prev = player.in_round(player.round_number - 1)
    marty_prev = prev.contribution if prev.contribution is not None else 0
    others = [marty_prev, prev.doc_contribution, prev.biff_contribution]
    avg = sum(others) / len(others)
    return int(max(0, min(C.ENDOWMENT, round(avg))))


def marty_tit_for_tat_contribution(player):
    """Tit-for-tat per Marty-bot (sessioni/test automatici).

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


# ---------------------------------------------------------------------------
# LOGICA DI SIMULAZIONE E ACCUMULO INTERTEMPORALE
# ---------------------------------------------------------------------------

def simulate(group):
    """Calcola contributi, fondo di round, accumulo energetico e verdetto finale."""
    for player in group.get_players():
        player.marty_strategy = group.session.config.get('marty_strategy', 'human')

        doc = doc_contribution(player)
        biff = biff_contribution(player)
        jennifer = jennifer_conditional_contribution(player)

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

        # Economia del singolo round
        total = float(marty + doc + biff + jennifer)
        fund = total * C.MULTIPLIER
        share = fund / C.N_PLAYERS

        player.total_contribution = total
        player.fund_energy = fund
        player.individual_share = share

        player.marty_payoff = round(C.ENDOWMENT - marty + share, 2)
        player.doc_payoff = round(C.ENDOWMENT - doc + share, 2)
        player.biff_payoff = round(C.ENDOWMENT - biff + share, 2)
        player.jennifer_payoff = round(C.ENDOWMENT - jennifer + share, 2)

        # Accumulo energetico progressivo
        prev_rounds = player.in_previous_rounds()
        cumul_energy = sum(p.total_contribution for p in prev_rounds) + total
        player.cumulative_energy = round(cumul_energy, 2)

        # Potenza del Flusso Canalizzatore (GW cumulati verso 1.21 GW)
        gw_ratio = cumul_energy / C.CUMULATIVE_TARGET_ENERGY
        player.cumulative_gw = round(gw_ratio * C.FLUX_TARGET_GW, 3)
        player.round_flux_gw = player.cumulative_gw
        player.energy_progress_pct = round(min(100.0, gw_ratio * 100.0), 1)

        # Somma provvisoria dei payoff di Marty nei round giocati
        cumul_marty_payoff = sum(p.marty_payoff for p in prev_rounds) + player.marty_payoff
        player.cumulative_marty_payoff = round(cumul_marty_payoff, 2)

        # Gestione round finale (Round 5) vs round intermedi (1..4)
        is_final = (player.round_number == C.NUM_ROUNDS)
        player.is_final_round = is_final

        if is_final:
            success = (cumul_energy >= C.CUMULATIVE_TARGET_ENERGY)
            player.game_success = success
            player.goal_reached = success

            if success:
                player.final_game_payoff = player.cumulative_marty_payoff
                player.payoff = player.marty_payoff
            else:
                player.final_game_payoff = round(player.cumulative_marty_payoff * C.PARADOX_PAYOFF_RATIO, 2)
                # Collasso da Paradosso Temporale: azzera i payoff accumulati nei round precedenti
                for p in prev_rounds:
                    p.payoff = 0.0
                player.payoff = player.final_game_payoff
        else:
            player.game_success = False
            player.goal_reached = False
            player.final_game_payoff = 0.0
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
            intro_1=t['intro_1'],
            intro_2=t['intro_2'].format(n=C.NUM_ROUNDS),
            intro_goal=t['intro_goal'].format(target=C.CUMULATIVE_TARGET_ENERGY),
            intro_rounds=t['intro_rounds'].format(n=C.NUM_ROUNDS),
        )


class DecisionPage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player):
        t = get_texts(player)
        prev_rounds = player.in_previous_rounds()
        current_cumul_gw = 0.0
        current_pct = 0.0
        if prev_rounds:
            last_round = prev_rounds[-1]
            current_cumul_gw = last_round.cumulative_gw
            current_pct = last_round.energy_progress_pct

        status_text = t['decision_charge_status'].format(
            gw=current_cumul_gw, pct=current_pct
        )

        return dict(
            texts=t,
            title=t['decision_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            decision_charge_status=status_text,
            show_charge_status=(player.round_number > 1),
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
        is_final = (player.round_number == C.NUM_ROUNDS)
        rounds_remaining = max(0, C.NUM_ROUNDS - player.round_number)

        round_history = []
        if is_final:
            all_rounds = player.in_all_rounds()
            for r in all_rounds:
                round_history.append({
                    'round': r.round_number,
                    'marty_contrib': r.contribution,
                    'group_total': round(r.total_contribution, 1),
                    'marty_payoff': r.marty_payoff,
                })

        return dict(
            texts=t,
            title=t['results_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            is_final_round=is_final,
            show_bot_results=player.session.config.get('show_bot_results', False),

            # Round corrente
            contribution=player.contribution,
            doc_contribution=player.doc_contribution,
            biff_contribution=player.biff_contribution,
            jennifer_contribution=player.jennifer_contribution,
            total_contribution=round(player.total_contribution, 2),
            fund_energy=round(player.fund_energy, 2),
            individual_share=round(player.individual_share, 2),
            marty_payoff=player.marty_payoff,
            doc_payoff=player.doc_payoff,
            biff_payoff=player.biff_payoff,
            jennifer_payoff=player.jennifer_payoff,

            # Progresso cumulativo
            cumulative_energy=player.cumulative_energy,
            cumulative_target_energy=C.CUMULATIVE_TARGET_ENERGY,
            cumulative_gw=player.cumulative_gw,
            flux_target_gw=C.FLUX_TARGET_GW,
            energy_progress_pct=player.energy_progress_pct,
            cumulative_marty_payoff=player.cumulative_marty_payoff,
            rounds_remaining=rounds_remaining,
            interim_status_text=t['results_interim_status'].format(rem_rounds=rounds_remaining),
            energy_accumulated_text=t['results_energy_accumulated'].format(
                cumul=player.cumulative_energy, target=C.CUMULATIVE_TARGET_ENERGY
            ),

            # Esito finale
            game_success=player.game_success,
            final_game_payoff=player.final_game_payoff,
            round_history=round_history,
        )


page_sequence = [LanguagePage, IntroPage, DecisionPage, ResultsWaitPage, ResultsPage]
