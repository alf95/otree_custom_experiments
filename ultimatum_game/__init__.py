from otree.api import *

doc = """
Strategy method for ultimatum game.
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    INSTRUCTIONS_FILE = __name__ + '/instructions.html'
    ENDOWMENT = cu(10)
    OFFER_CHOICES = currency_range(0, ENDOWMENT, 1)
    OFFER_CHOICES_COUNT = len(OFFER_CHOICES)

    POSSIBLE_ALLOCATIONS = []
    for OFFER in OFFER_CHOICES:
        POSSIBLE_ALLOCATIONS.append(dict(p1_amount=OFFER, p2_amount=ENDOWMENT - OFFER))




class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.finished_round = False


class Group(BaseGroup):
    print(C.OFFER_CHOICES)
    amount_offered = models.CurrencyField(choices=C.OFFER_CHOICES,)
    offer_accepted = models.BooleanField(
        label="Would you accept the offer?",
        widget=widgets.RadioSelect,
        # note to self: remove this once i release bugfix
        choices=[[False, 'No'], [True, 'Yes']],
    )
    


def set_payoffs(group: Group):    
    p1, p2 = group.get_players()
    p1.player_type = 'proposer'
    p2.player_type = 'responder'
    amount_offered = group.amount_offered
    if group.offer_accepted:
        p1.payoff = C.ENDOWMENT - amount_offered
        p2.payoff = amount_offered 
    else:
        p1.payoff = cu(0)
        p2.payoff = cu(0)

    p1.finished_round = True
    p2.finished_round = True

    print("Players in subsession")
    if group.subsession.round_number == C.NUM_ROUNDS:
        players_other_groups = list(filter(lambda player: player.participant.id_in_session not in [p1.participant.id_in_session, p2.participant.id_in_session], group.subsession.get_players()))
        active_players = list(filter(lambda p:  p.round_number < C.NUM_ROUNDS or not(p.finished_round), players_other_groups))
        #print(active_players)
        if len(active_players) == 0:
            print("Session completed")
            players = []
            for pl in group.subsession.get_players():
                participant = pl.participant
                players.append([participant.label, participant.payoff.__int__()])
            write_payoffs_to_db(players)
    #print(group.subsession.get_players()[0].participant.payoff)
    

def write_payoffs_to_db(data):
    """
    Salva i payoff finali nel database PostgreSQL.
    I dati sono già persistiti attraverso il modello Participant di oTree,
    ma questa funzione crea un record nella tabella FinalPayoff per tracciamento.
    """
    from datetime import datetime
    for player_data in data:
        player_id, payoff = player_data
        payoff_record = FinalPayoff.create()
        payoff_record.player_label = player_id
        payoff_record.final_payoff = payoff
        payoff_record.timestamp = datetime.now().isoformat()
    print(f"Salvati {len(data)} payoff nel database")


class FinalPayoff(ExtraModel):
    """
    Modello personalizzato per salvare i payoff finali dei giocatori.
    Questa tabella viene creata nel database PostgreSQL.
    """
    player_label = models.StringField()
    final_payoff = models.IntegerField()
    timestamp = models.StringField()


class Player(BasePlayer):
    player_type = models.StringField(choices=['proposer', 'responder'])
    finished_round = models.BooleanField()


class P1(Page):
    form_model = 'group'
    form_fields = ['amount_offered']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1



class P1ContributionWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2



class P2(Page):
    form_model = 'group'
    form_fields = ['offer_accepted']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2



class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    title_text = "Thank you"
    body_text = (
        "You can close this page. When the other player arrives, the payoff will be calculated."
    )


class Results(Page):
    pass


page_sequence = [
    P1,
    P1ContributionWaitPage,
    P2,
    ResultsWaitPage,
    Results,
]
