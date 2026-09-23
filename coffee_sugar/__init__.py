from otree.api import *


doc = """
Esperimento di Economia Comportamentale - La Trappola Cognitiva "Caffè & Zucchero".
Adattamento del celebre problema della "Mazza e Pallina" (Cognitive Reflection Test - CRT)
introdotto da Shane Frederick e reso celebre dal premio Nobel Daniel Kahneman.

Il partecipante affronta la domanda:
"Un caffè e una bustina di zucchero costano in totale 1,10 €.
Il caffè costa 1,00 € in più dello zucchero.
Quanto costa lo zucchero?"

Misura la prevalenza del Sistema 1 (euristica impulsiva: 0,10 € / 10 centesimi) rispetto al
Sistema 2 (ragionamento logico-matematico: 0,05 € / 5 centesimi) e registra il tempo di risposta.
"""


class C(BaseConstants):
    NAME_IN_URL = 'coffee_sugar'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Dati del problema
    TOTAL_PRICE = 1.10
    DIFF_PRICE = 1.00

    # Risposte di riferimento
    CORRECT_SUGAR_PRICE = 0.05
    CORRECT_COFFEE_PRICE = 1.05
    INTUITIVE_TRAP_PRICE = 0.10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Risposta testuale fornita dal partecipante
    answer_raw = models.StringField(
        label="Quanto costa lo zucchero (€)?",
        blank=False,
        initial='',
        doc="Stringa inserita dal partecipante (es. '0.05', '0,05', '0.10')"
    )

    # Valore numerico normalizzato
    submitted_price = models.FloatField(
        initial=0.0,
        doc="Prezzo dello zucchero interpretato come float"
    )

    # Classificazione della risposta
    is_correct = models.BooleanField(
        initial=False,
        doc="True se la risposta è 0.05 € (ragionamento analitico - Sistema 2)"
    )
    is_trap = models.BooleanField(
        initial=False,
        doc="True se il partecipante è caduto nella trappola intuitiva (0.10 € - Sistema 1)"
    )

    # Metriche comportamentali
    response_time_seconds = models.FloatField(
        initial=0.0,
        doc="Tempo impiegato per rispondere in secondi (misurato dal client)"
    )


def parse_price(raw_str: str):
    """
    Pulisce e converte una stringa di prezzo in float.
    Supporta formati italiani e anglosassoni: '0,05', '0.05', '0,10', '0.10', '5', '10'.
    Ritorna il float se valido, altrimenti None.
    """
    if not raw_str:
        return None
    cleaned = raw_str.strip().replace('€', '').replace('EUR', '').replace('eur', '').strip()
    cleaned = cleaned.replace(',', '.')
    try:
        val = float(cleaned)
        return round(val, 2)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# PAGINE
# ---------------------------------------------------------------------------

class Intro(Page):
    """
    Breve introduzione neutrale per non allertare il partecipante né indurre
    artificiosamente una modalità analitica (evitando di 'spoilerare' la trappola).
    """
    pass


class GamePage(Page):
    form_model = 'player'
    form_fields = ['answer_raw', 'response_time_seconds']

    @staticmethod
    def error_message(player: Player, values):
        raw = values.get('answer_raw')
        price = parse_price(raw)
        if price is None:
            return "Inserisci un importo numerico valido in Euro (es. con virgola o punto per i decimali)."
        if price < 0:
            return "Il prezzo non può essere un valore negativo."
        if price > 10.0:
            return "L'importo inserito sembra eccessivo rispetto al totale di 1,10 €. Verifica il valore inserito."

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_price_str=f"{C.TOTAL_PRICE:.2f}".replace('.', ','),
            diff_price_str=f"{C.DIFF_PRICE:.2f}".replace('.', ','),
            answer_val=player.field_maybe_none('answer_raw') or '',
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        raw = player.field_maybe_none('answer_raw')
        price = parse_price(raw)
        player.submitted_price = price if price is not None else 0.0

        # Verifica se è corretta (0.05 €) con tolleranza centesimi
        player.is_correct = (abs(player.submitted_price - C.CORRECT_SUGAR_PRICE) < 0.009)

        # Verifica se è la tipica trappola euristica del Sistema 1 (0.10 € / 10 centesimi)
        player.is_trap = (abs(player.submitted_price - C.INTUITIVE_TRAP_PRICE) < 0.009)


class Results(Page):
    """
    Schermata di debriefing: rivelazione del tranello cognitivo, spiegazione scientifica
    (Kahneman & Shane Frederick, Sistema 1 vs Sistema 2) e scomposizione algebrica.
    """
    @staticmethod
    def vars_for_template(player: Player):
        price_str = f"{player.submitted_price:.2f}".replace('.', ',')
        correct_sugar_str = f"{C.CORRECT_SUGAR_PRICE:.2f}".replace('.', ',')
        correct_coffee_str = f"{C.CORRECT_COFFEE_PRICE:.2f}".replace('.', ',')
        total_price_str = f"{C.TOTAL_PRICE:.2f}".replace('.', ',')
        diff_price_str = f"{C.DIFF_PRICE:.2f}".replace('.', ',')

        # Calcolo ipotetico del caffè basato sulla risposta dell'utente per lo zucchero
        implied_coffee = round(C.TOTAL_PRICE - player.submitted_price, 2)
        implied_diff = round(implied_coffee - player.submitted_price, 2)

        return dict(
            submitted_price_str=price_str,
            is_correct=player.is_correct,
            is_trap=player.is_trap,
            is_other=not (player.is_correct or player.is_trap),
            is_fast_decision=(player.response_time_seconds < 8.0),
            correct_sugar_str=correct_sugar_str,
            correct_coffee_str=correct_coffee_str,
            total_price_str=total_price_str,
            diff_price_str=diff_price_str,
            response_time=round(player.response_time_seconds, 1),
            implied_coffee_str=f"{implied_coffee:.2f}".replace('.', ','),
            implied_diff_str=f"{implied_diff:.2f}".replace('.', ','),
        )


page_sequence = [Intro, GamePage, Results]
