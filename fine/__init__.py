from otree.api import *


doc = """
Schermata di chiusura condivisa dell'esperimento "Notte dei Ricercatori 2026".

E' l'ULTIMA app di ogni sessione sperimentale unificata. Viene raggiunta:
    * dall'adulto (>= 9 anni) al termine di bttf_pgg (salto esplicito da
      bttf_pgg verso questa app, scavalcando pizza_pgg);
    * dal bambino (< 9 anni) al termine di pizza_pgg (progressione naturale).

Mostra il codice identificativo e il payoff finale accumulato dal partecipante.
"""


class C(BaseConstants):
    NAME_IN_URL = 'fine'
    # Ogni partecipante arriva da solo: nessun gruppo.
    PLAYERS_PER_GROUP = None

    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class ClosingPage(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            codice_id=player.participant.vars.get('codice_id', ''),
            final_payoff=player.participant.payoff,
        )


page_sequence = [ClosingPage]
