from otree.api import *

doc = """
Strategy method for ultimatum game.
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    INSTRUCTIONS_FILE = __name__ + '/instructions.html'
    ENDOWMENT = cu(10)
    OFFER_CHOICES = currency_range(0, ENDOWMENT, 1)
    OFFER_CHOICES_COUNT = len(OFFER_CHOICES)

    POSSIBLE_ALLOCATIONS = []
    for OFFER in OFFER_CHOICES:
        POSSIBLE_ALLOCATIONS.append(dict(p1_amount=OFFER, p2_amount=ENDOWMENT - OFFER))


class Subsession(BaseSubsession):
    pass



class Group(BaseGroup):
    print(C.OFFER_CHOICES)
    amount_offered = models.CurrencyField(choices=C.OFFER_CHOICES,)
    offer_accepted = models.BooleanField(
        label="Would you accept the offer?",
        widget=widgets.RadioSelect,
        # note to self: remove this once i release bugfix
        choices=[[False, 'No'], [True, 'Yes']],
    )
    # another way to implement this game would be with an ExtraModel, instead of making
    # all these hardcoded fields.
    # that's what the choice_list app does.
    # that would be more flexible, but also more complex since you would have to implement the
    # formfields yourself with HTML and Javascript.
    # in this case, since the rules of the game are pretty simple,
    # and there are not too many fields,
    # just defining these hardcoded fields is fine.
    


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


class Player(BasePlayer):
    player_type = models.StringField(choices=['proposer', 'responder'])


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
