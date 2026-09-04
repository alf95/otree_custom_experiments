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

| Giocatore | Tipo | Strategia |
|-----------|------|-----------|
| **Marty** | Umano (o bot nei test) | Scelta libera / Tit-for-Tat |
| **Doc**   | Bot  | Always Cooperate |
| **Biff**  | Bot  | Always Defect |
| **Jennifer** | Bot | Random |

In ogni round i quattro giocatori ricevono una dotazione di **10 Unita' di
Energia** (Plutonio / Energy Units) e decidono quanto versare nel fondo comune.
Se il fondo supera la soglia di **1.21 GW** il viaggio nel tempo riesce -
**"Viaggio nel tempo riuscito (88 MPH)!"** - altrimenti si innesca un
**"Paradosso Temporale Innescato!"**.

---

## 2. Regole del PGG e valori matematici

Il gioco e' un *public goods game* lineare standard.

- **Dotazione iniziale** per giocatore: `ENDOWMENT = 10` Unita' di Energia.
- **Fattore moltiplicativo** del fondo comune: `MULTIPLIER = 1.6`.
- **Numero di giocatori**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Numero di round**: `NUM_ROUNDS = 5` (modificabile in `C`).

Ogni giocatore `i` sceglie un contributo `c_i` compreso tra `0` e `10`.
Il payoff del round per il giocatore `i` e':

```
payoff_i = 10 - c_i + (1.6 * (c_1 + c_2 + c_3 + c_4)) / 4
```

In pratica:

1. Si sommano i contributi dei 4 giocatori: `fondo = c_marty + c_doc + c_biff + c_jennifer`.
2. Il fondo viene moltiplicato per `1.6`.
3. Il fondo moltiplicato viene diviso in **4 parti uguali**.
4. Il guadagno di ciascuno e': *10 - contributo versato + la propria quota*.

**Esempio**: se tutti versano 10 -> fondo `40 x 1.6 = 64`, quota `16` a testa,
payoff `10 - 10 + 16 = 16` a testa.

### Soglia narrativa (1.21 GW)

- `FLUX_TARGET_GW = 1.21` (potenza necessaria al viaggio nel tempo).
- `THRESHOLD_POT = 30` (contributo totale minimo per raggiungere 1.21 GW).

La potenza del Flusso Canalizzatore e' calcolata cosi':

```
potenza (GW) = (1.6 * fondo) * (1.21 / (30 * 1.6))
```

Il fondo moltiplicato di soglia vale `30 x 1.6 = 48` unita', che corrisponde
esattamente a **1.21 GW**. Il viaggio riesce quando
`fondo totale >= THRESHOLD_POT` (cioe' almeno 30 unita' versate in totale).

---

## 3. Strategie dei bot

Le strategie sono implementate in `bttf_pgg/__init__.py`.

### Doc - *Always Cooperate*
Versa **sempre 10 unita'** a ogni round.

```python
doc = C.ENDOWMENT  # 10
```

### Biff - *Always Defect*
Versa **sempre 0 unita'** a ogni round.

```python
biff = 0
```

### Jennifer - *Random*
Versa un **ammontare casuale** (intero uniforme in `[0, 10]`) a ogni round.

```python
jennifer = random.randint(0, C.ENDOWMENT)
```

### Marty - umano o bot (Tit-for-Tat)

- **Marty umano** (`marty_strategy = 'human'`): sceglie il contributo tramite la
  **dashboard interattiva** (slider da 0 a 10).
- **Marty bot** (`marty_strategy = 'tit_for_tat'`, sessioni/test automatici):
  - **Round 1**: versa **5 unita'** (`TFT_FIRST_ROUND = 5`).
  - **Dal round 2**: versa la **media (arrotondata) dei contributi forniti dagli
    altri tre giocatori (Doc, Biff, Jennifer) nel round precedente**.

```python
def marty_tit_for_tat_contribution(player):
    if player.round_number == 1:
        return C.TFT_FIRST_ROUND
    prev = player.in_round(player.round_number - 1)
    others = [prev.doc_contribution, prev.biff_contribution, prev.jennifer_contribution]
    return int(round(sum(others) / len(others)))
```

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
