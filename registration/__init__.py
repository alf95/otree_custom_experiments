from otree.api import *

import hashlib
import string


doc = """
Scheda di registrazione condivisa per l'esperimento "Notte dei Ricercatori 2026".

E' la PRIMA app di ogni sessione sperimentale unificata. Ogni partecipante
compila una sola volta la scheda anagrafica; in base all'eta' inserita il
sistema instrada automaticamente al gioco corretto:
    * eta < 9  -> pizza_pgg (gioco per bambini)
    * eta >= 9 -> bttf_pgg  (gioco "Ritorno al Futuro")

L'instradamento usa `app_after_this_page` (salto di intere app, feature
nativa di oTree): se il partecipante e' un bambino, dall'ultima pagina di
questa app si salta direttamente a pizza_pgg, scavalcando bttf_pgg.
I dati condivisi tra le app vengono salvati in `participant.vars`:
`codice_id`, `eta`, `assigned_game` ('pizza' oppure 'bttf').
"""


class C(BaseConstants):
    NAME_IN_URL = 'registration'
    # Ogni partecipante gioca da solo (nessun gruppo): non serve attendere
    # altri umani per l'instradamento.
    PLAYERS_PER_GROUP = None

    NUM_ROUNDS = 1

    # Soglia di eta' (inclusiva verso l'alto) per la scelta del gioco:
    # eta < AGE_THRESHOLD -> pizza_pgg ; eta >= AGE_THRESHOLD -> bttf_pgg.
    AGE_THRESHOLD = 9


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- Scheda anagrafica (Notte dei Ricercatori 2026) ---
    codice_id = models.StringField(initial='')
    genere = models.StringField(
        choices=[
            ['uomo', 'Uomo'],
            ['donna', 'Donna'],
            ['altro', 'Altro'],
            ['non_specifico', 'Preferisco non specificare'],
        ],
        label='Genere',
    )
    eta = models.IntegerField(
        min=1, max=120,
        label="Eta' (in cifre)",
    )
    titolo_studio = models.StringField(
        choices=[
            ['licenza_elementare', 'Licenza elementare (scuola primaria)'],
            ['licenza_media', 'Licenza media (scuola secondaria di I grado)'],
            ['diploma', 'Diploma di scuola superiore (scuola secondaria di II grado)'],
            ['qualifica_professionale', 'Qualifica professionale'],
            ['laurea_triennale', 'Laurea triennale / base'],
            ['laurea_magistrale', 'Laurea magistrale'],
            ['master_i', 'Master universitario di I livello'],
            ['master_ii', 'Master universitario di II livello'],
            ['dottorato', 'Dottorato di ricerca'],
        ],
        label='Titolo di studio raggiunto',
    )
    occupazione = models.StringField(
        choices=[
            ['studente', 'Studente'],
            ['lavoratore', 'Lavoratore'],
            ['disoccupato', 'Disoccupato'],
            ['pensionato', 'Pensionato'],
        ],
        label='Occupazione',
    )
    luogo_residenza = models.StringField(
        label="Luogo di residenza (citta' o paese)",
    )
    esperienza_precedente = models.StringField(
        choices=[
            ['si', "Si'"],
            ['no', 'No'],
        ],
        label='Esperienza pregressa nella partecipazione ad esperimenti',
    )


def generate_participant_id(player):
    """Genera un codice identificativo univoco nel formato
    ID + numero (0-500, minimo 2 cifre) + lettera maiuscola (A-Z).

    Esempi: 'ID01A', 'ID402X'. Il codice e' derivato in modo deterministico
    dal `participant.code` di oTree (univoco per sessione), quindi non cambia
    tra un round e l'altro e non collide tra partecipanti diversi.
    """
    seed = player.participant.code or str(player.participant.id)
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    number = int(digest[:6], 16) % 501                    # 0..500
    letter = string.ascii_uppercase[int(digest[6:8], 16) % 26]  # A..Z
    return f"ID{number:02d}{letter}"


def assigned_game(eta):
    """Decide il gioco in base all'eta': 'pizza' se eta < soglia, altrimenti 'bttf'."""
    return 'pizza' if eta < C.AGE_THRESHOLD else 'bttf'


class InitialFormPage(Page):
    form_model = 'player'
    form_fields = [
        'genere', 'eta', 'titolo_studio', 'occupazione',
        'luogo_residenza', 'esperienza_precedente',
    ]

    @staticmethod
    def vars_for_template(player):
        codice = player.participant.vars.get('codice_id')
        if not codice:
            codice = generate_participant_id(player)
            player.participant.vars['codice_id'] = codice
        return dict(codice_id=codice)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.codice_id = player.participant.vars.get('codice_id', '')
        # Dati condivisi con le app successive (bttf_pgg / pizza_pgg / fine).
        player.participant.vars['eta'] = player.eta
        player.participant.vars['assigned_game'] = assigned_game(player.eta)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        # Bambino (< soglia): salta l'intera app bttf_pgg e va direttamente a
        # pizza_pgg. La guardia `in upcoming_apps` rende innocua questa logica
        # anche nelle sessioni standalone di bttf (senza pizza in sequenza).
        if player.participant.vars.get('assigned_game') == 'pizza':
            if 'pizza_pgg' in upcoming_apps:
                return 'pizza_pgg'
        return None


page_sequence = [InitialFormPage]
