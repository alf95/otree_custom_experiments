# Public Goods Game - "Back to the Future" (EN Documentation)

An **oTree** application implementing a **classic 4-player Public Goods Game (PGG)** (1 human + 3 bots), framed in the **"Back to the Future"** narrative.

This edition has been **simplified and pedagogically adapted for youth and students aged 10 to 18 years old**, introducing a **tangible monetary endowment (Coins / Piggy Bank)** to make the value of personal endowments and the public-goods trade-off immediately intuitive.

---

## 1. Narrative & Overview for Young Participants (10-18 Years)

You are **Marty McFly**, in 1985. The **DeLorean** is stranded and the **Flux Capacitor** is drained: to travel back to the future, you need **1.21 GW** of power. Doc Brown needs funds to power up the scientific equipment.

Three other Hill Valley friends are in the game with you:

| Player | Type | Personality / Strategy | Behavioral Role (Literature) |
|--------|------|------------------------|-------------------------------|
| **Marty** | Human (or bot in tests) | Free choice / Tit-for-Tat | Decision maker (pivotal) |
| **Doc**   | Bot  | Generous (Always Cooperates) | Altruist / Target-Pacer (Milinski et al. 2008) |
| **Biff**  | Bot  | Selfish (Pure Free Rider) | Pure Free Rider (Fischbacher et al. 2001) |
| **Jennifer** | Bot | Reciprocal (Conditional Cooperator) | Reactive / Reciprocal (Fischbacher et al. 2001) |

### Monetary Endowment and the Personal Piggy Bank
In each of the 5 rounds, every player receives **10 personal Coins (🪙)**:
1. **🔒 In your Piggy Bank**: coins you choose NOT to donate remain safely in your personal account.
2. **⚡ In the DeLorean Fund**: coins donated by you and the other players are pooled together, multiplied by **1.6** by Doc (a 60% increase!), and divided equally among all 4 participants.
3. **💰 Round Earnings**: `Coins kept in piggy bank + your equal share of the DeLorean fund`.

---

## 2. Collective Team Goal (1.21 GW - 100 Coins)

The game blends a repeated public goods game with an intertemporal **Collective-Risk Social Dilemma (CRSD)**:

- **Round endowment**: `ENDOWMENT = 10` Coins per player (50 total across 5 rounds).
- **Multiplier**: `MULTIPLIER = 1.6`.
- **Number of players**: `N_PLAYERS = 4` (Marty + Doc + Biff + Jennifer).
- **Number of rounds**: `NUM_ROUNDS = 5`.
- **Collective target**: `CUMULATIVE_TARGET_MONEY = 100` total coins donated by the group across 5 rounds (equivalent to 1.21 GW). 100 coins represents a 50% overall cooperation rate (maximum capacity: `4 * 10 * 5 = 200`).

### Final Verdict (Round 5)
- If the team donates **at least 100 Coins (1.21 GW)**:
  **"88 MPH - Time travel successful!"** The DeLorean hits 88 MPH.
- If the team donates **fewer than 100 Coins**:
  **"Time Paradox!"** The car runs dry and does not start.

> **No loss possible**: in both cases the participant **always** keeps all the coins
> accumulated in their piggy bank (`final_game_payoff` = accumulated total). The
> success/failure verdict is narrative only and never wipes out any earnings.

---

## 3. Bot Personalities (Scientific Foundations)

The bot strategies simulate well-known empirical types from behavioral economics (*Fischbacher, Gächter & Fehr 2001*; *Milinski et al. 2008*):

### Doc Brown - *Generous / Altruistic Cooperator*
Always contributes **10 coins every round** to build a solid baseline for the mission (50 coins total).

### Biff Tannen - *Selfish / Pure Free Rider*
Always contributes **0 coins**, keeping everything in his piggy bank and taking advantage of others.

### Jennifer Parker - *Reciprocal / Conditional Cooperator*
- **Round 1**: contributes a friendly start of **5 coins**.
- **Rounds 2–5**: copies what the group did in the previous round (matching the average of Marty, Doc, and Biff).

### Marty - Human or Bot (Tit-for-Tat)
- **Human** (`marty_strategy = 'human'`): plays using the visual dashboard with real-time feedback (dual counters for *Piggy Bank* vs *DeLorean Fund*).
- **Bot** (`marty_strategy = 'tit_for_tat'`): contributes 5 coins on round 1, then the rounded average of the other 3 players.

---

## 4. User Experience for Students (Ages 10-18)

1. **Dual Real-Time Counter (`DecisionPage.html`)**:
   As the student moves the slider, they see:
   - 🟢 **In your Piggy Bank**: `10 - X` coins (bright green)
   - ⚡ **In the DeLorean Fund**: `X` coins (bright orange)
   This removes cognitive load and mental math, making the trade-off crystal clear.

2. **Step-by-Step Earnings Calculation (`ResultsPage.html`)**:
   Clear linear breakdown:
   `Coins kept in piggy bank + share of DeLorean fund = round earnings`, alongside the running total in the piggy bank.

3. **Battery Progress Bar**:
   Real-time progress towards 1.21 GW and the required 100 coins.

---

## 5. Running & Testing

### Development server
```bash
otree devserver
```
Open <http://localhost:8000> and pick `bttf_pgg_human` or `bttf_pgg_auto`.

### Automated tests (both IT and EN cases)
```bash
otree test bttf_pgg_auto
```
Runs both language paths across all 5 rounds and verifies calculations.
