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
    """Genera un codice identificativo univoco di 6 caratteri nel formato
    4 cifre (0000-9999) + 2 lettere maiuscole (A-Z), senza prefisso 'ID'.

    Esempi: '0421AB', '8410XQ'. Il codice e' derivato in modo deterministico
    dal `participant.code` di oTree (univoco per sessione), quindi non cambia
    tra un round e l'altro e non collide tra partecipanti diversi.
    """
    seed = player.participant.code or str(player.participant.id)
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    number = int(digest[:8], 16) % 10000                   # 0..9999
    letters = ''.join(
        string.ascii_uppercase[int(digest[i:i + 2], 16) % 26]
        for i in range(8, 12, 2)                           # due lettere A..Z
    )
    return f"{number:04d}{letters}"


def assigned_game(eta):
    """Decide il gioco in base all'eta': 'pizza' se eta < soglia, altrimenti 'bttf'."""
    return 'pizza' if eta < C.AGE_THRESHOLD else 'bttf'


# ---------------------------------------------------------------------------
# Validazione della scheda di registrazione
# ---------------------------------------------------------------------------
# oTree applica in automatico i controlli "di base" definiti sul modello
# (campo obbligatorio, tipo numerico, min/max, scelta tra i valori ammessi),
# con messaggi di errore gia' tradotti in italiano (settings LANGUAGE_CODE).
#
# Le funzioni qui sotto aggiungono i controlli SEMANTICI che il modello non
# sa esprimere da solo (es. "non solo spazi", lunghezze minime/massime del
# testo libero). Vengono richiamate da InitialFormPage.error_message solo
# DOPO che tutti i controlli di base sono passati.
# ---------------------------------------------------------------------------

# Limiti applicati al campo testuale libero "luogo_residenza". Devono
# combaciare con gli attributi HTML (maxlength) usati nel template.
LUOGO_MIN_LENGTH = 2
LUOGO_MAX_LENGTH = 100

MSG_LUOGO_REQUIRED = 'Inserisci un luogo di residenza valido (non solo spazi).'
MSG_LUOGO_TOO_SHORT = (
    f'Il luogo di residenza deve contenere almeno {LUOGO_MIN_LENGTH} caratteri.'
)
MSG_LUOGO_TOO_LONG = (
    f'Il luogo di residenza puo\' contenere al massimo {LUOGO_MAX_LENGTH} caratteri.'
)


def normalize_luogo_residenza(value):
    """Rimuove spazi iniziali/finali e compatta le sequenze di spazi interni."""
    if value is None:
        return ''
    return ' '.join(value.split())


def registration_field_errors(values):
    """Controlli semantici aggiuntivi sui campi del form di registrazione.

    Riceve il dict ``values`` dei dati gia' ripuliti dal form oTree e
    restituisce un dict {campo: messaggio_di_errore}; vuoto se tutto e'
    valido. NB: viene invocata solo quando i controlli di base del modello
    sono gia' passati (es. eta' e' un intero valido e nei limiti, le scelte
    sono tra quelle ammesse).
    """
    errors = {}

    # `luogo_residenza` e' l'unico campo a testo libero: oltre all'obbligo
    # (gestito dal modello) verifichiamo che non siano solo spazi e che la
    # lunghezza sia entro i limiti.
    luogo = normalize_luogo_residenza(values.get('luogo_residenza'))
    if not luogo:
        # Stringa composta solo da spazi: sfugge al controllo "obbligatorio"
        # di oTree (che considera presente anche una sequenza di soli spazi).
        if values.get('luogo_residenza'):
            errors['luogo_residenza'] = MSG_LUOGO_REQUIRED
    elif len(luogo) < LUOGO_MIN_LENGTH:
        errors['luogo_residenza'] = MSG_LUOGO_TOO_SHORT
    elif len(luogo) > LUOGO_MAX_LENGTH:
        errors['luogo_residenza'] = MSG_LUOGO_TOO_LONG

    return errors


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
    def error_message(player, values):
        """Controlli semantici extra (oltre a quelli automatici del modello).

        Restituisce un dict {campo: messaggio}; se vuoto il form e' valido.
        oTree chiama questo metodo solo quando tutti i controlli di base
        (obbligatorieta', tipo, min/max, scelte ammesse) sono passati.
        """
        return registration_field_errors(values)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.codice_id = player.participant.vars.get('codice_id', '')
        # Dati condivisi con le app successive (bttf_pgg / pizza_pgg / fine).
        player.participant.vars['eta'] = player.eta
        player.participant.vars['assigned_game'] = assigned_game(player.eta)
        # Salva il testo libero normalizzato (niente spazi superflui).
        player.luogo_residenza = normalize_luogo_residenza(player.luogo_residenza)

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
