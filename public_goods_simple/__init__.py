from otree.api import *
import json

def get_endowments_from_db():
    from ultimatum_game import FinalPayoff

    endowments = {}
    # Recupera tutti i record dalla tabella FinalPayoff
    payoff_records = FinalPayoff.filter()

    for record in payoff_records:
        endowments[record.player_label] = record.final_payoff

    return endowments

class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    endowments = models.LongStringField()



def creating_session(subsession: Subsession):
    print("creating_session method")
    print("round number " + str(subsession.round_number))
    if(subsession.round_number == 1):
        subsession.endowments = json.dumps(get_endowments_from_db())


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    endowment = models.IntegerField()
    contribution = models.CurrencyField(min=0)

# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = group.total_contribution * group.subsession.session.config['MPCR']

    for p in players:
        p.payoff = p.endowment - p.contribution + group.individual_share


# PAGES
class FirstWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        endowments = json.loads(group.subsession.in_round(1).endowments)
        for player in group.get_players():
            player_id = player.participant.label
            player.endowment = endowments[player_id]


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [FirstWaitPage, Contribute, ResultsWaitPage, Results]
