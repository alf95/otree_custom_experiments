# Dilemma del Prigioniero Quantistico (protocollo EWL) — Documentazione Tecnica Completa

> Documentazione di riferimento per l'esperimento oTree in questo repository.
> Copre: il significato degli angoli ? e ?, la mossa speciale Q, il perché
> non è obbligatoria e come ometterla (come giocatore o come sperimentatore).

---

## Sommario

1. [Che cos'è il gioco](#1-che-cose-il-gioco)
2. [Il protocollo EWL in sintesi](#2-il-protocollo-ewl-in-sintesi)
3. [Gli angoli ? e ?](#3-gli-angoli-?-e-?)
4. [La matrice di strategia U(?, ?)](#4-la-matrice-di-strategia-u?-?)
5. [L'entanglement: l'operatore J e ?](#5-lentanglement-loperatore-j-e-?)
6. [Il circuito completo](#6-il-circuito-completo)
7. [Esiti e payoff](#7-esiti-e-payoff)
8. [La mossa speciale Q è obbligatoria?](#8-la-mossa-speciale-q-e-obbligatoria)
9. [Come omettere la mossa speciale](#9-come-omettere-la-mossa-speciale)
10. [Verifica matematica degli esiti](#10-verifica-matematica-degli-esiti)
11. [Modello dati e campi esportati](#11-modello-dati-e-campi-esportati)
12. [Note tecniche (gotchas)](#12-note-tecniche-gotchas)

---

## 1. Che cos'è il gioco

Un singolo partecipante **umano** gioca il **Dilemma del Prigioniero** contro un
**bot** (avversario controllato dal computer). In ogni round:

- il partecipante sceglie **due parametri continui**, ? (Theta) e ? (Phi),
  tramite due cursori;
- questi due parametri definiscono una **strategia unitaria** $U(\theta,\phi)$
  applicata al "qubit" del partecipante;
- il bot applica la propria strategia (configurata dallo sperimentatore);
- le due strategie agiscono su una coppia di qubit **entangled**;
- il sistema viene misurato e produce un **esito classico** tra `CC`, `CD`,
  `DC`, `DD` con certe **probabilità quantistiche**;
- l'esito determina i punti del round secondo la classica matrice del
  Dilemma del Prigioniero.

Il protocollo si chiama **EWL**, dalle iniziali di Eisert, Wilkens e Lewenstein
(1999): è il modo standard di "quantizzare" il Dilemma del Prigioniero.

---

## 2. Il protocollo EWL in sintesi

Il flusso è sempre lo stesso, indipendentemente dalle scelte dei giocatori:

1. Il sistema parte nello stato **|00?** (entrambi i qubit a "cooperare").
2. Viene applicato un operatore di **entanglement** $J$, che correla i due qubit.
3. Ogni giocatore applica la propria unitaria $U(\theta,\phi)$ al proprio qubit.
4. Viene applicato l'operatore inverso $J^\dagger$.
5. Lo stato finale viene **misurato** nella base computazionale, ottenendo le
   probabilità dei quattro esiti classici $|CC\rangle, |CD\rangle, |DC\rangle, |DD\rangle$.

In formula, lo stato finale è:

$$
|\psi_f\rangle = J^\dagger \cdot \big(U_h \otimes U_b\big) \cdot J \cdot |00\rangle
$$

dove $U_h$ è la strategia dell'umano (primo qubit) e $U_b$ quella del bot
(secondo qubit). Le probabilità degli esiti sono i moduli quadri delle
componenti di $|\psi_f\rangle$:

$$
P_{XY} = \big|\langle XY | \psi_f \rangle\big|^2
$$

---

## 3. Gli angoli ? e ?

I due cursori non sono quantità astratte: sono i due angoli che parametrizzano
**tutte** le possibili mosse quantistiche di un giocatore.

### 3.1 ? (Theta) — da 0 a ? — la scelta classica

? controlla il **trade-off tra cooperazione e tradimento**.

| Valore | Significato |
|--------|-------------|
| ? = 0      | **Cooperare** (la strategia è l'identità $I$) |
| ? = ?      | **Tradire** (la strategia è $D = \begin{bmatrix}0&1\\-1&0\end{bmatrix}$) |
| ? intermedio | **Mossa mista**: una sovrapposizione quantistica tra C e D |

Intuitivamente: **tutto a sinistra = cooperi, tutto a destra = tradisci**,
come spiega la pagina di gioco.

### 3.2 ? (Phi) — da 0 a ?/2 — la "mossa speciale"

? controlla l'uso della **fase quantistica** che distingue le mosse classiche
da quelle genuinamente quantistiche.

| Valore | Significato |
|--------|-------------|
| ? = 0      | **Mossa classica** (nessun effetto di fase) |
| ? = ?/2    | **Mossa speciale Q** |
| ? intermedio | Mossa quantistica generica |

Intuitivamente: **tutto a sinistra = mossa normale, tutto a destra = mossa
speciale**. Ha effetto soprattutto quando stai cooperando (? ? 0).

### 3.3 Il punto chiave

? e ? **insieme** descrivono ogni possibile strategia unitaria. Le mosse
classiche del Dilemma del Prigioniero (C e D) sono **casi particolari**
con ? = 0: quindi il gioco quantistico *contiene* il gioco classico.

---

## 4. La matrice di strategia U(?, ?)

Ogni giocatore applica al proprio qubit la matrice unitaria:

$$
U(\theta,\phi) =
\begin{bmatrix}
e^{i\phi}\cos(\theta/2) & \sin(\theta/2) \\
-\sin(\theta/2) & e^{-i\phi}\cos(\theta/2)
\end{bmatrix}
$$

Nel codice (`quantum_pd/__init__.py`) è implementata dalla funzione
`unitary(theta, phi)`.

### Le mosse speciali

| Mossa          | ?   | ?      | Matrice $U$                       |
|----------------|-----|--------|-----------------------------------|
| Cooperare (C)  | 0   | 0      | $I = \begin{bmatrix}1&0\\0&1\end{bmatrix}$ |
| Tradire (D)    | ?   | 0      | $\begin{bmatrix}0&1\\-1&0\end{bmatrix}$ |
| Mossa speciale (Q) | 0 | ?/2 | $\begin{bmatrix}i&0\\0&-i\end{bmatrix} = iZ$ |

- **C** = identità: non fa nulla al proprio qubit (lascia "cooperare").
- **D** = "flip" (operatore di defezione classica).
- **Q** = la "mossa miracolo" del protocollo EWL: applica una fase $i$ a
  $|0\rangle$ e $-i$ a $|1\rangle$.

---

## 5. L'entanglement: l'operatore J e ?

L'operatore di entanglement $J$ è costruito **usando lo stesso operatore di
tradimento D** della parametrizzazione (questo è un dettaglio critico, vedi
§12):

$$
J = \cos(\gamma/2)\,(I \otimes I) \;+\; i\,\sin(\gamma/2)\,(D \otimes D)
$$

dove $D = U(\pi, 0)$.

Il parametro **? (GAMMA)** è l'intensità della correlazione quantistica:

- ? = 0 ? nessun entanglement (il gioco è puramente classico);
- **? = ?/2** ? stato di **Bell massimamente entangled** (valore standard del
  protocollo, usato in questo esperimento).

> ?? Nel codice, `GAMMA = math.pi / 2`. Il commento avvisa di **non modificarlo**
> se non si sa cosa si sta facendo: è il valore che rende il protocollo
> corretto.

---

## 6. Il circuito completo

```mermaid
flowchart LR
    subgraph "Qubit umano"
        H0[|0?]
    end
    subgraph "Qubit bot"
        B0[|0?]
    end
    H0 --> J[Entanglement J]
    B0 --> J
    J --> UH[Strategia umana U_h]
    J --> UB[Strategia bot U_b]
    UH --> JD[J†]
    UB --> JD
    JD --> M[Misura]
    M --> O[P_CC, P_CD, P_DC, P_DD]
```

Il calcolo è implementato in `ewl_probabilities(theta_h, phi_h, theta_b, phi_b, gamma)`:

```python
J = entanglement_operator(gamma)
U_h = unitary(theta_h, phi_h)
U_b = unitary(theta_b, phi_b)
U_total = np.kron(U_h, U_b)

psi0 = np.zeros(4, dtype=complex)
psi0[0] = 1.0                      # |00>

psi_final = J.conj().T @ U_total @ J @ psi0
probs = np.real(psi_final * np.conj(psi_final))
probs = probs / probs.sum()
return [float(probs[0]), float(probs[1]), float(probs[2]), float(probs[3])]
```

La convenzione è: **primo qubit = umano, secondo qubit = bot**, e `0` = coopera,
`1` = tradisce. Quindi:

- `P_CC` ? entrambi cooperano
- `P_CD` ? umano coopera, bot tradisce
- `P_DC` ? umano tradisce, bot coopera
- `P_DD` ? entrambi tradiscono

---

## 7. Esiti e payoff

La matrice classica dei payoff (punti del **partecipante**) è definita in
`C` in `__init__.py`:

| Esito | Umano | Bot | Punti umano | Punti bot |
|-------|-------|-----|-------------|-----------|
| `CC`  | coopera | coopera | 3 | 3 |
| `CD`  | coopera | tradisce | 0 | 5 |
| `DC`  | tradisce | coopera | 5 | 0 |
| `DD`  | tradisce | tradisce | 1 | 1 |

Dopo il calcolo delle probabilità, il backend calcola:

- **Payoff atteso** = media pesata dei quattro payoff sulle probabilità;
- **Payoff effettivo del round** = payoff dell'esito **estratto a sorte** con
  `random.choices` usando le quattro probabilità come pesi.

---

## 8. La mossa speciale Q è obbligatoria?

**No, non è obbligatoria.**

Nella versione quantistica ogni giocatore sceglie liberamente $U(\theta,\phi)$
con $\theta \in [0,\pi]$ e $\phi \in [0,\pi/2]$. La mossa speciale
$Q = U(0,\pi/2)$ è **solo uno** degli infiniti punti di questo spazio:

- le mosse classiche ($\phi = 0$) sono casi particolari della parametrizzazione;
- un giocatore può giocare **perfettamente in modo classico** dentro lo stesso
  gioco quantistico;
- il bot stesso ha strategie sia classiche sia quantistiche (vedi
  `BOT_STRATEGIES`).

### Perché allora è importante?

Perché è l'unica mossa che **cambia l'equilibrio del gioco**:

- Se **entrambi** giocano Q ? esito **CC** con payoff **(3, 3)**: è la "miracolo"
  che risolve il dilemma (nel gioco classico l'equilibrio di Nash è DD con (1,1)).
- Se un giocatore gioca Q e l'altro D, l'entanglement altera le probabilità
  rispetto al caso classico, eliminando la trappola del dilemma.

In sintesi: la "versione quantistica" non **impone** Q, semplicemente **la
permette**. Q è ciò che rende il gioco *davvero* quantistico.

---

## 9. Come omettere la mossa speciale

Ci sono due livelli distinti: come **giocatore** e come **sperimentatore**.

### 9.1 Come giocatore: non usarla mai

Basta tenere **? = 0** (cursore "mossa speciale" tutto a sinistra). Con ? = 0
le mosse sono solo classiche e il gioco coincide esattamente con il Dilemma del
Prigioniero classico:

| Mossa | ? | ? | Matrice |
|-------|---|---|---------|
| C | 0 | 0 | I |
| D | ? | 0 | [[0,1],[-1,0]] |

### 9.2 Come sperimentatore: toglierla dall'esperimento

Se vuoi che i partecipanti **non abbiano affatto** la possibilità di usarla,
ci sono due opzioni.

#### Opzione A — Rimuovere il cursore ? (consigliata)

I partecipanti vedono solo il cursore ?; ? viene forzato a 0 nel backend.

**Passo 1** — In `quantum_pd/DecisionePage.html`, elimina l'intera card del
cursore ? (il blocco `<div class="card mb-4">` con `name="phi"`), e rimuovi
dalla funzione `setPreset` il terzo bottone "Mossa speciale".

**Passo 2** — In `quantum_pd/__init__.py`:

1. Cambia il valore iniziale del campo:

   ```python
   phi = models.FloatField(
       min=0, max=math.pi / 2, initial=0.0,
       label="Quanto usi la mossa speciale (0 = no, pi/2 = si)",
   )
   ```

2. Togli `phi` dai campi del form e forza il valore a 0 prima della simulazione:

   ```python
   class DecisionePage(Page):
       form_model = 'player'
       form_fields = ['theta']

       @staticmethod
       def before_next_page(player, timeout_happened):
           player.phi = 0.0
   ```

   In alternativa (o in aggiunta), forza ? = 0 dentro `simulate()`:

   ```python
   def simulate(group):
       for player in group.get_players():
           player.phi = 0.0   # mossa speciale disattivata
           # ...resto invariato...
   ```

#### Opzione B — Forzare ? = 0 solo nel backend

Lasci il form com'è (cursore visibile) ma azzeri ? prima del calcolo, in modo
che qualunque cosa faccia il partecipante valga solo ?:

```python
def simulate(group):
    for player in group.get_players():
        player.phi = 0.0   # ignora la mossa speciale
        # ...resto invariato...
```

### Attenzione: l'entanglement resta comunque

Anche con ? = 0, l'operatore $J$ (con ? = ?/2) **viene applicato comunque**.
La differenza è osservabile solo se **qualcuno** usa Q:

- nessuno usa Q ? l'entanglement non produce alcun effetto osservabile, e il
  gioco è identico al classico;
- qualcuno usa Q ? l'entanglement cambia le probabilità e rompe il dilemma.

Quindi, se ometti Q del tutto, stai eseguendo un **PD classico** con un
overhead quantistico inutile: per un esperimento puramente classico basterebbe
il gioco classico senza qubit.

---

## 10. Verifica matematica degli esiti

Con ? = ?/2 (Bell), il protocollo riproduce esattamente il gioco classico
quando ? = 0, e la "miracolo" quando entrambi giocano Q:

| Umano | Bot | Esito | Payoff (umano, bot) |
|-------|-----|-------|---------------------|
| C (0,0)   | C (0,0)   | CC | (3, 3) |
| C (0,0)   | D (?,0)   | CD | (0, 5) |
| D (?,0)   | C (0,0)   | DC | (5, 0) |
| D (?,0)   | D (?,0)   | DD | (1, 1) |
| Q (0,?/2) | Q (0,?/2) | CC | (3, 3) |

Questi sono gli esiti "verificati" riportati anche in `AGENTS.md`. Il punto
critico che garantisce la miracolo è che $J$ sia costruito con **lo stesso D**
della parametrizzazione (vedi §12).

---

## 11. Modello dati e campi esportati

I campi del modello `Player` (esportati nella scheda **Data** di oTree):

| Campo | Tipo | Significato |
|-------|------|-------------|
| `theta`, `phi` | Float | Angoli scelti dall'umano |
| `bot_strategy` | String | Chiave della strategia del bot (da `session.config`) |
| `bot_theta`, `bot_phi` | Float | Angoli del bot per il round |
| `prob_cc`, `prob_cd`, `prob_dc`, `prob_dd` | Float | Probabilità dei quattro esiti |
| `outcome` | String | Esito estratto (`CC`, `CD`, `DC`, `DD`) |
| `payoff_round` | Float | Punti dell'umano nel round |
| `bot_payoff` | Float | Punti del bot nel round |
| `expected_payoff` | Float | Payoff atteso dell'umano |
| `expected_bot_payoff` | Float | Payoff atteso del bot |

Le strategie del bot (`BOT_STRATEGIES` in `C`) sono:

| Chiave | Comportamento |
|--------|---------------|
| `always_classical_cooperate` | Coopera sempre: $U(0,0)$ |
| `always_classical_defect` | Tradisce sempre: $U(\pi,0)$ |
| `always_quantum` | Mossa speciale $Q = U(0,\pi/2)$ |
| `random` | ? ~ U(0,?), ? ~ U(0,?/2) a ogni round |
| `tit_for_tat` | Copia gli angoli del round precedente (round 1 = coopera) |

---

## 12. Note tecniche (gotchas)

1. **Stesso operatore D.** $J$ **deve** essere costruito con lo stesso operatore
   di defezione $D = U(\pi,0)$ usato dalla parametrizzazione. Usare $\sigma_x$
   invece di D rompe silenziosamente la "mossa miracolo": $(Q,Q)$ darebbe DD
   invece di CC.

2. **Cast a `float`.** I risultati numpy vanno convertiti a `float` Python
   prima di salvarli nei campi del modello (oTree 5.x ha un bug con i dtype
   numpy nei campi). Il codice già lo fa.

3. **`numpy` non è installato in questo ambiente di sviluppo**: la fisica è
   stata verificata con uno script in puro Python (`cmath`). Per verificare la
   matematica senza numpy, replica il circuito con `cmath`.

4. **Convenzioni oTree 5+.** Template direttamente nella cartella dell'app con
   nome esatto `<PageName>.html`; costanti in `C(BaseConstants)`; pagine con
   `form_model` + `form_fields` e metodi `@staticmethod`; slider in HTML grezzo
   che si legano al modello solo perché il `name` coincide con un campo di
   `form_fields`.
