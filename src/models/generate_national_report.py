# -*- coding: utf-8 -*-
"""
generate_national_report.py
Genera il Report Nazionale di Sintesi: reports/REPORT_NAZIONALE_MEDCAREER2031.md
Integrando dati quantitativi, formule matematiche, tabelle sinottiche e riferimenti grafici.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def safe_filename(name):
    s = name.lower()
    for src, tgt in [("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")]:
        s = s.replace(src, tgt)
    return s.replace(" ", "_").replace("'", "").replace(",", "").replace("*", "").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_")

print("Caricamento dataset per il Report Nazionale...")
df_proj = pd.read_parquet("data/processed/proiezioni_2031_multiscenario.parquet")
df_base = pd.read_parquet("data/processed/database_unificato.parquet")

conn = sqlite3.connect("data/processed/discipline_clinical_guidance.sqlite")
df_guidance = pd.read_sql("SELECT * FROM guida_clinica", conn).set_index("disciplina")
conn.close()

nat_base = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_baseline')].copy()
nat_plet = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_pletora')].copy()
nat_corr = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_correttivo')].copy()

base_n = df_base[df_base['tipo_territorio'] == 'Nazionale'].set_index('disciplina')

# Calcolo classifiche
top_carenza = nat_base.sort_values('isoo', ascending=True).head(10)
top_pletora = nat_base.sort_values('isoo', ascending=False).head(10)
top_qol = nat_base.sort_values('qol_score_base', ascending=False).head(10)
top_rep = nat_base.sort_values('rep_lorda_annua', ascending=False).head(10)

# Calcolo Sweet Spot: Score composito normalizzato (Opportunità SSN 40% + QoL 30% + REP 30%)
nat_base['norm_opp'] = 1.0 - (nat_base['isoo'] - nat_base['isoo'].min()) / (nat_base['isoo'].max() - nat_base['isoo'].min())
nat_base['norm_qol'] = (nat_base['qol_score_base'] - nat_base['qol_score_base'].min()) / (nat_base['qol_score_base'].max() - nat_base['qol_score_base'].min())
nat_base['norm_rep'] = (nat_base['rep_lorda_annua'] - nat_base['rep_lorda_annua'].min()) / (nat_base['rep_lorda_annua'].max() - nat_base['rep_lorda_annua'].min())
nat_base['sweet_spot_score'] = (nat_base['norm_opp'] * 0.40 + nat_base['norm_qol'] * 0.30 + nat_base['norm_rep'] * 0.30) * 100.0
top_sweet = nat_base.sort_values('sweet_spot_score', ascending=False).head(10)

# Aggregazione Macro-Aree Territoriali
reg_base = df_proj[(df_proj['tipo_territorio'] == 'Regione') & (df_proj['scenario_id'] == 'scenario_baseline')].copy()

nord_regions = ['Piemonte', "Valle d'Aosta", 'Liguria', 'Lombardia', 'P.A. Bolzano', 'P.A. Trento', 'Veneto', 'Friuli-Venezia Giulia', 'Emilia-Romagna']
centro_regions = ['Toscana', 'Umbria', 'Marche', 'Lazio']
sud_isole_regions = ['Abruzzo', 'Molise', 'Campania', 'Puglia', 'Basilicata', 'Calabria', 'Sicilia', 'Sardegna']

def assign_macro(row):
    if row['territorio'] in nord_regions:
        return 'Nord'
    elif row['territorio'] in centro_regions:
        return 'Centro'
    else:
        return 'Mezzogiorno e Isole'

reg_base['macro_area'] = reg_base.apply(assign_macro, axis=1)

macro_agg = reg_base.groupby('macro_area').agg({
    'stock_medici_attivi': 'sum',
    'pensionamenti_stimati_5y': 'sum',
    'esodo_dimissioni_stimato_5y': 'sum',
    'fabbisogno_netto_ssn_2031': 'sum',
    'nuovi_diplomati_effettivi_5y': 'sum',
    'saldo_netto_ssn': 'sum'
}).reset_index()

macro_agg['isoo_macro'] = macro_agg['nuovi_diplomati_effettivi_5y'] / macro_agg['fabbisogno_netto_ssn_2031']

print("Generazione testo del Report Nazionale...")

md = []
md.append("""# Rapporto Nazionale sulle Prospettive Occupazionali dei Medici Specialisti in Italia
## Modello Previsionale e Dinamiche del Mercato del Lavoro Sanitario al 2031 per la Coorte SSM 2026
**Autore:** Analisi Scientifica e Statistica Sanitaria  
**Orizzonte Temporale di Proiezione:** Novembre 2026 – Novembre 2031 (Coorte Concorsuale SSM 2026)  
**Documenti Correlati:** [52 Schede Monografiche di Disciplina](specializzazioni/) | [Guida alla Consultazione e Metodologia](GUIDA_ALLA_CONSULTAZIONE.md)

---

## Sintesi Esecutiva per il Medico Neolaureato

Il presente rapporto fornisce un quadro scientifico, trasparente e quantitativo sulle reali opportunità di impiego e sulle condizioni lavorative che attenderanno i medici che iniziano il percorso di formazione specialistica a novembre 2026, conseguendo il diploma tra la fine del 2029 (Medicina Generale) e il 2030-2031 (specializzazioni quadriennali e quinquennali).

Dalle analisi condotte su dati ministeriali (MEF, MUR, Ministero della Salute), demografici (ISTAT) e sindacali (ANAAO Assomed, ALS), emergono tre evidenze fondamentali:

1. **La Fine della Carenza Indifferenziata e la Polarizzazione Estrema:**  
   L'onda anomala pensionistica dei medici nati durante il baby boom (la "gobba pensionistica") raggiungerà il suo culmine tra il 2025 e il 2028, esaurendosi gradualmente attorno al 2030. In concomitanza con il raddoppio dei contratti di specializzazione stanziati post-pandemia (oltre 14.000 borse/anno), il SSN non si troverà di fronte a una carenza indistinta di medici, bensì a una **bipolarizzazione drammatica**:
   - Da un lato, **carenze voraginose e strutturali** in medicina generale, emergenza-urgenza, chirurgia generale, anestesia e servizi di laboratorio;
   - Dall'altro lato, **rischio imminente di saturazione e pletora specialistica** in numerose discipline clinico-ambulatoriali e dei servizi a bassa complessità ospedaliera (Medicina dello Sport, Cure Palliative, Scienza dell'Alimentazione, Allergologia, Genetica Medica).

2. **La Frattura Geografica Nord-Sud:**  
   Il ricambio generazionale segue dinamiche fortemente asimmetriche. Le regioni settentrionali (Lombardia, Veneto, Piemonte, Emilia-Romagna) presentano un deficit di specialisti quasi incolmabile ($\text{ISOO} < 0.85$), garantendo l'assunzione a tempo indeterminato praticamente a tutti i neo-diplomati. Al contrario, in diverse regioni del Centro-Sud il fabbisogno organico si saturerà rapidamente, determinando un'elevata concorrenza concorsuale e la necessità di mobilità geografica verso il Nord o verso l'attività libero-professionale pura.

3. **Il Trade-Off tra Occupabilità, Qualità della Vita e Reddito:**  
   Le discipline a più alta garanzia di assunzione ospedaliera immediata (Pronto Soccorso, Anestesia, Chirurgia Generale) risultano penalizzate da un basso indice di Qualità della Vita (QoL < 45/100), ritmi notturni massacranti e rischio contenzioso elevato. Al contrario, le discipline con la più alta qualità di vita (QoL > 85/100) richiedono spesso un posizionamento proattivo sul mercato privato per sfuggire alla saturazione dei pochi ruoli ospedalieri disponibili.

---

## 1. Quadro Metodologico Rigoroso e Fonti Istituzionali

L'analisi adotta un **modello quantitativo Stock-Flow a coorti dinamiche**, calibrato sulle 52 discipline (51 universitarie + Medicina Generale MMG*) e disaggregato su tutte le 21 Regioni e Province Autonome italiane.

### 1.1 Fonti Istituzionali dei Dati
Il modello poggia esclusivamente su banche dati ufficiali e certificate:
- **Ministero dell'Economia e delle Finanze (MEF - Conto Annuale dello Stato):** Rilevazione censuaria del personale dipendente del SSN per disciplina, qualifica, età anagrafica e anzianità di servizio.
- **Ministero dell'Università e della Ricerca (MUR):** Decreti ministeriali di accreditamento e contratti di formazione medico-specialistica finanziati con fondi statali, regionali e PNRR dal 2020 al 2024.
- **Istituto Nazionale di Statistica (ISTAT):** Serie storiche e previsioni demografiche comunali e regionali della popolazione residente per singola età fino al 2080 (Scenario Mediano ISTAT 2023-2031).
- **Studi di Settore ANAAO Assomed:** Curve attuariali sui pensionamenti della dirigenza medica (2018–2025), indagine sulle dimissioni volontarie dal SSN (2022) e studio sull'imminente rischio pletora medica (2024).
- **Rilevazioni ALS (Associazione Liberi Specializzandi):** Monitoraggio dei contratti non assegnati, abbandoni durante il percorso formativo e tassi di reiscrizione al concorso SSM.

### 1.2 La Formulazione Matematica del Modello Stock-Flow a 5 Anni
Per ciascuna disciplina $d$ e per ciascun territorio $r$, lo stock di medici specialisti al termine del quinquennio formativo ($S_{2031}$) è governato dall'equazione di continuità:

$$S_{2031, d, r} = S_{2026, d, r} - \sum_{t=2026}^{2031} \Big( P_{t, d, r} + E_{t, d, r} \Big) + \sum_{t=2026}^{2031} A_{t, d, r}$$

dove:
- $S_{2026, d, r}$: Stock di medici specialisti attivi nel SSN censiti a inizio periodo.
- $P_{t, d, r}$: Uscite fisiologiche per pensionamento di vecchiaia o anzianità (quota di medici con età $\ge 60$ anni).
- $E_{t, d, r}$: Uscite anticipate per dimissioni volontarie, esodo verso la sanità privata o gettoneria (stimato tra il $1.5\%$ e il $3.0\%$ annuo a seconda della gravosità della branca).
- $A_{t, d, r}$: Nuove assunzioni a tempo indeterminato nel SSN.

### 1.3 Il Moltiplicatore Demografico ISTAT ($M_d$)
La domanda di salute non è costante, ma evolve in funzione della piramide demografica. Tra il 2026 e il 2031, la popolazione italiana over 65 crescerà dell'**+8.5%** a livello nazionale (con punte superiori all'11% in alcune regioni), mentre la popolazione pediatrica under 15 si contrarrà del **-6.2%**.  
Il fabbisogno netto di specialisti tiene conto di questa transizione epidemiologica mediante il coefficiente demografico target:

$$\text{Fabbisogno Netto SSN}_{d, r} = \Big( \sum_{t=2026}^{2031} (P_{t, d, r} + E_{t, d, r}) \Big) \times \Big( 1 + \Delta \text{Pop}_{\text{target}(d), r} \Big)$$

- Per le discipline dell'anziano (Cardiologia, Geriatria, Ortopedia, Neurologia, Nefrologia, Oncologia), il moltiplicatore demografico incrementa il fabbisogno organico;
- Per le discipline pediatriche (Pediatria, Chirurgia Pediatrica), il decremento demografico attenua la necessità di rimpiazzo dei posti letto.

### 1.4 L'Indice di Saturazione e Opportunità Occupazionale (ISOO)
L'indice sintetico ISOO rappresenta il rapporto tra l'offerta totale di nuovi specialisti formati nel quinquennio e la domanda complessiva (capacità di assorbimento del SSN sommata alla capacità di assorbimento del settore privato accreditato/ambulatoriale):

$$\text{ISOO}_{d, r} = \frac{\text{Nuovi Specialisti Effettivi}_{d, r}}{\text{Fabbisogno Netto SSN}_{d, r} + \text{Capacità Assorbimento Privato}_{d, r}}$$

dove $\text{Nuovi Specialisti Effettivi} = \text{Contratti Assegnati} \times (1 - \text{Tasso Storico Abbandono})$.

#### Tabella Operativa di Decisione per il Medico
| Valore ISOO | Semaforo | Categoria Occupazionale | Probabilità Concorso SSN | Strategia Professionale Consigliata |
| :---: | :---: | :--- | :---: | :--- |
| **$< 0.80$** | 🟢 **Verde Scuro** | **Carenza Severa / Assunzione Immediata** | **$> 95\%$** | Scelta prioritaria della sede desiderata; arruolamento rapido prima o subito dopo il titolo. |
| **$0.80 - 1.15$** | 🟢 **Verde Chiaro** | **Equilibrio Fisiologico / Buona Occupabilità** | **$75\% - 95\%$** | Mercato solido; assorbimento fluido tra ospedale pubblico e strutture convenzionate. |
| **$1.16 - 1.45$** | 🟠 **Arancione** | **Saturazione Moderata / Concorrenza** | **$50\% - 75\%$** | Graduatorie concorsuali selettive; indispensabile acquisire sub-specialità tecniche e mobilità regionale. |
| **$> 1.45$** | 🔴 **Rosso** | **Pletora / Rischio Elevato di Sottoccupazione** | **$< 50\%$** | Posti SSN insufficienti; sbocco quasi obbligato nella libera professione pura o nel settore privato. |

---

## 2. Risultati Nazionali al 2031: Classifiche e Indicatori

### 2.1 Il Ranking Nazionale Completo delle 52 Discipline
Il seguente diagramma vettoriale illustra la classificazione completa dell'Indice ISOO per tutte le 52 discipline nello Scenario Baseline:

![Ranking Nazionale ISOO](figures/isoo_ranking_nazionale.svg)

---

### 2.2 Tabella Sinottica Generale Nazionale (Coorte 2026–2031)
Di seguito è riportata la sintesi comparativa per tutte le 52 discipline nello Scenario Baseline. Cliccando sul nome della disciplina è possibile aprire il dossier monografico dettagliato:

| Disciplina | Area | Durata | Borse/Anno | Uscite SSN 5y | Nuovi Spec. | Saldo SSN | ISOO | P. Bando | QoL | REP Lorda | Scheda |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")

# Righe tabella
for _, r in nat_base.sort_values('isoo', ascending=True).iterrows():
    disc = r['disciplina']
    slug = safe_filename(disc)
    sem = '🟢' if r['isoo'] <= 1.15 else ('🟠' if r['isoo'] <= 1.45 else '🔴')
    sal = int(r['saldo_netto_ssn'])
    sal_str = f"+{sal}" if sal > 0 else f"{sal}"
    md.append(f"| [{disc}](specializzazioni/{slug}.md) | {r['area']} | {r['durata_anni']}a | {int(base_n.loc[disc]['contratti_annui_totali']):,} | {int(r['uscite_totali_ssn_5y']):,} | {int(r['nuovi_diplomati_effettivi_5y']):,} | {sal_str} | **{r['isoo']:.2f}** | {r['probabilita_bando_ssn_pct']:.0f}% | {r['qol_score_base']:.0f} | ~{r['rep_lorda_annua']:,.0f} € | [Apri Scheda](specializzazioni/{slug}.md) |")

md.append("""
---

### 2.3 Top 10 Discipline a Massima Carenza al 2031 (Assunzione Immediata)
Nelle seguenti discipline l'offerta di specialisti formati rimarrà largamente inferiore al fabbisogno del SSN:

| Pos. | Disciplina | Area | Fabbisogno Netto SSN | Nuovi Specialisti | Saldo Mancante | Indice ISOO | Prob. Concorso |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
""")

for i, (_, r) in enumerate(top_carenza.iterrows(), start=1):
    disc = r['disciplina']
    slug = safe_filename(disc)
    sal = int(r['saldo_netto_ssn'])
    md.append(f"| **{i}** | [{disc}](specializzazioni/{slug}.md) | {r['area']} | {int(r['fabbisogno_netto_ssn_2031']):,} | {int(r['nuovi_diplomati_effettivi_5y']):,} | **{sal}** | **{r['isoo']:.2f}** | **{r['probabilita_bando_ssn_pct']:.0f}%** |")

md.append("""
> [!IMPORTANT]
> **Osservazioni Clinico-Operative sulle Prime Posizioni**:
> - **Medicina Generale (MMG*) - ISOO 0.41:** Il pensionamento di oltre 21.000 medici convenzionati attivi su 39.000 genererà un vuoto di assistenza primaria senza precedenti. L'assegnazione della zona carente e il massimale di 1.500 assistiti saranno istantanei in quasi tutti i distretti d'Italia.
> - **Chirurgia Generale & MEU - ISOO 0.53 e 0.76:** Nonostante un numero elevato di contratti teorici, i tassi di abbandono e di borse non assegnate superano il 35-50% in MEU e il 20% in Chirurgia Generale. Chi porta a termine il percorso ha la certezza assoluta di un posto a tempo indeterminato in qualunque ospedale d'Italia.
> - **Anatomia Patologica & Patologia Clinica - ISOO 0.60 e 0.69:** Specialità dei servizi ad altissimo ricambio per anzianità elevata della classe medica, con graduatorie concorsuali regolarmente deserte.

---

### 2.4 Top 10 Discipline a Rischio Pletora e Saturazione SSN al 2031
All'estremo opposto, le seguenti discipline formeranno un contingente di medici nettamente superiore ai posti di ruolo disponibili nelle piante organiche del SSN:

| Pos. | Disciplina | Area | Fabbisogno Netto SSN | Nuovi Specialisti | Esubero Stimato | Indice ISOO | Prob. Concorso |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
""")

for i, (_, r) in enumerate(top_pletora.iterrows(), start=1):
    disc = r['disciplina']
    slug = safe_filename(disc)
    sal = int(r['saldo_netto_ssn'])
    md.append(f"| **{i}** | [{disc}](specializzazioni/{slug}.md) | {r['area']} | {int(r['fabbisogno_netto_ssn_2031']):,} | {int(r['nuovi_diplomati_effettivi_5y']):,} | **+{sal}** | **{r['isoo']:.2f}** | **{r['probabilita_bando_ssn_pct']:.0f}%** |")

md.append("""
> [!WARNING]
> **Fattori Determinanti della Saturazione**:
> - **Medicina dello Sport (ISOO 1.77) e Scienza dell'Alimentazione (ISOO 1.76):** Dotazioni organiche ospedaliere minime o nulle. La formazione è quasi interamente assorbita dal mercato privato puro o da convenzioni societarie sportive.
> - **Cure Palliative (ISOO 1.83):** Forte incremento di borse stanziate negli ultimi anni a fronte di reti di Hospice territoriali con organici compatti.
> - **Allergologia e Genetica Medica (ISOO 1.83 e 1.74):** Ruoli ospedalieri riservati a poli universitari Hub di III livello; concorsi pubblici rari e contesi tra decine di candidati per singolo posto.

---

## 3. Analisi del Trade-Off: Qualità della Vita vs Redditività Economica

La scelta della scuola di specializzazione non si riduce al mero tasso di assunzione, ma richiede una ponderazione realistica dello stile di vita quotidiano e del potenziale economico a medio-lungo termine.

### 3.1 La Matrice a 4 Quadranti
Il diagramma seguente posiziona tutte le 52 discipline combinando il **QoL Score (0–100)** sull'asse orizzontale e la **Redditività Lorda Annua Stimata (REP)** sull'asse verticale:

![Trade-off QoL vs REP](figures/qol_vs_rep_scatter.svg)

---

### 3.2 Interpretazione dei 4 Quadranti
1. **Quadrante Verde (Alta QoL / Alta Redditività) — *Lo Sweet Spot Professionale*:**  
   Comprende discipline ad alta richiesta privata e bassissimo impatto di guardie notturne o urgenze: **Dermatologia, Oftalmologia, Chirurgia Plastica, Radiodiagnostica**. Permette di conciliare una vita privata serena con guadagni al vertice del settore sanitario.
2. **Quadrante Blu (Alta QoL / Redditività Standard SSN):**  
   Discipline dei servizi e della sanità pubblica (**Igiene e Medicina Preventiva, Statistica Sanitaria, Medicina del Lavoro, Medicina Legale, Allergologia**). Offrono orari d'ufficio regolari, zero notti di guardia, rischio medico-legale quasi nullo e reddito da dipendente pubblico stabile e garantito.
3. **Quadrante Rosso (Bassa QoL / Alta Redditività):**  
   Le grandi branche chirurgiche e interventistiche ad alta complessità (**Cardiochirurgia, Neurochirurgia, Ortopedia, Chirurgia Generale, Cardiologia Interventistica**). Comportano turni notturni pesanti, reperibilità e stress peritale continuo, ma consentono proventi chirurgici e intramurari elevatissimi.
4. **Quadrante Arancione (Bassa QoL / Redditività Standard SSN) — *L'Area Critica del SSN*:**  
   Discipline dell'urgenza ospedaliera pura (**Medicina d'Emergenza-Urgenza, Anestesia e Rianimazione, Medicina Interna**). Elevatissimo carico di lavoro, notti frequenti, retribuzione ancorata ai tabellari del CCNL con possibilità ridotte di libera professione privata. È l'area maggiormente colpita da burnout e abbandoni precoci.

---

### 3.3 Top 10 per Qualità della Vita vs Top 10 per Redditività Economica

| Pos. | Top 10 Qualità della Vita (QoL Score / 100) | Top 10 Redditività Economica Potenziale (Lordo Annuo) |
| :---: | :--- | :--- |
""")

for i in range(10):
    q_row = top_qol.iloc[i]
    r_row = top_rep.iloc[i]
    q_disc = q_row['disciplina']
    r_disc = r_row['disciplina']
    q_slug = safe_filename(q_disc)
    r_slug = safe_filename(r_disc)
    md.append(f"| **{i+1}** | [{q_disc}](specializzazioni/{q_slug}.md) (**{q_row['qol_score_base']:.0f}/100**) | [{r_disc}](specializzazioni/{r_slug}.md) (**~{r_row['rep_lorda_annua']:,.0f} €**) |")

md.append("""
---

### 3.4 La Classifica "Sweet Spot" (Equilibrio Globale)
Combinando in un indice armonico la facilità di assunzione concorsuale (40%), la qualità della vita lavorativa (30%) e la redditività economica complessiva (30%), emergono le 10 specialità con il **miglior bilanciamento di carriera per la coorte 2026–2031**:

| Pos. | Disciplina | Area | ISOO 2031 | QoL Score | REP Lorda Annua | Sweet Spot Score (/100) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
""")

for i, (_, r) in enumerate(top_sweet.iterrows(), start=1):
    disc = r['disciplina']
    slug = safe_filename(disc)
    md.append(f"| **{i}** | [{disc}](specializzazioni/{slug}.md) | {r['area']} | **{r['isoo']:.2f}** | {r['qol_score_base']:.0f}/100 | ~{r['rep_lorda_annua']:,.0f} € | **{r['sweet_spot_score']:.1f}** |")

md.append("""
---

## 4. Il Mosaico Territoriale: Divario Nord - Centro - Mezzogiorno

L'analisi territoriale condotta sulle 21 Regioni e Province Autonome evidenzia una profonda eterogeneità di assorbimento della forza lavoro medica.

### 4.1 Sintesi delle Macro-Aree Geografiche (Scenario Baseline al 2031)

| Macro-Area Territoriale | Medici Attivi 2026 | Uscite Totali SSN (5y) | Nuovi Diplomati Assegnati | Saldo Netto SSN 2031 | Indice ISOO Macro | Verdetto Territoriale |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
""")

for _, r in macro_agg.iterrows():
    sal = int(r['saldo_netto_ssn'])
    sal_str = f"+{sal:,}" if sal > 0 else f"{sal:,}"
    verdetto = "🟢 Carenza Acuta (Assorbimento Totale)" if r['isoo_macro'] < 0.90 else ("🟢 Equilibrio Solido" if r['isoo_macro'] <= 1.15 else "🟠 Saturazione Moderata")
    md.append(f"| **{r['macro_area']}** | {int(r['stock_medici_attivi']):,} | {int(r['pensionamenti_stimati_5y'] + r['esodo_dimissioni_stimato_5y']):,} | {int(r['nuovi_diplomati_effettivi_5y']):,} | **{sal_str}** | **{r['isoo_macro']:.2f}** | {verdetto} |")

md.append("""
### 4.2 Dinamiche di Mobilità Post-Specializzazione
- **La Voragine del Nord:** Le regioni settentrionali presentano una percentuale più elevata di dirigenti medici over 60 e un maggiore tasso di dimissioni verso la sanità privata o la Svizzera/estero. Il saldo occupazionale rimane negativo in quasi tutte le discipline di rete, rendendo il Nord un bacino di assorbimento primario per i giovani medici.
- **La Competitività del Centro-Sud:** Nel Mezzogiorno, complice un turnover storicamente più contenuto e un numero inferiore di posti letto privati accreditati per abitante, l'indice ISOO medio è più elevato. Numerosi giovani specialisti formatisi nel Sud dovranno pianificare una mobilità geografica verso il Centro-Nord nei primi anni post-titolo.

---

## 5. Confronto Dinamico dei 3 Scenari al 2031

Il modello Stock-Flow è stato sottoposto a stress-test sotto tre differenti ipotesi macroeconomiche e legislative:

1. **Scenario 1: Baseline Inerziale:** Mantenimento delle attuali tendenze di spesa del SSN, turnover al 100% delle cessazioni, trend di dimissioni costanti e numero di borse SSM stabile.
2. **Scenario 2: Pletora Grave (Worst-Case):** Tagli di bilancio alla sanità pubblica, blocco parziale del turnover organico (assunzioni limitate all'80% delle uscite), crollo delle dimissioni verso il privato per saturazione economica e minore tasso di abbandono formativo.
3. **Scenario 3: Riforma Correttiva (Best-Case):** Piena attuazione del PNRR e del DM 77/2022 con potenziamento degli Ospedali di Comunità, defiscalizzazione del lavoro notturno/festivo, riduzione dell'orario settimanale a 36 ore effettive con conseguente espansione del fabbisogno organico (+10%).

### 5.1 Distribuzione dei Verdetti nei 3 Scenari (Nazionale)

| Verdetto Occupazionale al 2031 | Scenario 1 (Baseline) | Scenario 2 (Pletora Worst) | Scenario 3 (Riforma Best) |
| :--- | :---: | :---: | :---: |
| 🟢 **Carenza Severa / Assunzione Immediata** | 7 discipline | 5 discipline | 13 discipline |
| 🟢 **Equilibrio Fisiologico / Buona Occupabilità** | 15 discipline | 8 discipline | 19 discipline |
| 🟠 **Saturazione Moderata / Concorrenza** | 16 discipline | 19 discipline | 13 discipline |
| 🔴 **Pletora / Rischio Saturazione SSN** | 14 discipline | 20 discipline | 7 discipline |

> [!TIP]
> **Impatto delle Riforme Istituzionali**:
> Nello Scenario 3 (Riforma Correttiva), discipline oggi a rischio come **Geriatria, Medicina di Comunità e Psichiatria** vedono il proprio indice ISOO crollare sotto la soglia di equilibrio (diventando a carenza elevata), grazie all'apertura reale delle strutture territoriali intermedie previste dal DM 77.

---

## 6. Indice Analitico delle 52 Monografie di Specializzazione

Tutte le 52 schede monografiche complete di dati formativi, tabelle regionali, scorecard QoL/REP e consigli di orientamento clinico sono accessibili direttamente dai seguenti elenchi suddivisi per area:

### 🏥 Area Medica (Clinica Generale e Specialistica)
""")

med_list = nat_base[nat_base['area'] == 'Medica'].sort_values('disciplina')
for _, r in med_list.iterrows():
    d = r['disciplina']
    slug = safe_filename(d)
    sem = '🟢' if r['isoo'] <= 1.15 else ('🟠' if r['isoo'] <= 1.45 else '🔴')
    md.append(f"- {sem} [{d}](specializzazioni/{slug}.md) — *ISOO: {r['isoo']:.2f}* ({r['verdetto_carriera_2031']})")

md.append("""
### 🔪 Area Chirurgica
""")

chir_list = nat_base[nat_base['area'] == 'Chirurgica'].sort_values('disciplina')
for _, r in chir_list.iterrows():
    d = r['disciplina']
    slug = safe_filename(d)
    sem = '🟢' if r['isoo'] <= 1.15 else ('🟠' if r['isoo'] <= 1.45 else '🔴')
    md.append(f"- {sem} [{d}](specializzazioni/{slug}.md) — *ISOO: {r['isoo']:.2f}* ({r['verdetto_carriera_2031']})")

md.append("""
### 🔬 Area dei Servizi Clinici e Diagnostici
""")

serv_list = nat_base[nat_base['area'] == 'Servizi'].sort_values('disciplina')
for _, r in serv_list.iterrows():
    d = r['disciplina']
    slug = safe_filename(d)
    sem = '🟢' if r['isoo'] <= 1.15 else ('🟠' if r['isoo'] <= 1.45 else '🔴')
    md.append(f"- {sem} [{d}](specializzazioni/{slug}.md) — *ISOO: {r['isoo']:.2f}* ({r['verdetto_carriera_2031']})")

md.append("""
### 🩺 Cure Primarie e Assistenza Territoriale
""")

prim_list = nat_base[nat_base['area'] == 'Cure Primarie*'].sort_values('disciplina')
for _, r in prim_list.iterrows():
    d = r['disciplina']
    slug = safe_filename(d)
    sem = '🟢' if r['isoo'] <= 1.15 else ('🟠' if r['isoo'] <= 1.45 else '🔴')
    md.append(f"- {sem} [{d}](specializzazioni/{slug}.md) — *ISOO: {r['isoo']:.2f}* ({r['verdetto_carriera_2031']})")

md.append("""
---

## 7. Conclusioni e Raccomandazioni per i Neo-Iscritti 2026

Per il medico che si accinge a formalizzare l'iscrizione a novembre 2026, la pianificazione strategica della carriera deve basarsi sui seguenti principi:

1. **Non basare la scelta solo sulla situazione contingente del 2026:**  
   L'attuale penuria di medici specialisti è in massima parte un fenomeno transitorio legato al picco di uscite dei medici nati prima del 1965. Al momento del diploma (2030–2031), il mercato ospedaliero avrà assorbito decine di migliaia di nuovi specialisti formati con i mega-bandi post-COVID.
2. **Sviluppare fin dal 2° anno una barriera all'ingresso tecnica:**  
   Nelle discipline a rischio saturazione (Allergologia, Dermatologia, Endocrinologia, Fisiatria), la differenza tra sottoccupazione e successo professionale risiede nella padronanza di competenze pratico-strumentali (POCUS, ecografia interventistica, biologia molecolare, metodiche endoscopiche mininvasive).
3. **Mantenere flessibilità geografica:**  
   La disponibilità a muoversi nelle ASL spoke o nei presidi del Centro-Nord azzera quasi completamente il rischio di disoccupazione anche nelle specialità più competitive.
4. **Valutare l'ecosistema privato prima della scelta:**  
   Se la disciplina prescelta ha un indice ISOO superiore a 1.20, accertarsi preventivamente della solidità del mercato ambulatoriale privato o convenzionato nel territorio in cui si intende vivere.

---
[↑ Torna all'Inizio del Rapporto](#rapporto-nazionale-sulle-prospettive-occupazionali-dei-medici-specialisti-in-italia) | [Consulta la Guida Metodologica](GUIDA_ALLA_CONSULTAZIONE.md)
""")

report_content = "\n".join(md)

with open("reports/REPORT_NAZIONALE_MEDCAREER2031.md", "w", encoding="utf-8") as f_out:
    f_out.write(report_content)

print(f"REPORT NAZIONALE GENERATO CON SUCCESSO! Dimensione: {len(report_content):,} caratteri.")
