# Specifica delle Modifiche al Codice e ai Testi

## Panoramica
Il presente documento contiene l'elenco dettagliato delle modifiche da apportare all'applicazione dell'esperimento della **Notte dei Ricercatori** (Variante "Adulti" / DeLorean) e al **Pizza Game**. 

Le modifiche sono strutturate per categorie operative (Terminologia e Testi, Logica di Gioco e Payoff, Struttura dei Round e Interfaccia Utente).

---

## Parte 1: Esperimento "Notte dei Ricercatori" (Variante Adulti - DeLorean)

### 1. Terminologia e Testi di Gioco

* **1.1 Alimentazione e Fondi DeLorean:**
  - Sostituire la dicitura `"fondi per alimentare l'esperimento"` con una delle seguenti opzioni:
    - *Opzione A:* `"fondi per alimentare la DeLorean"`
    - *Opzione B:* `"fondi per finanziare l'approvvigionamento di energia per far partire la DeLorean"`

* **1.2 Cassa Comune $\rightarrow$ Fondo Comune:**
  - Sostituire in tutto l'esperimento le parole `"cassa comune"` e `"cassa"` con **`"fondo comune"`**.
  - **Eccezione / Prima occorrenza:** Alla prima apparizione del termine nell'esperimento, scrivere la forma estesa:
    > `"fondo comune per consentire il funzionamento della DeLorean"`

* **1.3 Integrazioni Terminologiche Specifiche:**
  - Inserire la dicitura **`"fondo DeLorean"`** nei punti opportuni.
  - Inserire la dicitura **`"nel fondo comune per la DeLorean"`**.
  - Inserire la dicitura **`"quota del fondo comune"`**.
  - Includere la dicitura **`"donate dai membri del gruppo"`**.
  - Sostituire la locuzione `"messe insieme"` con **`"sommate"`**.

---

### 2. Logica di Gioco, Payoff e Unità di Misura (Monete vs Energia)

* **2.1 Calcolo del Payoff:**
  - Nel testo o nella schermata esplicativa del calcolo del payoff, sostituire tutta la parte che segue il segno `+` con la seguente formulazione:
    > `+ la tua parte derivante dalla suddivisione equa del fondo comune (ricorda che quello che ricevi dipende anche dalle scelte effettuate dagli altri membri del gruppo)`

* **2.2 Unificazione / Standardizzazione Valuta (Monete vs Energia):**
  - *Problema riscontrato:* Parlare contemporaneamente di "monete" e di "energia" genera confusione nei soggetti sperimentali.
  - *Azione richiesta:* Applicare una delle due soluzioni seguenti:
    - **Soluzione A (Consigliata):** Eliminare completamente i riferimenti alle `"monete"` anche nella schermata dei risultati, mantenendo la spiegazione legata unicamente all'energia.
      - *Esempio:* Sostituire `"sono state cumulate TOT monete"` con `"in questo round, sono stati raggiunti TOT GW di energia"`.
    - **Soluzione B:** Qualora si debbano mantenere entrambi i termini, specificare chiaramente fin dall'inizio dell'esperimento l'equivalenza vincolante (es. `1 moneta = 1 unità di energia` oppure `1 moneta = TOT unità di energia`).

---

### 3. Struttura dei Round e Trasparenza Temporale

*Nota metodologica: Per evitare che la conoscenza del numero finale di round influenzi il comportamento strategico dei soggetti (effetto "endgame"), il numero complessivo dei round NON deve essere visibile.*

* **3.1 Rimozione riferimenti al totale dei round nei testi:** Eliminare qualsiasi menzione alla durata di 5 round da tutte le istruzioni dell'esperimento.
* **3.2 Header dei Round (UI):** Eliminare in alto la dicitura `"Round X di 5"` (es. `"Round 1 di 5"`, ..., `"Round 5 di 5"`). Mostrare solo l'indicatore generico o progressivo (es. `"Round 1"`, `"Round 2"`, ecc.).
* **3.3 Indicatori temporali residui:** Eliminare ovunque la dicitura `"ancora X rounds"`.

---

### 4. Interfaccia Utente (UI / UX)

* **4.1 Rimozione Scelte Veloci:** Eliminare il pannello con i pulsanti di "scelta veloce" (preset buttons).
* **4.2 Input Slider:** Mantenere esclusivamente lo slider di selezione comprende tutte le opzioni di scelta possibili nell'intervallo consentito.

---

## Parte 2: Pizza Game

### 1. Modifica Terminologica
* Sostituire la dicitura **`"amico reciproco"`** con **`"amico equo"`** in tutto il testo, nell'interfaccia utente e nei materiali relativi al Pizza Game.

---

## Summary Checklist per Opencode

- [ ] (Punto 1) Sostituito "fondi per alimentare l'esperimento" con variante DeLorean.
- [ ] (Punto 2 & 9) Sostituito "cassa comune"/"cassa" con "fondo comune" (con dicitura estesa alla prima occorrenza).
- [ ] (Punto 3) Inserito "fondo DeLorean".
- [ ] (Punto 4) Sostituito "messe insieme" con "sommate".
- [ ] (Punto 5) Aggiornata la formula del payoff post `+`.
- [ ] (Punto 6) Inclusa la dicitura "donate dai membri del gruppo".
- [ ] (Punto 7 & 13) Unificata la terminologia Monete/Energia (o definito il tasso di cambio).
- [ ] (Punto 8, 12, 15) Rimosso ogni riferimento ai 5 round ("Round X di 5", "ancora X rounds", ecc.).
- [ ] (Punto 10) Rimosse le "scelte veloci" lasciando solo lo slider.
- [ ] (Punto 11) Inserito "nel fondo comune per la DeLorean".
- [ ] (Punto 14) Inserito "quota del fondo comune".
- [ ] (Pizza Game) Sostituito "amico reciproco" con "amico equo".