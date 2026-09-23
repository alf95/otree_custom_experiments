from otree.api import *


doc = """
Coffee-Sugar Problem - Esperimento interattivo di Scelta del Consumatore ed Economia Comportamentale.

Il partecipante dispone di un budget fisso in Euro (€) e deve scegliere come allocare
le proprie risorse tra due beni complementari: Tazze di Caffè e Bustine di Zucchero.
Preferenze in stile Leontief (rapporto ideale 1:2) con gradimento in tempo reale (0-100%)
e calcolo del guadagno sperimentale finale.
"""


class C(BaseConstants):
    NAME_IN_URL = 'coffee_sugar'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Parametri economici (in Euro €)
    BUDGET = 20.00
    COFFEE_PRICE = 3.00
    SUGAR_PRICE = 1.00
    IDEAL_SUGAR_PER_COFFEE = 2

    # Limiti massimi teorici per bene
    MAX_COFFEE = int(BUDGET // COFFEE_PRICE)  # 6
    MAX_SUGAR = int(BUDGET // SUGAR_PRICE)    # 20

    # Ponderazioni del Punteggio / Soddisfazione
    POINTS_PER_PERFECT_CUP = 20.0
    POINTS_PER_BITTER_COFFEE = 4.0   # Caffè senza il giusto zucchero
    POINTS_PER_SURPLUS_SUGAR = 0.5   # Zucchero avanzato oltre la proporzione
    POINTS_PER_SAVED_EURO = 0.5      # Valore residuo di liquidità

    # Numero massimo di combinazioni ideali con il budget iniziale (20 / (3 + 2*1) = 4)
    MAX_IDEAL_CUPS = int(BUDGET // (COFFEE_PRICE + IDEAL_SUGAR_PER_COFFEE * SUGAR_PRICE))
    MAX_BENCHMARK_SCORE = MAX_IDEAL_CUPS * POINTS_PER_PERFECT_CUP  # 80.0

    # Conversione monetaria payoff:
    # Soddisfazione piena (100%) -> 15.00 € di bonus consumatore
    # Budget residuo non speso -> 25% del valore convertito in denaro (0.25 € per ogni 1.00 € risparmiato)
    SATISFACTION_MAX_BONUS = 15.00
    SAVED_BUDGET_CASH_RATE = 0.25


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Quantità scelte dal partecipante
    coffee_units = models.IntegerField(
        min=0, max=C.MAX_COFFEE, initial=0,
        doc="Unità di caffè acquistate dal partecipante"
    )
    sugar_units = models.IntegerField(
        min=0, max=C.MAX_SUGAR, initial=0,
        doc="Bustine di zucchero acquistate dal partecipante"
    )

    # Risultati economici e di utilità
    budget_spent = models.FloatField(
        initial=0.0,
        doc="Totale speso in Euro per il paniere scelto"
    )
    budget_left = models.FloatField(
        initial=C.BUDGET,
        doc="Fondi residui in Euro non spesi"
    )
    perfect_cups = models.IntegerField(
        initial=0,
        doc="Numero di tazze perfettamente bilanciate (1 caffè : 2 zuccheri)"
    )
    utility_score = models.FloatField(
        initial=0.0,
        doc="Punteggio grezzo di utilità calcolato dalla funzione di preferenza"
    )
    satisfaction_percent = models.FloatField(
        initial=0.0,
        doc="Indice di soddisfazione del consumatore normalizzato (0 - 100%)"
    )
    total_payout = models.FloatField(
        initial=0.0,
        doc="Guadagno finale in Euro accreditato al partecipante"
    )


# ---------------------------------------------------------------------------
# LOGICA ECONOMICA E FORMULE
# ---------------------------------------------------------------------------

def calculate_outcomes(coffee: int, sugar: int):
    """
    Calcola spesa, budget residuo, tazze perfette, punteggio di utilità,
    indice di soddisfazione (0-100%) e payout finale in Euro.
    """
    spent = round(coffee * C.COFFEE_PRICE + sugar * C.SUGAR_PRICE, 2)
    left = round(max(0.0, C.BUDGET - spent), 2)

    # Quante tazze perfette con rapporto 1:2
    perfect = min(coffee, sugar // C.IDEAL_SUGAR_PER_COFFEE)
    extra_coffee = coffee - perfect
    extra_sugar = sugar - (perfect * C.IDEAL_SUGAR_PER_COFFEE)

    # Funzione di preferenza quasi-lineare / complementi imperfetti:
    raw_score = (
        perfect * C.POINTS_PER_PERFECT_CUP +
        extra_coffee * C.POINTS_PER_BITTER_COFFEE +
        extra_sugar * C.POINTS_PER_SURPLUS_SUGAR +
        left * C.POINTS_PER_SAVED_EURO
    )

    # Indice percentuale di soddisfazione (con 4 tazze perfette e 0€ residui si raggiunge il 100%)
    satisfaction = min(100.0, max(0.0, (raw_score / C.MAX_BENCHMARK_SCORE) * 100.0))

    # Payout monetario in Euro:
    # Bonus soddisfazione (fino a 15.00 €) + conversione del risparmio (0.25 € per ogni € non speso)
    satisfaction_bonus = (satisfaction / 100.0) * C.SATISFACTION_MAX_BONUS
    cash_from_savings = left * C.SAVED_BUDGET_CASH_RATE
    payout = round(satisfaction_bonus + cash_from_savings, 2)

    return {
        'spent': spent,
        'left': left,
        'perfect_cups': perfect,
        'extra_coffee': extra_coffee,
        'extra_sugar': extra_sugar,
        'utility_score': round(raw_score, 2),
        'satisfaction_percent': round(satisfaction, 1),
        'total_payout': payout,
    }


# ---------------------------------------------------------------------------
# PAGINE
# ---------------------------------------------------------------------------

class Intro(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            budget=f"{C.BUDGET:.2f}".replace('.', ','),
            coffee_price=f"{C.COFFEE_PRICE:.2f}".replace('.', ','),
            sugar_price=f"{C.SUGAR_PRICE:.2f}".replace('.', ','),
            ideal_sugar=C.IDEAL_SUGAR_PER_COFFEE,
            max_ideal_cups=C.MAX_IDEAL_CUPS,
            max_payout=f"{C.SATISFACTION_MAX_BONUS:.2f}".replace('.', ','),
            savings_rate_pct=int(C.SAVED_BUDGET_CASH_RATE * 100),
        )


class GamePage(Page):
    form_model = 'player'
    form_fields = ['coffee_units', 'sugar_units']

    @staticmethod
    def error_message(player: Player, values):
        coffee = values.get('coffee_units')
        sugar = values.get('sugar_units')

        if coffee is None or coffee < 0:
            return "Il numero di tazze di caffè non può essere negativo."
        if sugar is None or sugar < 0:
            return "Il numero di bustine di zucchero non può essere negativo."

        cost = coffee * C.COFFEE_PRICE + sugar * C.SUGAR_PRICE
        if cost > C.BUDGET + 1e-4:
            return (
                f"La spesa calcolata ({cost:.2f} €) supera il tuo budget disponibile "
                f"di {C.BUDGET:.2f} €. Riduci la quantità prima di proseguire."
            )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            budget=C.BUDGET,
            budget_str=f"{C.BUDGET:.2f}".replace('.', ','),
            coffee_price=C.COFFEE_PRICE,
            coffee_price_str=f"{C.COFFEE_PRICE:.2f}".replace('.', ','),
            sugar_price=C.SUGAR_PRICE,
            sugar_price_str=f"{C.SUGAR_PRICE:.2f}".replace('.', ','),
            ideal_sugar=C.IDEAL_SUGAR_PER_COFFEE,
            max_coffee=C.MAX_COFFEE,
            max_sugar=C.MAX_SUGAR,
            max_ideal_cups=C.MAX_IDEAL_CUPS,
            max_bonus=C.SATISFACTION_MAX_BONUS,
            savings_rate=C.SAVED_BUDGET_CASH_RATE,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        coffee = player.coffee_units or 0
        sugar = player.sugar_units or 0
        results = calculate_outcomes(coffee, sugar)

        player.budget_spent = results['spent']
        player.budget_left = results['left']
        player.perfect_cups = results['perfect_cups']
        player.utility_score = results['utility_score']
        player.satisfaction_percent = results['satisfaction_percent']
        player.total_payout = results['total_payout']

        # Registrazione su player.payoff per tracking oTree standard
        player.payoff = results['total_payout']


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        coffee = player.coffee_units
        sugar = player.sugar_units
        results = calculate_outcomes(coffee, sugar)

        return dict(
            budget_str=f"{C.BUDGET:.2f}".replace('.', ','),
            coffee_units=coffee,
            sugar_units=sugar,
            coffee_price_str=f"{C.COFFEE_PRICE:.2f}".replace('.', ','),
            sugar_price_str=f"{C.SUGAR_PRICE:.2f}".replace('.', ','),
            spent_str=f"{results['spent']:.2f}".replace('.', ','),
            left_str=f"{results['left']:.2f}".replace('.', ','),
            perfect_cups=results['perfect_cups'],
            extra_coffee=results['extra_coffee'],
            extra_sugar=results['extra_sugar'],
            utility_score=results['utility_score'],
            satisfaction_percent=results['satisfaction_percent'],
            total_payout_str=f"{results['total_payout']:.2f}".replace('.', ','),
        )


page_sequence = [Intro, GamePage, Results]
