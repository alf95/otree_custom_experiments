# Public Goods Game - "Ritorno al Futuro" (Documentazione IT)

Applicazione **oTree** che implementa un **Public Goods Game (PGG) classico a 4
giocatori** - 1 utente umano + 3 bot - ambientato nella narrativa di
**"Ritorno al Futuro"** (*Back to the Future*).

---

## 1. Descrizione generale e narrativa

Sei **Marty McFly**, nel 1985. La **DeLorean** e' ferma e il **Flusso
Canalizzatore** (*Flux Capacitor*) e' scarico: per viaggiare nel tempo serve una
potenza di almeno **1.21 GW**. Insieme a te giocano altri tre abitanti di Hill
Valley:

| Giocatore | Tipo | Strategia | Ruolo Comportamentale (Letteratura) |
|-----------|------|-----------|-----------------------------------|
| **Marty** | Umano (o bot nei test) | Scelta libera / Tit-for-Tat | Giocatore decisionale (pivotal) |
| **Doc**   | Bot  | Always Cooperate | Altruist / Target-Pacer (Milinski et al. 2008) |
| **Biff**  | Bot  | Always Defect | Pure Free Rider (Fischbacher et al. 2001) |
| **Jennifer** | Bot | Conditional Cooperator | Reattiva/Reciproca (Fischbacher et al. 2001) |

In ciascuno dei 5 round i quattro giocatori ricevono una dotazione di **10 Unita' di
Energia** (Plutonio / Energy Units) e decidono quanto versare nel fondo comune.
L'energia si accumula progressivamente round dopo round nel Flusso Canalizzatore.
Al termine del **Round 5 (fine gioco)**, se la carica complessiva del gruppo raggiunge
almeno **100 unita' (pari a 1.21 GW)**, il viaggio nel tempo riesce:
**"88 MPH - Viaggio nel tempo riuscito!"** e Marty incassa tutti i punti accumulati.
Se invece il fondo non raggiunge la soglia, si innesca il **"Paradosso Temporale"**:
la linea temporale collassa e i guadagni vengono azzerati (*Collective-Risk failure*, Milinski et al. 2008).

---

## 2. Regole del PGG e valori matematici

Il gioco combina un *public goods game* lineare ripetuto con un **Collective-Risk Social Dilemma (CRSD)** intertemporale.

- **Dotazione per round**: `ENDOWMENT = 10` Unita' di Energia per giocatore (50 totali a testa in 5 round).
- **Fattore moltiplicativo del round**: `MULTIPLIER = 1.6`.
- **Numero di giocatori**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Numero di round**: `NUM_ROUNDS = 5`.

In ciascun round ogni giocatore `i` sceglie un contributo `c_i \in [0, 10]`.
Il payoff provvisorio del round per il giocatore `i` e':

```
payoff_i = 10 - c_i + (1.6 * (c_1 + c_2 + c_3 + c_4)) / 4
```

### Soglia cumulativa a fine gioco (1.21 GW)

- `FLUX_TARGET_GW = 1.21` (potenza necessaria al viaggio nel tempo).
- `CUMULATIVE_TARGET_ENERGY = 100` (somma minima dei contributi di tutti i 4 giocatori sui 5 round).
- Capacita' massima del gruppo nei 5 round: `4 giocatori * 10 unita' * 5 round = 200 unita'`.
- La soglia di 100 unita' corrisponde esattamente al **50% di cooperazione complessiva**.

La potenza del Flusso Canalizzatore cresce proporzionalmente all'energia accumulata:

```
potenza (GW) = (energia_cumulata / 100) * 1.21 GW
```

- **Nei Round 1–4 (fase di accumulo)**: la schermata dei risultati mostra l'avanzamento della carica con una barra di progressione retro, senza emettere sentenze premature.
- **Al Round 5 (verdetto finale)**:
  - Se `energia_cumulata >= 100` (almeno 1.21 GW): **Viaggio nel tempo riuscito (88 MPH)**. Marty conserva il 100% dei punti accumulati nei 5 round.
  - Se `energia_cumulata < 100`: **Paradosso Temporale Innescato**. Il payoff finale viene azzerato (`PARADOX_PAYOFF_RATIO = 0.0`).

---

## 3. Strategie dei bot (Fondamenti Scientifici)

Le strategie dei bot sono basate sulla letteratura empirica sui beni pubblici (*Fischbacher, Gächter & Fehr 2001*; *Milinski et al. 2008*):

### Doc - *Altruistic Cooperator / Target-Pacer*
Versa **sempre 10 unita'** a ogni round per assicurare la base energetica della DeLorean (50 unita' totali).

### Biff - *Pure Free Rider*
Versa **sempre 0 unita'** a ogni round, sfruttando gli altri partecipanti per massimizzare il proprio conto privato.

### Jennifer - *Conditional Cooperator*
Non e' piu' puramente casuale, ma rispecchia il profilo empirico del cooperatore condizionato:
- **Round 1**: offre un contributo benevolo di **5 unita'**.
- **Round 2–5**: calcola la media dei contributi degli altri partecipanti (Marty, Doc, Biff) al round precedente e si allinea ad essa.
  Se Marty coopera generosamente (10), Jennifer risponde versando 7; se Marty diserta (0), Jennifer si ritrae versando 3.

### Marty - umano o bot (Tit-for-Tat)

- **Marty umano** (`marty_strategy = 'human'`): sceglie il contributo tramite la dashboard interattiva (slider da 0 a 10).
- **Marty bot** (`marty_strategy = 'tit_for_tat'`, sessioni/test automatici):
  - **Round 1**: versa **5 unita'**.
  - **Dal round 2**: versa la media (arrotondata) dei contributi forniti dagli altri tre giocatori (Doc, Biff, Jennifer) nel round precedente.

---

## 4. Installazione, esecuzione e configurazione

### Requisiti

- Python 3.9+
- oTree 5+ (consigliato 5.10 o 6.0)

Il file `requirements.txt` contiene `otree` e `numpy` (quest'ultima e' usata
dall'app `quantum_pd`, non dalla PGG).

### Installazione

```bash
pip install -r requirements.txt
```

### Avvio del server di sviluppo

```bash
otree devserver
```

Apri <http://localhost:8000>. Nella pagina iniziale scegli una delle sessioni:

| Sessione | `marty_strategy` | Uso |
|----------|------------------|-----|
| `bttf_pgg_human` | `human` | Marty giocato da un umano (dashboard interattiva) |
| `bttf_pgg_auto`  | `tit_for_tat` | Marty simulato (sessioni/test automatici) |

### Test automatici con i bot

```bash
otree test bttf_pgg_auto
```

In modalita' test Marty e' un bot che usa **Tit-for-Tat** (5 al primo round, poi
la media dei contributi altrui del round precedente).

### Configurazione delle sessioni

Ogni voce di `SESSION_CONFIGS` in `settings.py` accetta tre chiavi personalizzate:

- `marty_strategy` - `'human'` (default) oppure `'tit_for_tat'`.
- `default_language` - lingua di partenza del selettore: `'it'` oppure `'en'`.
- `show_bot_results` - `False` (default, il partecipante vede solo la propria decisione e il risultato aggregato del fondo, senza vedere le strategie e i contributi dei singoli bot) oppure `True` (mostra la tabella analitica con Doc, Biff e Jennifer).

Esempio:

```python
dict(
    name='bttf_pgg_human',
    display_name='Public Goods Game - Ritorno al Futuro (Marty: umano)',
    num_demo_participants=1,
    app_sequence=['bttf_pgg'],
    marty_strategy='human',
    default_language='it',
    show_bot_results=False,
)
```

### Parametri modificabili (in `bttf_pgg/__init__.py`, classe `C`)

| Parametro | Valore | Significato |
|-----------|--------|-------------|
| `NUM_ROUNDS` | `5` | Numero di round |
| `ENDOWMENT` | `10` | Dotazione iniziale per giocatore |
| `MULTIPLIER` | `1.6` | Fattore moltiplicativo del fondo |
| `THRESHOLD_POT` | `30` | Contributo totale minimo per 1.21 GW |
| `FLUX_TARGET_GW` | `1.21` | Potenza obiettivo (GW) |
| `TFT_FIRST_ROUND` | `5` | Contributo Tit-for-Tat al round 1 |

---

## 5. Multilingua (Italiano / Inglese)

L'interfaccia e' completamente bilingue. La prima pagina e' un **selettore di
lingua** ([ IT ] Italiano / [ EN ] English); la scelta viene salvata nel
partecipante e usata per tutte le pagine successive.

Le stringhe sono centralizzate nel dizionario `TEXTS` (chiavi `'it'` e `'en'`)
in `bttf_pgg/__init__.py`.

---

## 6. Architettura (note non ovvie)

- I tre bot sono **virtuali**: `PLAYERS_PER_GROUP = 1` (ogni gruppo = un solo
  umano, Marty). La simulazione dei bot e tutto il calcolo del PGG avvengono in
  `simulate()`, collegata a `ResultsWaitPage.after_all_players_arrive`.
  Non viene usato il framework bot di oTree per i bot avversari (solo per i
  test automatici).
- I template seguono le convenzioni **"lite" di oTree 5+**: file direttamente
  nella cartella dell'app, sintassi `{{ extends }}`, `{{ block }}`, senza tag
  `{% %}`.
- Il tema visivo e' una **dashboard anni '80** (verde/arancione al neon su sfondo
  scuro), definita tramite CSS inline nei template.

## 7. Struttura dei file

```
bttf_pgg/
??? __init__.py            # Modelli, TEXTS, strategie bot, simulate(), pagine, PlayerBot
??? LanguagePage.html      # Selettore lingua
??? IntroPage.html         # Istruzioni e narrativa
??? DecisionPage.html      # Dashboard con slider del contributo
??? ResultsWaitPage.html   # Attesa "calcolo in corso"
??? ResultsPage.html       # Risultati, GW e payoff
```
