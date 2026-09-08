from otree.api import Bot, Submission

from . import (
    C,
    marty_tit_for_tat_contribution,
    LanguagePage,
    InitialFormPage,
    IntroPage,
    DecisionPage,
    ResultsPage,
)


class PlayerBot(Bot):
    """Bot per i test automatici (otree test bttf_pgg_auto).

    Testa sia il percorso in lingua italiana ('it') che in lingua inglese ('en').
    Marty e' simulato con la strategia tit-for-tat.
    """

    cases = ['it', 'en']

    def play_round(self):
        if self.player.round_number == 1:
            yield Submission(LanguagePage, dict(lang=self.case))
            yield Submission(InitialFormPage, dict(
                genere='non_specifico',
                eta=18,
                titolo_studio='diploma',
                occupazione='studente',
                luogo_residenza='Chieti',
                esperienza_precedente='no',
            ))
            yield Submission(IntroPage)
        yield Submission(
            DecisionPage,
            dict(contribution=marty_tit_for_tat_contribution(self.player)),
        )
        yield Submission(ResultsPage)
