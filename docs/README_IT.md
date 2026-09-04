# Public Goods Game - "Ritorno al Futuro" (Documentazione IT)

Applicazione **oTree** che implementa un **Public Goods Game (PGG) classico a 4 giocatori** (1 utente umano + 3 bot), ambientato nella narrativa di **"Ritorno al Futuro"** (*Back to the Future*).

Questa versione è stata specificamente **semplificata e ottimizzata didatticamente per ragazzi e studenti dai 10 ai 18 anni**, introducendo una **dotazione monetaria tangibile (Monete / Salvadanaio)** per rendere immediatamente percepibile l'importanza delle proprie risorse e il trade-off con il bene pubblico.

---

## 1. Descrizione generale e narrativa per ragazzi (10-18 anni)

Sei **Marty McFly**, nel 1985. La **DeLorean** è ferma e il **Flusso Canalizzatore** (*Flux Capacitor*) è scarico: per viaggiare nel tempo e tornare al futuro serve una potenza di almeno **1.21 GW**. Doc Brown ha bisogno di fondi per alimentare l'esperimento scientifico.

Insieme a te giocano altri tre compagni di Hill Valley:

| Giocatore | Tipo | Carattere / Strategia | Ruolo Comportamentale (Letteratura) |
|-----------|------|-----------------------|-----------------------------------|
| **Marty** | Umano (o bot nei test) | Scelta libera / Tit-for-Tat | Giocatore decisionale (pivotal) |
| **Doc**   | Bot  | Generoso (Altruista) | Altruist / Target-Pacer (Milinski et al. 2008) |
| **Biff**  | Bot  | Egoista (Free Rider) | Pure Free Rider (Fischbacher et al. 2001) |
| **Jennifer** | Bot | Reciproca (Cooperatore Condizionato) | Reattiva/Reciproca (Fischbacher et al. 2001) |

### La dotazione monetaria e il Salvadanaio personale
In ciascuno dei 5 round ogni giocatore riceve **10 Monete personali (🪙)**:
1. **🔒 Nel tuo Salvadanaio**: le monete che decidi di NON donare restano subito al sicuro nel tuo salvadanaio personale.
2. **⚡ Nella Cassa per la DeLorean**: le monete donate da te e dagli altri vengono raccolte insieme, moltiplicate per **1.6** da Doc (crescono del 60%!) e divise in 4 parti uguali tra tutti i partecipanti.
3. **💰 Guadagno del round**: `Monete tenute nel salvadanaio + quota della cassa comune`.

---

## 2. Obiettivo finale collettivo (1.21 GW - 100 Monete)

Il gioco combina la dinamica dei beni pubblici ripetuta con un **Collective-Risk Social Dilemma (CRSD)** intertemporale:

- **Dotazione per round**: `ENDOWMENT = 10` Monete a giocatore (50 totali in 5 round).
- **Fattore moltiplicativo**: `MULTIPLIER = 1.6`.
- **Numero di giocatori**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Numero di round**: `NUM_ROUNDS = 5`.
- **Soglia di successo collettivo**: `CUMULATIVE_TARGET_MONEY = 100` monete complessive donate dal gruppo in 5 round (pari a 1.21 GW). 100 monete corrisponde al 50% di cooperazione complessiva del gruppo (capacità massima: `4 * 10 * 5 = 200`).

### Verdetto finale (Round 5)
- Se a fine gioco il gruppo ha donato **almeno 100 Monete (1.21 GW)**:
  **"88 MPH - Viaggio nel tempo riuscito!"** La DeLorean parte e raggiunge le 88 MPH.
- Se il gruppo ha donato **meno di 100 Monete**:
  **"Paradosso Temporale!"** La macchina resta a secco e non parte.

> **Nessuna perdita possibile**: in entrambi i casi il partecipante tiene **sempre**
> tutte le monete accumulate nel proprio salvadanaio (`final_game_payoff` = totale
> accumulato). Il verdetto successo/fallimento ha solo valore narrativo e non azzera
> alcun guadagno.

---

## 3. Strategie dei bot (Fondamenti Scientifici)

Le strategie dei compagni virtuali riflettono i profili empirici classici della letteratura sperimentale (*Fischbacher, Gächter & Fehr 2001*; *Milinski et al. 2008*):

### Doc Brown - *Generoso / Altruistic Cooperator*
Dona **sempre 10 monete** a ogni round per garantire una solida base per la macchina del tempo (50 monete complessive).

### Biff Tannen - *Egoista / Pure Free Rider*
Dona **sempre 0 monete**, tenendo tutto nel proprio salvadanaio e approfittando della generosità altrui.

### Jennifer Parker - *Reciproca / Conditional Cooperator*
- **Round 1**: offre un contributo amichevole di **5 monete**.
- **Round 2–5**: osserva le scelte degli altri (Marty, Doc, Biff) al round precedente e dona un importo pari alla media del loro contributo. Se Marty dona 10, Jennifer donerà 7; se Marty dona 0, Jennifer si ritrarrà donando 3.

### Marty - Umano o simulato (Tit-for-Tat)
- **Umano** (`marty_strategy = 'human'`): gioca tramite la dashboard interattiva con visual feedback immediato in tempo reale (doppio contatore *Salvadanaio* vs *Cassa DeLorean*).
- **Bot automatico** (`marty_strategy = 'tit_for_tat'`): dona 5 monete al round 1, poi la media arrotondata degli altri 3 giocatori.

---

## 4. Esperienza utente per la fascia 10-18 anni

1. **Doppio contatore dinamico (`DecisionPage.html`)**:
   Mentre il ragazzo sposta il cursore, vede in tempo reale:
   - 🟢 **Nel tuo Salvadanaio**: `10 - X` monete (in verde neon)
   - ⚡ **Nella Cassa DeLorean**: `X` monete (in arancione)
   Questo elimina la necessità di calcoli a mente e rende lampante l'effetto della decisione.

2. **Calcolo passo-passo trasparente (`ResultsPage.html`)**:
   Invece di formule matematiche opache, il ragazzo vede l'addizione lineare chiara:
   `Monete tenute + quota cassa comune = guadagno round`, con il saldo progressivo del proprio salvadanaio.

3. **Barra di carica a batteria**:
   Progresso visivo costante verso i 1.21 GW e le 100 monete necessarie.

---

## 5. Installazione, esecuzione e test

### Requisiti
- Python 3.9+
- oTree 5+

### Avvio locale
```bash
otree devserver
```
Apri <http://localhost:8000> e seleziona:
- `bttf_pgg_human`: Marty giocato da un partecipante umano.
- `bttf_pgg_auto`: Marty simulato per test rapidi.

### Test automatici (bilingue IT ed EN)
```bash
otree test bttf_pgg_auto
```
Il test esegue automaticamente entrambi i percorsi in lingua italiana e in lingua inglese, verificando tutti i 5 round e i calcoli.

---

## 6. Configurazione delle sessioni (`settings.py`)

- `marty_strategy`: `'human'` o `'tit_for_tat'`
- `default_language`: `'it'` o `'en'`
- `show_bot_results`: `False` (default, mostra solo la scelta di Marty e il totale del fondo) oppure `True` (mostra la tabella dettagliata di tutti i compagni).
