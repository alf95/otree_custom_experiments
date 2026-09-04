from otree.api import Bot, Submission

from . import (
    C,
    marty_tit_for_tat_contribution,
    LanguagePage,
    IntroPage,
    DecisionPage,
    ResultsPage,
)


class PlayerBot(Bot):
    """Bot per i test automatici (otree test bttf_pgg_auto).

    Marty e' simulato con la strategia tit-for-tat: 5 unita' al primo round,
    poi la media dei contributi degli altri tre giocatori del round precedente.
    """

    def play_round(self):
        if self.player.round_number == 1:
            yield Submission(LanguagePage, dict(lang='it'))
            yield Submission(IntroPage)
        yield Submission(
            DecisionPage,
            dict(contribution=marty_tit_for_tat_contribution(self.player)),
        )
        yield Submission(ResultsPage)
