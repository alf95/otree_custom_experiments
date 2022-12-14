from otree.api import *
import pathlib

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
        p1.payoff = 0
        p2.payoff = 0

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
            write_payoffs_to_csv(players)
    #print(group.subsession.get_players()[0].participant.payoff)
    

def write_payoffs_to_csv(data):
    import csv
    from io import StringIO
    from RemoteFileSystem import RemoteFileSystem

    
    header = ['id','endowment']
    buff = StringIO()
    writer2 = csv.writer(buff, quoting=csv.QUOTE_NONE)
    writer2.writerow(header)
    writer2.writerows(data)
    RemoteFileSystem().update_file(filename="endowment_players.csv", content= buff.getvalue())

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
