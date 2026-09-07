from otree.api import *


doc = """
Pizzagame - Public Goods Game (PGG) classico adattato per bambini (6-9 anni).

Un bambino (Tu) gioca insieme a tre amici controllati dal computer:
    * Il Goloso         -> tiene sempre tutto per sé (0 fette nel Piatto Condiviso)
    * Il Generoso       -> mette sempre tutte le sue 5 fette nel Piatto Condiviso
    * L'Amico Reciproco -> al primo round mette 3 fette, poi mette quanto la media
                           delle fette messe dagli altri nel round precedente

Regole: a ogni round ogni bambino riceve 5 fette di pizza.
Le fette che NON metti nel Piatto Condiviso restano per te.
Le fette messe nel Piatto Condiviso vengono RADDOPPIATE (x2) e poi divise
in 4 parti uguali tra tutti i bambini.
Fette che mangi = fette tenute per te + la tua parte del piatto raddoppiato.
"""


class C(BaseConstants):
    NAME_IN_URL = 'pizza_pgg'
    # I 3 bot sono virtuali e vengono simulati in `simulate()`: ogni
    # partecipante che apre lo stesso link gioca autonomamente contro i bot.
    PLAYERS_PER_GROUP = None

    NUM_ROUNDS = 5

    # --- Parametri economici del PGG ---
    N_PLAYERS = 4           # 1 umano (Tu) + 3 bot
    ENDOWMENT = 5           # Fette di pizza iniziali per ogni bambino a ogni round
    MULTIPLIER = 2          # Le fette nel Piatto Condiviso vengono raddoppiate

    # --- Strategie dei bot ---
    GOLOSO_CONTRIBUTION = 0
    GENEROSO_CONTRIBUTION = 5
    RECIPROCO_FIRST_ROUND = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- Scelta del bambino ---
    contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT,
    )

    # --- Fette messe nel Piatto Condiviso dai tre bot ---
    goloso_contribution = models.IntegerField()
    generoso_contribution = models.IntegerField()
    reciproco_contribution = models.IntegerField()

    # --- Risultati del singolo round ---
    total_contribution = models.FloatField()
    fund = models.FloatField()
    individual_share = models.FloatField()

    human_payoff = models.FloatField()
    goloso_payoff = models.FloatField()
    generoso_payoff = models.FloatField()
    reciproco_payoff = models.FloatField()

    # --- Monitoraggio cumulativo ---
    cumulative_human = models.FloatField()
    cumulative_group = models.FloatField()

    is_final_round = models.BooleanField()


# ---------------------------------------------------------------------------
# STRATEGIE COMPORTAMENTALI DEI BOT
# ---------------------------------------------------------------------------

def goloso_contribution(player):
    """Il Goloso: tiene sempre tutto per sé e non mette mai fette nel piatto."""
    return C.GOLOSO_CONTRIBUTION


def generoso_contribution(player):
    """Il Generoso: mette sempre tutte le sue fette nel Piatto Condiviso."""
    return C.GENEROSO_CONTRIBUTION


def reciproco_contribution(player):
    """L'Amico Reciproco: al primo round mette 3 fette; poi mette quanto la
    media (arrotondata) delle fette messe dagli ALTRI tre bambini nel round
    precedente (Tu, Il Goloso, Il Generoso)."""
    if player.round_number == 1:
        return C.RECIPROCO_FIRST_ROUND

    prev = player.in_round(player.round_number - 1)
    human_prev = prev.contribution if prev.contribution is not None else 0
    others = [human_prev, prev.goloso_contribution, prev.generoso_contribution]
    avg = sum(others) / len(others)
    return int(max(0, min(C.ENDOWMENT, round(avg))))


# ---------------------------------------------------------------------------
# FORMATTAZIONE DELLE FETTE (per i bambini)
# ---------------------------------------------------------------------------

def format_slices(x):
    """Trasforma un numero di fette in una scritta semplice per i bambini.

    Esempi: 3 -> '3 fette', 1 -> '1 fetta', 2.5 -> '2 fette e mezza',
    0.5 -> 'mezza fetta'.
    """
    x = round(float(x), 2)
    whole = int(x)
    frac = x - whole
    if frac < 1e-9:
        return f"{whole} fette" if whole != 1 else "1 fetta"
    if whole == 0:
        return "mezza fetta"
    return f"{whole} fette e mezza" if whole != 1 else f"{whole} fetta e mezza"


# ---------------------------------------------------------------------------
# LOGICA DI SIMULAZIONE
# ---------------------------------------------------------------------------

def simulate(player):
    """Calcola le fette dei bot, il Piatto Condiviso raddoppiato e quante
    fette mangia ogni bambino nel round.

    Opera sul SINGOLO giocatore (non sul gruppo): ogni partecipante gioca
    autonomamente contro i bot, senza attendere altri umani.
    """
    goloso = goloso_contribution(player)
    generoso = generoso_contribution(player)
    reciproco = reciproco_contribution(player)

    player.goloso_contribution = goloso
    player.generoso_contribution = generoso
    player.reciproco_contribution = reciproco

    human = player.field_maybe_none('contribution')
    if human is None:
        human = 0

    # Economia del singolo round
    total = float(human + goloso + generoso + reciproco)
    fund = total * C.MULTIPLIER
    share = fund / C.N_PLAYERS

    player.total_contribution = total
    player.fund = fund
    player.individual_share = share

    player.human_payoff = round(C.ENDOWMENT - human + share, 2)
    player.goloso_payoff = round(C.ENDOWMENT - goloso + share, 2)
    player.generoso_payoff = round(C.ENDOWMENT - generoso + share, 2)
    player.reciproco_payoff = round(C.ENDOWMENT - reciproco + share, 2)

    # Accumulo tra i round
    prev_rounds = player.in_previous_rounds()
    player.cumulative_human = round(
        sum(p.human_payoff for p in prev_rounds) + player.human_payoff, 2
    )
    player.cumulative_group = round(
        sum(p.total_contribution for p in prev_rounds) + total, 2
    )

    player.is_final_round = (player.round_number == C.NUM_ROUNDS)

    # Il payoff del round viene sempre accreditato: `participant.payoff`
    # somma automaticamente al totale accumulato.
    player.payoff = player.human_payoff


# ---------------------------------------------------------------------------
# PAGINE
# ---------------------------------------------------------------------------

class Istruzioni(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        return dict(
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
            n_players=C.N_PLAYERS,
        )


class Decisione(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player):
        contrib_val = player.field_maybe_none('contribution')
        if contrib_val is None:
            contrib_val = 0

        cumulative = 0
        if player.round_number > 1:
            prev = player.in_round(player.round_number - 1)
            cumulative = prev.cumulative_human or 0

        options = []
        for n in range(C.ENDOWMENT + 1):
            options.append({
                'value': n,
                'emoji': '🍕' * n,
                'label': format_slices(n),
            })

        return dict(
            round_number=player.round_number,
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            contribution_value=contrib_val,
            kept_value=C.ENDOWMENT - contrib_val,
            cumulative_human=cumulative,
            cumulative_human_text=format_slices(cumulative),
            options=options,
        )


class Risultati(Page):
    @staticmethod
    def vars_for_template(player):
        # La simulazione va eseguita QUI (prima del rendering), perche'
        # `vars_for_template` viene chiamato prima di `before_next_page`.
        simulate(player)

        human = player.contribution if player.contribution is not None else 0
        human_kept = C.ENDOWMENT - human

        kids = [
            dict(
                avatar='🧒', name='Tu',
                contribution=human,
                payoff=player.human_payoff,
                payoff_text=format_slices(player.human_payoff),
                is_you=True,
            ),
            dict(
                avatar='😋', name='Il Goloso',
                contribution=player.goloso_contribution,
                payoff=player.goloso_payoff,
                payoff_text=format_slices(player.goloso_payoff),
                is_you=False,
            ),
            dict(
                avatar='😊', name='Il Generoso',
                contribution=player.generoso_contribution,
                payoff=player.generoso_payoff,
                payoff_text=format_slices(player.generoso_payoff),
                is_you=False,
            ),
            dict(
                avatar='🤝', name="L'Amico Reciproco",
                contribution=player.reciproco_contribution,
                payoff=player.reciproco_payoff,
                payoff_text=format_slices(player.reciproco_payoff),
                is_you=False,
            ),
        ]

        return dict(
            round_number=player.round_number,
            num_rounds=C.NUM_ROUNDS,
            is_final_round=player.is_final_round,
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
            n_players=C.N_PLAYERS,

            kids=kids,
            human_contribution=human,
            human_kept=human_kept,
            total_contribution=round(player.total_contribution, 2),
            fund=round(player.fund, 2),
            individual_share=round(player.individual_share, 2),

            cumulative_human=player.cumulative_human,
            cumulative_group=round(player.cumulative_group, 2),

            human_payoff_text=format_slices(player.human_payoff),
            human_kept_text=format_slices(human_kept),
            share_text=format_slices(player.individual_share),
            cumulative_human_text=format_slices(player.cumulative_human),
        )


page_sequence = [Istruzioni, Decisione, Risultati]
