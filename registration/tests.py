from otree.api import Bot, Submission, SubmissionMustFail, expect

from . import (
    C,
    assigned_game,
    InitialFormPage,
    normalize_luogo_residenza,
    registration_field_errors,
)


# Dati validi di partenza: ogni test parte da questi e modifica solo il campo
# che vuole verificare.
VALID_DATA = dict(
    genere='donna',
    eta=25,
    titolo_studio='laurea_magistrale',
    occupazione='lavoratore',
    luogo_residenza='Chieti',
    esperienza_precedente='no',
)


def valid_data(**overrides):
    """Copia i dati validi applicando le eventuali sostituzioni."""
    data = dict(VALID_DATA)
    data.update(overrides)
    return data


class PlayerBot(Bot):
    """Suite di test automatici per la validazione della scheda di
    registrazione (otree test registration_validation).

    Ogni `case` e' un partecipante separato che esegue una sequenza di
    sottomissioni: prima quelle che DEVONO essere rifiutate
    (SubmissionMustFail), poi una valida (Submission) che deve passare.
    """

    cases = [
        'valid_submission',
        'required_fields_missing',
        'eta_out_of_range',
        'eta_not_integer',
        'invalid_choices',
        'luogo_residenza_validation',
        'routing_by_age',
    ]

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def submit_valid(self):
        """Invia il form con dati validi e verifica che passi."""
        yield Submission(InitialFormPage, valid_data())

    # ------------------------------------------------------------------
    # 1) Sottomissione valida
    # ------------------------------------------------------------------
    def case_valid_submission(self):
        yield self.submit_valid()
        # I dati devono essere stati salvati correttamente sul player.
        expect(self.player.genere, 'donna')
        expect(self.player.eta, 25)
        expect(self.player.titolo_studio, 'laurea_magistrale')
        expect(self.player.occupazione, 'lavoratore')
        expect(self.player.luogo_residenza, 'Chieti')
        expect(self.player.esperienza_precedente, 'no')
        # Il codice ID deve essere stato generato e condiviso (formato ID##X).
        codice = self.player.participant.vars['codice_id']
        expect(codice[:2], 'ID')
        expect(len(codice), 5)
        expect(self.player.participant.vars['eta'], 25)
        expect(self.player.participant.vars['assigned_game'], 'bttf')

    # ------------------------------------------------------------------
    # 2) Campi obbligatori mancanti
    # ------------------------------------------------------------------
    def case_required_fields_missing(self):
        # Ogni campo obbligatorio, se omesso, deve far fallire la validazione.
        for field in [
            'genere',
            'eta',
            'titolo_studio',
            'occupazione',
            'luogo_residenza',
            'esperienza_precedente',
        ]:
            data = valid_data()
            data.pop(field)
            yield SubmissionMustFail(InitialFormPage, data, error_fields=[field])

        # Anche un valore vuoto esplicito deve essere rifiutato.
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(genere=''),
            error_fields=['genere'],
        )
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(luogo_residenza=''),
            error_fields=['luogo_residenza'],
        )

        yield self.submit_valid()

    # ------------------------------------------------------------------
    # 3) Eta' fuori intervallo
    # ------------------------------------------------------------------
    def case_eta_out_of_range(self):
        # Sotto il minimo (1) e sopra il massimo (120).
        yield SubmissionMustFail(
            InitialFormPage, valid_data(eta=0), error_fields=['eta']
        )
        yield SubmissionMustFail(
            InitialFormPage, valid_data(eta=121), error_fields=['eta']
        )
        # Limiti inclusi: 1 e 120 sono validi.
        yield Submission(InitialFormPage, valid_data(eta=1))
        yield Submission(InitialFormPage, valid_data(eta=120))

    # ------------------------------------------------------------------
    # 4) Eta' non intera
    # ------------------------------------------------------------------
    def case_eta_not_integer(self):
        # Valori non numerici o decimali devono essere rifiutati.
        yield SubmissionMustFail(
            InitialFormPage, valid_data(eta='abc'), error_fields=['eta']
        )
        yield SubmissionMustFail(
            InitialFormPage, valid_data(eta=25.5), error_fields=['eta']
        )

    # ------------------------------------------------------------------
    # 5) Scelte non ammesse
    # ------------------------------------------------------------------
    def case_invalid_choices(self):
        # Valori che non compaiono tra le scelte definite sul modello.
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(genere='sconosciuto'),
            error_fields=['genere'],
        )
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(titolo_studio='nessuno'),
            error_fields=['titolo_studio'],
        )
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(occupazione='altro'),
            error_fields=['occupazione'],
        )
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(esperienza_precedente='forse'),
            error_fields=['esperienza_precedente'],
        )

    # ------------------------------------------------------------------
    # 6) Luogo di residenza (testo libero)
    # ------------------------------------------------------------------
    def case_luogo_residenza_validation(self):
        # Solo spazi: deve essere rifiutato (controllo semantico).
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(luogo_residenza='   '),
            error_fields=['luogo_residenza'],
        )
        # Troppo corto (< 2 caratteri).
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(luogo_residenza='A'),
            error_fields=['luogo_residenza'],
        )
        # Troppo lungo (> 100 caratteri).
        yield SubmissionMustFail(
            InitialFormPage,
            valid_data(luogo_residenza='X' * 101),
            error_fields=['luogo_residenza'],
        )
        # Lunghezza massima ammessa (100 caratteri) -> valido.
        yield Submission(InitialFormPage, valid_data(luogo_residenza='Y' * 100))
        # Il testo viene normalizzato (spazi compattati, niente spazi ai bordi).
        yield Submission(
            InitialFormPage, valid_data(luogo_residenza='  Pescara   Abruzzo  ')
        )
        expect(self.player.luogo_residenza, 'Pescara Abruzzo')

    # ------------------------------------------------------------------
    # 7) Instradamento in base all'eta'
    # ------------------------------------------------------------------
    def case_routing_by_age(self):
        # eta < soglia -> pizza ; eta >= soglia -> bttf.
        expect(assigned_game(C.AGE_THRESHOLD - 1), 'pizza')
        expect(assigned_game(C.AGE_THRESHOLD), 'bttf')
        expect(assigned_game(3), 'pizza')
        expect(assigned_game(40), 'bttf')

        yield Submission(InitialFormPage, valid_data(eta=8))
        expect(self.player.participant.vars['assigned_game'], 'pizza')
        expect(self.player.participant.vars['eta'], 8)

        yield Submission(InitialFormPage, valid_data(eta=9))
        expect(self.player.participant.vars['assigned_game'], 'bttf')
        expect(self.player.participant.vars['eta'], 9)

    # ------------------------------------------------------------------
    # Entry point: esegue il case selezionato
    # ------------------------------------------------------------------
    def play_round(self):
        case = self.case
        getattr(self, f'case_{case}')()
