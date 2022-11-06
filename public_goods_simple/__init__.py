from otree.api import *


def get_endowments_from_csv():
    import csv

    f = open(__name__ + '/endowment_players.csv', encoding='utf-8-sig')
    endowments = {}
    for row in csv.DictReader(f):
        endowments[row['id']] = int(row['endowment'])
    
    return endowments

class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    endowments = get_endowments_from_csv()
    #MPCR=0.5


class Subsession(BaseSubsession):
    pass



"""def creating_session(subsession: Subsession):
    session = subsession.session
    print(session.num_participants)"""
    

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
        endowments = C.endowments
        for player in group.get_players():
            playerId = player.participant.label
            player.endowment = endowments[playerId]  


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [FirstWaitPage, Contribute, ResultsWaitPage, Results]
