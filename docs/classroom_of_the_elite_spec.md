# Specifiche di Progetto: Classroom of the Elite — Special Exam Game (oTree 5+)

Il presente documento definisce la progettazione e il piano di replica sperimentale di un gioco interattivo basato sulle dinamiche di teoria dei giochi dell'opera **"Classroom of the Elite"** (*Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e*), ambientato presso la prestigiosa *Advanced Nurturing High School* (ANHS).

---

## 1. Visione Generale e Motivazione Scientifica

L'universo narrativo di *Classroom of the Elite* ruota attorno a esami speciali strutturati come veri e propri **giochi strategici con informazione asimmetrica**, incentrati su:
- Conflitto tra interesse individuale (Punti Privati, PP) e bene collettivo (Punti Classe, CP).
- Dilemmi del prigioniero a informazione imperfetta e incompletezza informativa.
- Dinamiche di segnalazione (*signaling*), inganno strategico (*bluffing*) e deduzione sociale.

La presente replica adatta la struttura sperimentale già collaudata nel repository (architettura oTree 5+ "lite", interfaccia a forte identità visiva, 1 partecipante umano integrato con compagni/avversari virtuali che seguono profili comportamentali noti in letteratura).

---

## 2. Selezione del Gioco: *Zodiac VIP Exam* (L'Esame della Nave da Crociera)

Tra i vari test presenti nella serie, lo **Zodiac Exam (Esame dei Pianeti / VIP Test - Vol. 4)** costituisce il modello di teoria dei giochi più celebre, rigoroso e adatto all'economia sperimentale.

### 2.1 Struttura del Gruppo e Assegnazione
- Gli studenti delle quattro classi in competizione (**Classe A, Classe B, Classe C, Classe D**) vengono suddivisi in gruppi interclasse da 4 studenti (uno per classe).
- Il partecipante umano interpreta lo studente della **Classe D** (Kiyotaka Ayanokoji).
- I tre rivali sono controllati da bot che personificano i leader canonici delle altre classi:
  - **Classe A**: Kohei Katsuragi (profilo conservatore e difensivo).
  - **Classe B**: Honami Ichinose (profilo cooperativo e pro-sociale).
  - **Classe C**: Kakeru Ryuen (profilo aggressivo e opportunista).
- La scuola seleziona in segreto **1 solo studente come "VIP"** (il bersaglio segreto) all'interno del gruppo.

---

## 3. Matrice delle Regole e dei Payoff (I 4 Casi Canonici)

La sessione si conclude con uno dei quattro esiti ufficiali previsti dal regolamento della scuola:

| Caso | Condizione di Chiusura | Payoff Classe VIP | Payoff VIP (Singolo) | Payoff Membri Gruppo | Payoff Traditore (Se presente) |
|---|---|---|---|---|---|
| **Caso 1: Fiducia Totale** *(Mutual Trust / Silence)* | Nessuno tenta tradimenti; al termine il gruppo concorda e preserva l'equilibrio. | **+50 CP** per la classe del VIP | **+500.000 PP** | **+500.000 PP** ciascuno | *Nessuno* |
| **Caso 2: Tradimento Anticipato Vincente** *(Early Betrayal Success)* | Uno studente di una classe rivale indovina e denuncia il VIP prima della scadenza. | **-50 CP** (penalità pesante) | **0 PP** | **0 PP** | **+50 CP** alla sua classe & **+500.000 PP** personali |
| **Caso 3: Falsa Accusa** *(Failed Sabotage / Penalty)* | Uno studente invia una denuncia errata (accusando un non-VIP). | **+50 CP** alla classe del VIP | **+500.000 PP** | **0 PP** | **-50 CP** alla classe di chi ha sbagliato |
| **Caso 4: Stallo / Mancata Intesa** *(Stalemate / Zero Consensus)* | Nessuna denuncia, ma il gruppo non trova un accordo cooperativo finale. | **0 CP** | **+500.000 PP** | **0 PP** | *Nessuno* |

### Note sui Punti dell'ANHS
- **Class Points (CP)**: Determinano il prestigio e il rango della classe (da Classe D verso Classe A). Hanno valore collettivo puro.
- **Private Points (PP)**: Valuta personale spendibile dal singolo studente.

---

## 4. Profili Comportamentali dei Bot (Agenti Virtuali)

In coerenza con l'architettura degli altri esperimenti (`bttf_pgg` e `pizza_pgg`), i bot non si limitano a scelte casuali, ma incarnano specifiche euristiche decisionali:

1. **Honami Ichinose (Classe B) — Cooperatore Puro**:
   - Propone costantemente la cooperazione aperta per raggiungere il **Caso 1** (500.000 PP per tutti).
   - Non invia mai accuse anticipate. Se interrogata, condivide informazioni in buona fede.
2. **Kakeru Ryuen (Classe C) — Predatore Opportunista**:
   - Usa un'euristica aggressiva basata sulla probabilità: tenta di individuare il VIP per conquistare il **Caso 2**.
   - Se stima che la probabilità di indovinare superi una soglia prefissata (es. $p > 0.60$), invia l'accusa anticipata.
3. **Kohei Katsuragi (Classe A) — Difensore Conservatore**:
   - Evita il rischio a ogni costo per proteggere il primato della Classe A.
   - Non tenta denunce al buio per non incorrere nella penalità del **Caso 3** (-50 CP). Promuove il silenzio strategico.

---

## 5. Architettura Applicativa oTree 5+ (`cote_zodiac`)

### 5.1 Struttura File
```text
cote_zodiac/
├── __init__.py           # Logica di backend, modelli, simulate(), calcolo casi e bot
├── IntroPage.html        # Introduzione narrativa ANHS, S-System e composizione gruppo
├── VIPRevealPage.html    # Schermata segreta con rivelazione dello status VIP personale
├── DiscussionPage.html   # Fase interattiva di consultazione e indizi tra compagni
├── DecisionPage.html     # Scelta strategica (Attendi / Coopera vs Denuncia VIP anticipata)
└── ResultsPage.html      # Verdetto della scuola (Caso 1-4), assegnazione CP/PP e classifica
```

### 5.2 Sequenza delle Pagine e Flusso Utente
1. **`IntroPage`**:
   - Spiegazione delle regole dell'Esame Speciale della Nave da Crociera.
   - Presentazione dei membri del gruppo (Katsuragi A, Ichinose B, Ryuen C, Ayanokoji D).
   - Riepilogo visivo della matrice a 4 casi (CP vs PP).
2. **`VIPRevealPage`**:
   - Notifica individuale riservata: il sistema notifica se il giocatore è il **VIP** oppure un **Membro Ordinario**.
3. **`DiscussionPage`**:
   - Fase di deliberazione: visualizzazione delle dichiarazioni e degli indizi offerti dagli altri 3 studenti.
   - Scelta di un atteggiamento da comunicare (Trasparente, Neutrale, Sospettoso).
4. **`DecisionPage`**:
   - Il bivio strategico:
     - **Opzione A**: *Attendi la fine dell'esame* (Punta alla cooperazione / Caso 1).
     - **Opzione B**: *Invia una denuncia anticipata alla scuola*, selezionando chi ritieni sia il VIP tra i compagni.
5. **`ResultsPage`**:
   - Verdetto ufficiale della commissione d'esame.
   - Dettaglio del caso scattato (Caso 1, 2, 3 o 4) con motivazione.
   - Variazione dei Class Points (CP) di ciascuna classe (+50 / 0 / -50) e Punti Privati (PP) guadagnati dal giocatore.
   - Classifica aggiornata della scuola con transizione di rango.

---

## 6. UI / UX Design System: *Advanced Nurturing High School Terminal*

In conformità alle linee guida estetiche del progetto, l'interfaccia adotta un'identità visiva esclusiva:
- **Sfondo**: Deep Navy Accademico (`#0a0f1d`) con accenti scuri (`#121b2f`).
- **Colori Primari delle Classi**:
  - Classe A: Viola Regale (`#6f42c1`)
  - Classe B: Verde Teal Istituzionale (`#20c997`)
  - Classe C: Rosso Scarlatto Rivoluzionario (`#d9383a`)
  - Classe D: Blu / Azzurro Oltremare (`#0d6efd`)
- **Accenti di Prestigio**: Oro d'élite (`#d4af37`) per badge, Punti Classe e Flusso S-System.
- **Tipografia**: Caratteri ad alta leggibilità e moderni (*Montserrat* / *Segoe UI*), con display numerici chiari per i contatori CP e PP.

---

## 7. Configurazione Sessioni (`settings.py`)

Aggiunta delle voci dedicate in `SESSION_CONFIGS`:
- `name='cote_zodiac_human'`: Partecipante umano che controlla la Classe D, con 3 bot avversari (Classe A, B, C).
- `name='cote_zodiac_auto'`: Modalità simulata automatica per testing rapido e validazione empirica.

---

## 8. Piano di Rilascio e Roadmap

- **Fase 1 (Completata con PR)**: Approvazione del documento formale di specifica e architettura di replica.
- **Fase 2**: Implementazione dell'app `cote_zodiac/` con modelli, template stilizzati e logica di simulazione a 4 casi.
- **Fase 3**: Integrazione con la scheda di registrazione anagrafica e inserimento nella dashboard sperimentale unificata.
