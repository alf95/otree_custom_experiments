from otree.api import Bot, Submission, SubmissionMustFail, expect
from . import C, Intro, GamePage, Results


class PlayerBot(Bot):
    """
    Suite di test automatici per coffee_sugar (otree test coffee_sugar_problem).
    Verifica:
    1. Risposta analitica corretta per lo zucchero (Sistema 2: 0,05 € sia con virgola che con punto) -> is_correct = True
    2. Risposta euristica trappola per lo zucchero (Sistema 1: 0,10 €) -> is_trap = True, is_correct = False
    3. Rifiuto server-side di input non validi (stringhe non numeriche, valori negativi, importi assurdi)
    """

    cases = [
        'correct_answer_comma',
        'correct_answer_dot',
        'intuitive_trap_answer',
        'invalid_input_failure',
    ]

    def case_correct_answer_comma(self):
        yield Submission(Intro)
        yield Submission(GamePage, dict(answer_raw="0,05", response_time_seconds=14.2))

        expect(self.player.is_correct, True)
        expect(self.player.is_trap, False)
        expect(self.player.submitted_price, 0.05)

        yield Submission(Results)

    def case_correct_answer_dot(self):
        yield Submission(Intro)
        yield Submission(GamePage, dict(answer_raw="0.05", response_time_seconds=16.8))

        expect(self.player.is_correct, True)
        expect(self.player.is_trap, False)
        expect(self.player.submitted_price, 0.05)

        yield Submission(Results)

    def case_intuitive_trap_answer(self):
        yield Submission(Intro)
        yield Submission(GamePage, dict(answer_raw="0,10", response_time_seconds=2.8))

        expect(self.player.is_correct, False)
        expect(self.player.is_trap, True)
        expect(self.player.submitted_price, 0.10)

        yield Submission(Results)

    def case_invalid_input_failure(self):
        yield Submission(Intro)

        # Test testo non valido
        yield SubmissionMustFail(GamePage, dict(answer_raw="non so", response_time_seconds=2.0))

        # Test numero negativo
        yield SubmissionMustFail(GamePage, dict(answer_raw="-0.05", response_time_seconds=2.0))

        # Test importo assurdo
        yield SubmissionMustFail(GamePage, dict(answer_raw="50.00", response_time_seconds=2.0))

        # Conclusione valida
        yield Submission(GamePage, dict(answer_raw="0.05", response_time_seconds=9.5))
        yield Submission(Results)

    def play_round(self):
        case = self.case
        getattr(self, f'case_{case}')()
