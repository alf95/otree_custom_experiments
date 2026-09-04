from otree.api import *

import random


doc = """
Public Goods Game (PGG) a 4 ruoli, tema "Ritorno al Futuro", strutturato come
Collective-Risk Social Dilemma (Milinski et al., 2008, Nature).
Versione didattica ed intuitiva adattata per ragazzi dai 10 ai 18 anni con
dotazione monetaria tangibile (Monete / Salvadanaio personale).

Un partecipante umano (Marty McFly) gioca contro tre bot con caratteri ben distinti:
    * Doc      -> Generoso / Altruista: dona sempre 10 monete
    * Biff     -> Egoista / Free Rider: tiene tutto per sé e dona 0 monete
    * Jennifer -> Reciproca / Cooperatrice Condizionata: al Round 1 dona 5 monete,
                  poi osserva cosa fanno gli altri e dona quanto la media del gruppo.

Regole: dotazione di 10 Monete a testa per 5 round.
Le monete NON donate rimangono al sicuro nel Salvadanaio personale del giocatore.
Le monete donate alla Cassa comune per la DeLorean vengono moltiplicate per 1.6
grazie alle invenzioni di Doc e divise equamente tra i 4 giocatori.
Guadagno round = (10 - monete donate) + (1.6 * cassa comune) / 4.

VERDETTO FINALE DEL VIAGGIO NEL TEMPO:
Tutte le monete donate dal gruppo servono a caricare la DeLorean (100 monete = 1.21 GW).
- Se al 5° round il gruppo ha raccolto almeno 100 monete (1.21 GW), la DeLorean
  raggiunge le 88 MPH: viaggio riuscito e Marty incassa tutte le monete del suo salvadanaio!
- Se il gruppo ha raccolto meno di 100 monete, scatta il Paradosso Temporale:
  la DeLorean resta bloccata e tutti i guadagni vengono azzerati (rischio collettivo).
"""


class C(BaseConstants):
    NAME_IN_URL = 'bttf_pgg'
    PLAYERS_PER_GROUP = None  # un solo gruppo con tutti i giocatori (i bot sono virtuali)

    NUM_ROUNDS = 5

    # --- Parametri economici del PGG ---
    N_PLAYERS = 4           # 1 umano (Marty) + 3 bot
    ENDOWMENT = 10          # Monete iniziali per giocatore a ogni round
    MULTIPLIER = 1.6        # Fattore moltiplicativo della cassa comune

    # --- Narrativa "Ritorno al Futuro" & Collective-Risk Threshold ---
    FLUX_TARGET_GW = 1.21   # Potenza necessaria al viaggio nel tempo
    # Monete complessive da donare in 5 round dall'intero gruppo (4x10x5 = 200 max)
    # per raggiungere 1.21 GW. 100 monete corrisponde al 50% di cooperazione complessiva.
    CUMULATIVE_TARGET_MONEY = 100
    CUMULATIVE_TARGET_ENERGY = 100  # Alias per retrocompatibilità

    # Percentuale del payoff conservata in caso di paradosso temporale (0.0 = perdita totale)
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
# Linguaggio semplice, chiaro ed intuitivo per ragazzi di 10-18 anni.
# ---------------------------------------------------------------------------

TEXTS = {
    'it': {
        'choose_lang': 'Scegli la lingua',
        'start': 'Inizia / Start',

        'intro_title': 'Benvenuto a Hill Valley, 1985!',
        'intro_1': (
            "Sei Marty McFly! La DeLorean è ferma e il Flusso Canalizzatore è scarico: "
            "per far partire la macchina del tempo e tornare al futuro serve una carica di 1.21 GW. "
            "Per riuscirci, Doc Brown ha bisogno di fondi per alimentare l'esperimento. "
            "Insieme a te partecipano altri tre ragazzi di Hill Valley: Doc, Biff e Jennifer."
        ),
        'intro_2': (
            "Il gioco dura {n} round. All'inizio di ogni round ricevi 10 Monete personali (🪙). "
            "Sei tu a scegliere quante monete tenere nel tuo Salvadanaio e quante donarne alla "
            "Cassa comune per la DeLorean!"
        ),
        'intro_rules_title': 'Come funziona il gioco: Monete e Macchina del Tempo',
        'rule_1': "🪙 La tua dotazione: a ogni round ricevi 10 Monete. Sono tue!",
        'rule_2': "🔒 Il tuo Salvadanaio: le monete che decidi di NON donare restano al sicuro nel tuo salvadanaio personale.",
        'rule_3': "⚡ Cassa della DeLorean: le monete donate da te e dagli altri vengono messe insieme e moltiplicate per 1.6 da Doc (crescono del 60%!). Il totale viene poi diviso in 4 parti uguali tra tutti i giocatori.",
        'rule_4': "💰 Il tuo guadagno a ogni round: Monete che hai tenuto per te + la tua parte della cassa comune.",
        'rule_5': "🚀 Ricarica collettiva: tutte le monete donate dal gruppo si sommano per caricare la DeLorean fino all'obiettivo di 1.21 GW (100 monete in totale).",
        'intro_goal': (
            "Obiettivo di squadra: donare almeno {target} Monete in totale entro la fine del 5° round per raggiungere 1.21 GW. "
            "Se il gruppo ce la fa, la DeLorean sfreccia a 88 MPH nel tempo e porti a casa tutte le monete del tuo salvadanaio! "
            "Ma attenzione: se il gruppo dona meno di {target} monete, scatta il Paradosso Temporale: la macchina non parte e tutte le monete accumulate svaniscono!"
        ),
        'intro_rounds': "Giocherai per {n} round. Doc, Biff e Jennifer sono guidati dal computer, ciascuno con il proprio carattere:",
        'intro_chars_title': "I tuoi compagni di gioco a Hill Valley",
        'char_doc': "Doc Brown (Generoso): crede nella scienza e dona sempre tutte le sue 10 monete.",
        'char_biff': "Biff Tannen (Egoista): pensa solo a sé, tiene tutto e dona sempre 0 monete.",
        'char_jennifer': "Jennifer Parker (Reciproca): parte donando 5 monete, poi dona quanto vede fare agli altri.",
        'intro_start': "Inizia l'avventura!",

        'decision_header': 'MISSIONE DE LOREAN: LA TUA SCELTA',
        'decision_title': 'Round {r} di {n} - Quante monete doni?',
        'decision_intro': (
            "Marty, hai 10 Monete per questo round! Decidi quante tenerne nel tuo Salvadanaio "
            "e quante donarne alla Cassa comune per caricare la DeLorean."
        ),
        'decision_charge_status': 'Carica attuale della DeLorean: {gw} GW / 1.21 GW ({pct}% - {cumul}/{target} monete raccolte finora)',
        'decision_box_keep_title': 'Nel tuo Salvadanaio',
        'decision_box_keep_desc': 'Monete sicure che tieni per te',
        'decision_box_give_title': 'Nella Cassa per la DeLorean',
        'decision_box_give_desc': 'Monete che doni alla missione comune',
        'decision_slider_label': 'Trascina il cursore per scegliere quante monete donare:',
        'decision_min': '0 monete (tieni tutto)',
        'decision_max': '10 monete (dona tutto)',
        'decision_quick': 'Scelte veloci',
        'decision_quick_none': 'Tieni tutto (0)',
        'decision_quick_half': 'Metà e metà (5)',
        'decision_quick_all': 'Dona tutto (10)',
        'decision_submit': 'Conferma la scelta',

        'wait_title': 'Calcolo in corso...',
        'wait_body': 'Doc Brown sta raccogliendo le monete e alimentando il Flusso Canalizzatore...',

        'results_header': 'RISULTATI DEL ROUND {r} DI {n}',
        'results_title': 'Round {r} di {n} - Resoconto',
        'col_player': 'Giocatore',
        'col_strategy': 'Carattere',
        'col_contribution': 'Monete donate',
        'col_payoff': 'Guadagno round',
        'you_label': 'Tu (Marty)',
        'strategy_you': 'La tua scelta',
        'strategy_doc': 'Generoso (dona sempre 10)',
        'strategy_biff': 'Egoista (dona sempre 0)',
        'strategy_jennifer': 'Reciproca (segue il gruppo)',
        'results_flux_title': 'Carica della DeLorean verso 1.21 GW',
        'results_flux_target': 'Obiettivo finale',
        'results_contrib_title': 'Le decisioni del gruppo in questo round',
        'results_your_decision': 'La tua decisione in questo round',
        'results_summary_title': 'Come è stato calcolato il tuo guadagno',
        'results_kept': 'Monete tenute nel tuo salvadanaio (10 - donate)',
        'results_total': 'Monete totali donate da tutti i 4 giocatori',
        'results_fund': 'Cassa comune moltiplicata da Doc (x 1.6)',
        'results_share': 'La tua quota della cassa comune (diviso 4)',
        'results_payoff_you': 'Totale guadagnato in questo round',
        'results_cumulative_payoff': 'Monete totali nel tuo salvadanaio finora',
        'results_progress_label': 'Carica Flusso Canalizzatore:',
        'results_energy_accumulated': 'Monete totali donate dal gruppo: {cumul} / {target} monete',
        'results_interim_status': 'Mancano {rem_rounds} round per raggiungere le 100 monete (1.21 GW) per far partire la DeLorean.',
        'results_continue': 'Prossimo round',

        # Fine gioco (Round 5)
        'final_header': 'VERDETTO FINALE: LA DE LOREAN PARTE?',
        'final_success_badge': '88 MPH - VIAGGIO NEL TEMPO RIUSCITO!',
        'final_paradox_badge': 'PARADOSSO TEMPORALE! LA MACCHINA NON PARTE!',
        'final_success_desc': (
            "Grande Giove! Il gruppo ha collaborato e la DeLorean ha superato 1.21 GW di potenza! "
            "La macchina ha raggiunto le 88 miglia orarie e siete tornati sani e salvi nel futuro. "
            "Tutte le monete accumulate nel tuo salvadanaio sono tue!"
        ),
        'final_paradox_desc': (
            "Energia insufficiente! Il gruppo ha donato {cumul} monete su 100 ({gw} GW ottenuti), senza raggiungere 1.21 GW. "
            "La DeLorean è rimasta a secco, il tempo è collassato e purtroppo tutte le monete accumulate sono andate perdute!"
        ),
        'final_total_power': 'Potenza finale raggiunta',
        'final_total_energy': 'Monete totali raccolte dal gruppo',
        'final_provisional_earnings': 'Monete accumulate nei 5 round',
        'final_actual_earnings': 'Monete finali che porti a casa',
        'final_round_history_title': 'Cronologia completa dei 5 round',
        'col_round': 'Round',
        'col_marty_contrib': 'Monete donate da te',
        'col_group_contrib': 'Totale donato dal gruppo',
        'col_marty_round_payoff': 'Tuo guadagno round',
        'final_finish_btn': 'Concludi la missione',

        'units': 'monete',
        'gw': 'GW',
    },
    'en': {
        'choose_lang': 'Choose your language',
        'start': 'Inizia / Start',

        'intro_title': 'Welcome to Hill Valley, 1985!',
        'intro_1': (
            "You are Marty McFly! The DeLorean is stranded and the Flux Capacitor is empty: "
            "to power the time machine and get back to the future, you need 1.21 GW of power. "
            "Doc Brown needs funding to fuel the experiment. "
            "Three other Hill Valley friends are playing with you: Doc, Biff, and Jennifer."
        ),
        'intro_2': (
            "The game lasts {n} rounds. At the start of each round, you receive 10 personal Coins (🪙). "
            "You decide how many coins to keep safely in your Piggy Bank and how many to donate "
            "to the DeLorean Fund!"
        ),
        'intro_rules_title': 'How the game works: Coins and the Time Machine',
        'rule_1': "🪙 Your endowment: each round you receive 10 Coins. They are yours!",
        'rule_2': "🔒 Your Piggy Bank: coins you choose NOT to donate stay safe in your personal piggy bank.",
        'rule_3': "⚡ DeLorean Fund: coins donated by you and the others are combined and multiplied by 1.6 by Doc (a 60% boost!). The total is split equally among all 4 players.",
        'rule_4': "💰 Your earnings each round: Coins kept in your piggy bank + your equal share of the DeLorean fund.",
        'rule_5': "🚀 Team target: all coins donated by the group accumulate across rounds towards the 1.21 GW goal (100 coins in total).",
        'intro_goal': (
            "Team Goal: donate at least {target} Coins in total by the end of Round 5 to reach 1.21 GW. "
            "If the team succeeds, the DeLorean hits 88 MPH and you take home all coins saved in your piggy bank! "
            "Warning: if the group donates fewer than {target} coins, a Time Paradox triggers: the car is stranded and all saved coins are wiped out!"
        ),
        'intro_rounds': "You play for {n} rounds. Doc, Biff, and Jennifer are computer-controlled, each with their own personality:",
        'intro_chars_title': "Your fellow players in Hill Valley",
        'char_doc': "Doc Brown (Generous): believes in science and always donates all his 10 coins.",
        'char_biff': "Biff Tannen (Selfish): thinks only of himself, keeps everything and donates 0 coins.",
        'char_jennifer': "Jennifer Parker (Reciprocal): starts by donating 5 coins, then copies what the group does.",
        'intro_start': "Start the Adventure!",

        'decision_header': 'DELOREAN MISSION: YOUR CHOICE',
        'decision_title': 'Round {r} of {n} - How many coins do you donate?',
        'decision_intro': (
            "Marty, you received 10 Coins for this round! Decide how many to keep in your Piggy Bank "
            "and how many to contribute to the DeLorean Fund."
        ),
        'decision_charge_status': 'Current DeLorean charge: {gw} GW / 1.21 GW ({pct}% - {cumul}/{target} coins collected so far)',
        'decision_box_keep_title': 'In your Piggy Bank',
        'decision_box_keep_desc': 'Coins kept safely for yourself',
        'decision_box_give_title': 'In the DeLorean Fund',
        'decision_box_give_desc': 'Coins contributed to the team mission',
        'decision_slider_label': 'Move the slider to choose how many coins to donate:',
        'decision_min': '0 coins (keep all)',
        'decision_max': '10 coins (donate all)',
        'decision_quick': 'Quick choices',
        'decision_quick_none': 'Keep all (0)',
        'decision_quick_half': 'Half & Half (5)',
        'decision_quick_all': 'Donate all (10)',
        'decision_submit': 'Confirm choice',

        'wait_title': 'Calculating...',
        'wait_body': 'Doc Brown is collecting the coins and powering up the Flux Capacitor...',

        'results_header': 'ROUND {r} OF {n} RESULTS',
        'results_title': 'Round {r} of {n} - Summary',
        'col_player': 'Player',
        'col_strategy': 'Personality',
        'col_contribution': 'Coins donated',
        'col_payoff': 'Round earnings',
        'you_label': 'You (Marty)',
        'strategy_you': 'Your choice',
        'strategy_doc': 'Generous (always donates 10)',
        'strategy_biff': 'Selfish (always donates 0)',
        'strategy_jennifer': 'Reciprocal (follows group)',
        'results_flux_title': 'DeLorean Charge towards 1.21 GW',
        'results_flux_target': 'Final Target',
        'results_contrib_title': 'Group decisions in this round',
        'results_your_decision': 'Your decision in this round',
        'results_summary_title': 'How your earnings were calculated',
        'results_kept': 'Coins kept in your piggy bank (10 - donated)',
        'results_total': 'Total coins donated by all 4 players',
        'results_fund': 'DeLorean fund multiplied by Doc (x 1.6)',
        'results_share': 'Your share of the fund (divided by 4)',
        'results_payoff_you': 'Total earned in this round',
        'results_cumulative_payoff': 'Total coins in your piggy bank so far',
        'results_progress_label': 'Flux Capacitor Charge:',
        'results_energy_accumulated': 'Total group coins donated: {cumul} / {target} coins',
        'results_interim_status': '{rem_rounds} rounds left to collect the 100 coins (1.21 GW) required to start the DeLorean.',
        'results_continue': 'Next round',

        # End of game (Round 5)
        'final_header': 'FINAL VERDICT: DOES THE DELOREAN START?',
        'final_success_badge': '88 MPH - TIME TRAVEL SUCCESSFUL!',
        'final_paradox_badge': 'TIME PARADOX! THE CAR DOES NOT START!',
        'final_success_desc': (
            "Great Scott! The group worked together and the DeLorean exceeded 1.21 GW of power! "
            "The car reached 88 MPH and you safely returned to the future. "
            "All the coins accumulated in your piggy bank are yours!"
        ),
        'final_paradox_desc': (
            "Not enough power! The group contributed {cumul} out of 100 coins ({gw} GW attained), falling short of 1.21 GW. "
            "The DeLorean was stranded, time collapsed, and all your saved coins were lost!"
        ),
        'final_total_power': 'Final power reached',
        'final_total_energy': 'Total coins gathered by the team',
        'final_provisional_earnings': 'Coins accumulated over 5 rounds',
        'final_actual_earnings': 'Final coins you take home',
        'final_round_history_title': 'Complete history of all 5 rounds',
        'col_round': 'Round',
        'col_marty_contrib': 'Coins you donated',
        'col_group_contrib': 'Total team donated',
        'col_marty_round_payoff': 'Your round earnings',
        'final_finish_btn': 'Complete Mission',

        'units': 'coins',
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
    Dona costantemente 10 monete per assicurare la missione della DeLorean."""
    return C.ENDOWMENT


def biff_contribution(player):
    """Biff: Pure Free Rider (Fischbacher et al. 2001).
    Dona costantemente 0 monete per tenere tutto nel proprio salvadanaio."""
    return 0


def jennifer_conditional_contribution(player):
    """Jennifer: Conditional Cooperator (Fischbacher, Gächter & Fehr 2001).

    Round 1 -> 5 monete (cooperazione iniziale amichevole).
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

    Round 1 -> C.TFT_FIRST_ROUND (5 monete).
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
    """Calcola contributi, cassa di round, carica DeLorean e verdetto finale."""
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

        # Accumulo monete progressivo (carica della DeLorean)
        prev_rounds = player.in_previous_rounds()
        cumul_energy = sum(p.total_contribution for p in prev_rounds) + total
        player.cumulative_energy = round(cumul_energy, 2)

        # Potenza del Flusso Canalizzatore (GW cumulati verso 1.21 GW)
        gw_ratio = cumul_energy / C.CUMULATIVE_TARGET_ENERGY
        player.cumulative_gw = round(gw_ratio * C.FLUX_TARGET_GW, 3)
        player.round_flux_gw = player.cumulative_gw
        player.energy_progress_pct = round(min(100.0, gw_ratio * 100.0), 1)

        # Somma provvisoria dei payoff di Marty nei round giocati (Salvadanaio)
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
            intro_goal=t['intro_goal'].format(target=C.CUMULATIVE_TARGET_MONEY),
            intro_rounds=t['intro_rounds'].format(n=C.NUM_ROUNDS),
            target_money=C.CUMULATIVE_TARGET_MONEY,
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
        current_cumul_coins = 0
        if prev_rounds:
            last_round = prev_rounds[-1]
            current_cumul_gw = last_round.cumulative_gw
            current_pct = last_round.energy_progress_pct
            current_cumul_coins = int(last_round.cumulative_energy)

        status_text = t['decision_charge_status'].format(
            gw=current_cumul_gw,
            pct=current_pct,
            cumul=current_cumul_coins,
            target=C.CUMULATIVE_TARGET_MONEY,
        )

        contrib_val = player.field_maybe_none('contribution')
        if contrib_val is None:
            contrib_val = 0
        kept_val = C.ENDOWMENT - contrib_val

        return dict(
            texts=t,
            title=t['decision_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            decision_charge_status=status_text,
            show_charge_status=(player.round_number > 1),
            contribution_value=contrib_val,
            kept_value=kept_val,
            max_contribution=C.ENDOWMENT,
            endowment=C.ENDOWMENT,
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

        marty_contrib = player.contribution if player.contribution is not None else 0
        marty_kept = round(C.ENDOWMENT - marty_contrib, 2)

        final_paradox_text = t['final_paradox_desc'].format(
            gw=player.cumulative_gw,
            cumul=int(player.cumulative_energy),
        )

        return dict(
            texts=t,
            title=t['results_title'].format(r=player.round_number, n=C.NUM_ROUNDS),
            is_final_round=is_final,
            show_bot_results=player.session.config.get('show_bot_results', False),

            # Round corrente
            contribution=marty_contrib,
            marty_kept=marty_kept,
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
            cumulative_energy=int(player.cumulative_energy),
            cumulative_target_energy=C.CUMULATIVE_TARGET_MONEY,
            cumulative_gw=player.cumulative_gw,
            flux_target_gw=C.FLUX_TARGET_GW,
            energy_progress_pct=player.energy_progress_pct,
            cumulative_marty_payoff=player.cumulative_marty_payoff,
            rounds_remaining=rounds_remaining,
            interim_status_text=t['results_interim_status'].format(rem_rounds=rounds_remaining),
            energy_accumulated_text=t['results_energy_accumulated'].format(
                cumul=int(player.cumulative_energy), target=C.CUMULATIVE_TARGET_MONEY
            ),

            # Esito finale
            game_success=player.game_success,
            final_paradox_text=final_paradox_text,
            final_game_payoff=player.final_game_payoff,
            round_history=round_history,
        )


page_sequence = [LanguagePage, IntroPage, DecisionPage, ResultsWaitPage, ResultsPage]
