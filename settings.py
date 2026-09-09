from os import environ

# =============================================================================
#  CONFIGURAZIONE DELLE SESSIONI - GUIDA RAPIDA PER LO SPERIMENTATORE
# =============================================================================
#  Non serve conoscere la fisica quantistica per usare questo esperimento.
#  Ogni voce qui sotto e' una "condizione sperimentale" gia' pronta: cambia
#  solo il COMPORTAMENTO del bot (l'avversario controllato dal computer).
#
#  Scegli una sessione in base a cosa vuoi che faccia il bot:
#
#    * coopera sempre ....... il bot non tradisce mai (condizione "gentile")
#    * tradisce sempre ...... il bot tradisce a ogni round (condizione "ostile")
#    * mossa speciale ....... il bot usa la strategia quantistica ottimale:
#                             se entrambi la usano si ottiene il massimo
#                             guadagno reciproco
#    * casuale .............. il bot sceglie a caso a ogni round
#    * tit-for-tat .......... il bot copia la scelta del partecipante del
#                             round precedente (al primo round coopera)
#
#  Ogni sessione corrisponde a UNA strategia del bot. Per confrontare le
#  condizioni, crea una sessione per ciascuna e confronta i risultati finali.
# =============================================================================

# La chiave personalizzata `bot_strategy` viene letta nel backend tramite
# `group.session.config['bot_strategy']` e determina il comportamento del bot.
# I suoi valori sono chiavi interne del codice: NON vanno modificati.
SESSION_CONFIGS = [
    # dict(
    #     name='quantum_pd_cooperate',
    #     display_name='Dilemma del Prigioniero - Bot: coopera sempre',
    #     doc='Il bot coopera a ogni round. Condizione piu\' semplice, utile per familiarizzare.',
    #     num_demo_participants=1,
    #     app_sequence=['quantum_pd'],
    #     bot_strategy='always_classical_cooperate',
    # ),
    # dict(
    #     name='quantum_pd_defect',
    #     display_name='Dilemma del Prigioniero - Bot: tradisce sempre',
    #     doc='Il bot tradisce a ogni round. Condizione "ostile".',
    #     num_demo_participants=1,
    #     app_sequence=['quantum_pd'],
    #     bot_strategy='always_classical_defect',
    # ),
    # dict(
    #     name='quantum_pd_quantum',
    #     display_name='Dilemma del Prigioniero - Bot: mossa speciale',
    #     doc='Il bot usa la strategia speciale del gioco quantistico (la piu\' vantaggiosa se usata da entrambi).',
    #     num_demo_participants=1,
    #     app_sequence=['quantum_pd'],
    #     bot_strategy='always_quantum',
    # ),
    # dict(
    #     name='quantum_pd_random',
    #     display_name='Dilemma del Prigioniero - Bot: casuale',
    #     doc='Il bot sceglie a caso a ogni round.',
    #     num_demo_participants=1,
    #     app_sequence=['quantum_pd'],
    #     bot_strategy='random',
    # ),
    # dict(
    #     name='quantum_pd_tit_for_tat',
    #     display_name='Dilemma del Prigioniero - Bot: tit-for-tat (imita)',
    #     doc='Il bot copia la scelta del partecipante del round precedente; al primo round coopera.',
    #     num_demo_participants=1,
    #     app_sequence=['quantum_pd'],
    #     bot_strategy='tit_for_tat',
    # ),
    # -------------------------------------------------------------------------
    # PUBLIC GOODS GAME - "Ritorno al Futuro" (1 umano Marty + 3 bot)
    # -------------------------------------------------------------------------
    #  * `marty_strategy`   = 'human'       -> Marty gioca tramite la dashboard
    #                                          interattiva (sessione con umano)
    #                        = 'tit_for_tat' -> Marty e' simulato (sessioni/test
    #                                          automatici): 5 monete al round 1,
    #                                          poi media dei contributi altrui.
    #  * `default_language` = lingua di partenza del selettore ('it' o 'en').
    #  * `show_bot_results` = True/False    -> se True mostra la tabella dettagliata
    #                                          con scelte/guadagni dei singoli bot;
    #                                          se False (default) mostra solo la
    #                                          scelta del giocatore e il fondo comune.
    # -------------------------------------------------------------------------
    dict(
        name='bttf_pgg_human',
        display_name='Public Goods Game - Ritorno al Futuro (Marty: umano)',
        doc='PGG a 4 ruoli (Marty umano + bot Doc, Biff, Jennifer). Dotazione in Monete/Salvadanaio (10-18 anni).',
        num_demo_participants=1,
        app_sequence=['registration', 'bttf_pgg'],
        marty_strategy='human',
        default_language='it',
        show_bot_results=False,
    ),
    dict(
        name='bttf_pgg_auto',
        display_name='Public Goods Game - Ritorno al Futuro (Marty: tit-for-tat)',
        doc='PGG a 4 ruoli con Marty simulato (tit-for-tat in monete), per sessioni/test automatici.',
        num_demo_participants=1,
        app_sequence=['bttf_pgg'],
        marty_strategy='tit_for_tat',
        default_language='it',
        show_bot_results=False,
    ),
    # -------------------------------------------------------------------------
    # PIZZAGAME - Public Goods Game per bambini (1 umano "Tu" + 3 bot)
    # -------------------------------------------------------------------------
    #  * Dotazione: 5 fette di pizza a testa a ogni round.
    #  * Piatto Condiviso: le fette donate vengono raddoppiate (x2) e divise
    #    in 4 parti uguali tra tutti i bambini.
    #  * Bot: Il Goloso (0 fette), Il Generoso (5 fette), L'Amico Reciproco
    #    (3 fette al round 1, poi media delle fette degli altri).
    # -------------------------------------------------------------------------
    dict(
        name='pizza_pgg_5round',
        display_name='Pizzagame - La Festa della Pizza (bambini, 5 round)',
        doc='PGG classico adattato per bambini (6-9 anni): 1 umano + 3 bot, 5 fette a testa, Piatto Condiviso x2.',
        num_demo_participants=1,
        app_sequence=['pizza_pgg'],
    ),
    # -------------------------------------------------------------------------
    # ESPERIMENTO UNIFICATO - "Notte dei Ricercatori 2026"
    # -------------------------------------------------------------------------
    #  Un'unica sessione che instrada automaticamente ogni partecipante in base
    #  all'eta' inserita nella scheda di registrazione (app `registration`):
    #      * eta < 9  -> pizza_pgg (gioco per bambini)
    #      * eta >= 9 -> bttf_pgg  (gioco "Ritorno al Futuro")
    #  Entrambi i rami terminano sulla schermata di chiusura condivisa (`fine`).
    # -------------------------------------------------------------------------
    dict(
        name='esperimento_nrd',
        display_name='Esperimento completo - Notte dei Ricercatori 2026 (instradamento per eta\')',
        doc='Sessione unificata: registrazione + instradamento automatico (eta<9 -> pizza, eta>=9 -> bttf) + chiusura.',
        num_demo_participants=1,
        app_sequence=['registration', 'bttf_pgg', 'pizza_pgg', 'fine'],
        marty_strategy='human',
        default_language='it',
        show_bot_results=False,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

LANGUAGE_CODE = 'it'

REAL_WORLD_CURRENCY_CODE = 'EUR'

USE_POINTS = True

# =============================================================================
#  ROOMS - UN SOLO LINK PER TUTTI I PARTECIPANTI
# =============================================================================
#  Una "room" (stanza) di oTree permette di dare a TUTTI i partecipanti lo
#  STESSO link per partecipare all'esperimento.
#
#  Come funziona:
#    * Ogni room e' legata a UNA sessione (creata da una SESSION_CONFIGS).
#    * Il link condiviso da distribuire ai partecipanti e':
#          http://<host>:<porta>/room/<nome_room>
#      (es. http://localhost:8000/room/esperimento_nrd)
#    * Ogni partecipante che apre quel link viene assegnato automaticamente
#      alla sessione collegata alla room (un "posto" per browser, tramite
#      cookie), quindi tutti giocano nella STESSA sessione.
#
#  Procedura per lo sperimentatore:
#    1. Avvia il server (otree devserver).
#    2. Vai su http://localhost:8000/rooms (pannello admin).
#    3. Nella room "Esperimento completo - Notte dei Ricercatori 2026"
#       clicca "Create session" e scegli la sessione `esperimento_nrd`.
#    4. Distribuisci ai partecipanti il link della room
#       (http://<host>:<porta>/room/esperimento_nrd).
#
#  NOTA: senza `participant_label_file` la room e' "aperta": chiunque apra il
#  link entra nella sessione finche' ci sono posti liberi. Se vuoi limitare
#  l'accesso a un elenco predefinito di partecipanti, aggiungi un file di
#  etichette (vedi documentazione oTree).
# =============================================================================
ROOMS = [
    dict(
        name='esperimento_nrd',
        display_name='Esperimento completo - Notte dei Ricercatori 2026',
        # Pagina di benvenuto personalizzata (in italiano) mostrata prima
        # dell'ingresso nella sessione. Se omessa, oTree usa quella di default.
        welcome_page='_templates/esperimento_nrd_welcome.html',
    ),
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'admin')

DEMO_PAGE_INTRO_HTML = """
<p><strong>Come iniziare (nessuna fisica richiesta).</strong>
Scegli una sessione qui sotto in base al comportamento che vuoi dare al bot
(l'avversario controllato dal computer):</p>
<ul>
    <li><strong>Coopera sempre</strong> &mdash; il bot non tradisce mai.</li>
    <li><strong>Tradisce sempre</strong> &mdash; il bot tradisce a ogni round.</li>
    <li><strong>Mossa speciale</strong> &mdash; il bot usa la strategia ottimale del gioco quantistico.</li>
    <li><strong>Casuale</strong> &mdash; il bot sceglie a caso.</li>
    <li><strong>Tit-for-tat</strong> &mdash; il bot imita la scelta precedente del partecipante.</li>
</ul>
<p>Per uno studio pulito, assegna ogni partecipante a una sola condizione.</p>
<p><strong>Esperimento completo &mdash; Notte dei Ricercatori 2026.</strong>
Sessione unificata con instradamento automatico: ogni partecipante compila la
scheda di registrazione e, in base all'et&agrave;, viene mandato al gioco
corretto (bambini sotto i 9 anni al Pizzagame, dai 9 anni in su al Public
Goods Game &ldquo;Ritorno al Futuro&rdquo;). Entrambi i rami terminano su una
schermata di chiusura condivisa.</p>
<p><strong>Public Goods Game &mdash; Ritorno al Futuro.</strong>
Sono disponibili anche due sessioni del gioco dei beni pubblici (PGG) a tema
<em>Ritorno al Futuro</em>: una in cui Marty e' giocato da un umano (con
registrazione) e una in simulazione automatica (Marty gioca tit-for-tat).</p>
<p><strong>Pizzagame &mdash; La Festa della Pizza (bambini).</strong>
PGG classico adattato per bambini (6-9 anni): 1 bambino umano + 3 bot, 5 fette
di pizza a testa a ogni round, Piatto Condiviso raddoppiato (x2) e diviso in 4
parti uguali. Interfaccia colorata con bottoni-pizza.</p>
"""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'quantum-pd-dev-secret-key')
