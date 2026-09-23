from otree.api import Bot, Submission, SubmissionMustFail, expect
from . import C, Intro, GamePage, Results


class PlayerBot(Bot):
    """
    Suite di test automatici per coffee_sugar (otree test coffee_sugar).
    Verifica:
    1. Sequenza completa Intro -> GamePage -> Results
    2. Rifiuto server-side delle allocazioni che superano il budget di 20,00 €
    3. Calcolo corretto dell'ottimo del consumatore (4 caffè, 8 bustine = 20,00 €)
    4. Calcolo corretto di panieri intermedi e liquidità residua
    """

    cases = [
        'optimal_bundle',
        'over_budget_failure',
        'zero_consumption',
        'partial_bundle',
    ]

    def case_optimal_bundle(self):
        # 1. Intro
        yield Submission(Intro)

        # 2. Scelta ottima: 4 caffè (12 €) + 8 zuccheri (8 €) = 20,00 €
        yield Submission(GamePage, dict(coffee_units=4, sugar_units=8))

        # Verifiche modello
        expect(self.player.coffee_units, 4)
        expect(self.player.sugar_units, 8)
        expect(self.player.budget_spent, 20.00)
        expect(self.player.budget_left, 0.00)
        expect(self.player.perfect_cups, 4)
        expect(self.player.satisfaction_percent, 100.0)
        expect(self.player.total_payout, 15.00)
        expect(self.player.payoff, 15.00)

        # 3. Results
        yield Submission(Results)

    def case_over_budget_failure(self):
        yield Submission(Intro)

        # Rifiuto: 7 caffè = 21,00 € (> 20,00 €)
        yield SubmissionMustFail(GamePage, dict(coffee_units=7, sugar_units=0))

        # Rifiuto: 5 caffè (15 €) + 6 zuccheri (6 €) = 21,00 €
        yield SubmissionMustFail(GamePage, dict(coffee_units=5, sugar_units=6))

        # Invio valido per completare il test
        yield Submission(GamePage, dict(coffee_units=2, sugar_units=4))
        yield Submission(Results)

    def case_zero_consumption(self):
        yield Submission(Intro)

        # Nessuna consumazione: tutto in liquidità (20,00 € non spesi)
        yield Submission(GamePage, dict(coffee_units=0, sugar_units=0))

        expect(self.player.budget_spent, 0.00)
        expect(self.player.budget_left, 20.00)
        expect(self.player.perfect_cups, 0)
        # 20 € rimasti * 0.25 cash = 5.00 € di base cash
        expect(self.player.total_payout > 5.0, True)

        yield Submission(Results)

    def case_partial_bundle(self):
        yield Submission(Intro)

        # 2 caffè (6 €) + 4 zuccheri (4 €) = 10 € spesi, 10 € rimasti
        yield Submission(GamePage, dict(coffee_units=2, sugar_units=4))

        expect(self.player.budget_spent, 10.00)
        expect(self.player.budget_left, 10.00)
        expect(self.player.perfect_cups, 2)
        expect(self.player.satisfaction_percent > 50.0, True)

        yield Submission(Results)

    def play_round(self):
        case = self.case
        getattr(self, f'case_{case}')()
