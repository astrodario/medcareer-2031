# -*- coding: utf-8 -*-
"""
MedCareer 2031 — Tool Interattivo di Orientamento per Specializzandi Medici in Italia
Autore: Analisi Scientifica e Statistica Sanitaria
Esecuzione: streamlit run src/app/streamlit_app.py
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="MedCareer 2031 | Orientamento Specializzazioni",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funzione per pulizia slug
def safe_filename(name):
    s = name.lower()
    for src, tgt in [("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")]:
        s = s.replace(src, tgt)
    return s.replace(" ", "_").replace("'", "").replace(",", "").replace("*", "").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_")

# Caricamento dati con cache
@st.cache_data
def load_data():
    df_proj = pd.read_parquet("data/processed/proiezioni_2031_multiscenario.parquet")
    df_base = pd.read_parquet("data/processed/database_unificato.parquet")
    df_disc = pd.read_csv("data/processed/discipline_caratteristiche.csv")
    return df_proj, df_base, df_disc

df_proj, df_base, df_disc = load_data()

# Sidebar
st.sidebar.title("🩺 MedCareer 2031")
st.sidebar.caption("Modello Previsionale e Decision Support System per Neolaureati in Medicina (Coorte SSM 2026–2031)")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Seleziona Modulo di Analisi:",
    [
        "📊 Dashboard Nazionale & Ranking",
        "🗺️ Analisi Territoriale (21 Regioni)",
        "⚖️ Calcolatore QoL Personalizzato",
        "🥊 Confronto Testa a Testa",
        "📄 Esploratore Schede Monografiche"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Dati Ufficiali Integrati:**\n"
    "- MEF (Conto Annuale SSN)\n"
    "- MUR (Bandi SSM e atenei)\n"
    "- ISTAT (Demografia 2026–2031)\n"
    "- ANAAO Assomed & ALS"
)

# ==============================================================================
# MODULO 1: DASHBOARD NAZIONALE
# ==============================================================================
if menu == "📊 Dashboard Nazionale & Ranking":
    st.title("📊 Dashboard Nazionale: Proiezioni Occupazionali al 2031")
    st.markdown(
        "Esplora il quadro generale delle **52 discipline mediche** (51 universitarie + Medicina Generale MMG*) "
        "sotto 3 differenti scenari normativi ed economici."
    )

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        scenario_sel = st.selectbox(
            "Seleziona Scenario Macroeconomico:",
            [
                "Scenario 1: Baseline (Inerziale)",
                "Scenario 2: Pletora Grave (Worst Case)",
                "Scenario 3: Riforma Correttiva (Best Case)"
            ]
        )
    with col2:
        sc_map = {
            "Scenario 1: Baseline (Inerziale)": "scenario_baseline",
            "Scenario 2: Pletora Grave (Worst Case)": "scenario_pletora",
            "Scenario 3: Riforma Correttiva (Best Case)": "scenario_correttivo"
        }
        curr_sc = sc_map[scenario_sel]
        area_filter = st.multiselect(
            "Filtra per Area Disciplinare:",
            ["Medica", "Chirurgica", "Servizi", "Cure Primarie*"],
            default=["Medica", "Chirurgica", "Servizi", "Cure Primarie*"]
        )
    with col3:
        sort_by = st.selectbox(
            "Ordina Tabella per:",
            ["Indice ISOO (Carenza -> Pletora)", "Saldo Mancante SSN", "Qualità della Vita (QoL)", "Redditività Stimata (REP)"]
        )

    # Filtraggio dati nazionali
    sub_nat = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == curr_sc)].copy()
    if area_filter:
        sub_nat = sub_nat[sub_nat['area'].isin(area_filter)]

    # Ordinamento
    if sort_by == "Indice ISOO (Carenza -> Pletora)":
        sub_nat = sub_nat.sort_values('isoo', ascending=True)
    elif sort_by == "Saldo Mancante SSN":
        sub_nat = sub_nat.sort_values('saldo_netto_ssn', ascending=True)
    elif sort_by == "Qualità della Vita (QoL)":
        sub_nat = sub_nat.sort_values('qol_score_base', ascending=False)
    else:
        sub_nat = sub_nat.sort_values('rep_lorda_annua', ascending=False)

    # KPI Top Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    n_carenza = len(sub_nat[sub_nat['isoo'] < 0.80])
    n_equilibrio = len(sub_nat[(sub_nat['isoo'] >= 0.80) & (sub_nat['isoo'] <= 1.15)])
    n_saturazione = len(sub_nat[(sub_nat['isoo'] > 1.15) & (sub_nat['isoo'] <= 1.45)])
    n_pletora = len(sub_nat[sub_nat['isoo'] > 1.45])

    kpi1.metric("🟢 Carenza Severa (ISOO < 0.80)", f"{n_carenza} discipline")
    kpi2.metric("🟢 Equilibrio (0.80 - 1.15)", f"{n_equilibrio} discipline")
    kpi3.metric("🟠 Saturazione (1.16 - 1.45)", f"{n_saturazione} discipline")
    kpi4.metric("🔴 Pletora Grave (ISOO > 1.45)", f"{n_pletora} discipline")

    st.markdown("---")

    # Tabella principale
    display_df = sub_nat[[
        'disciplina', 'area', 'durata_anni', 'fabbisogno_netto_ssn_2031',
        'nuovi_diplomati_effettivi_5y', 'saldo_netto_ssn', 'isoo',
        'probabilita_bando_ssn_pct', 'qol_score_base', 'rep_lorda_annua', 'verdetto_carriera_2031'
    ]].copy()

    display_df.columns = [
        'Disciplina', 'Area', 'Durata', 'Fabbisogno SSN',
        'Nuovi Specialisti', 'Saldo Netto SSN', 'Indice ISOO',
        'Prob. Concorso %', 'QoL Score', 'REP Lorda €', 'Verdetto Occupazionale'
    ]

    st.dataframe(
        display_df.style.format({
            'Fabbisogno SSN': '{:,.0f}',
            'Nuovi Specialisti': '{:,.0f}',
            'Saldo Netto SSN': '{:+,.0f}',
            'Indice ISOO': '{:.2f}',
            'Prob. Concorso %': '{:.0f}%',
            'QoL Score': '{:.0f}',
            'REP Lorda €': '{:,.0f} €'
        }),
        use_container_width=True,
        height=600
    )

    # Download CSV
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Tabella in Formato CSV",
        data=csv_data,
        file_name=f"medcareer2031_{curr_sc}.csv",
        mime="text/csv"
    )

# ==============================================================================
# MODULO 2: ANALISI TERRITORIALE (21 REGIONI)
# ==============================================================================
elif menu == "🗺️ Analisi Territoriale (21 Regioni)":
    st.title("🗺️ Analisi Territoriale Regionale (2026–2031)")
    st.markdown("Visualizza la proiezione per ciascuna delle **21 Regioni e Province Autonome** italiane.")

    regioni_disponibili = sorted(df_proj[df_proj['tipo_territorio'] == 'Regione']['territorio'].unique())
    col_reg1, col_reg2 = st.columns([2, 3])

    with col_reg1:
        reg_sel = st.selectbox("Seleziona Territorio:", regioni_disponibili, index=regioni_disponibili.index("Lombardia") if "Lombardia" in regioni_disponibili else 0)
    with col_reg2:
        area_reg = st.multiselect("Filtra per Area:", ["Medica", "Chirurgica", "Servizi", "Cure Primarie*"], default=["Medica", "Chirurgica", "Servizi", "Cure Primarie*"])

    sub_reg = df_proj[(df_proj['territorio'] == reg_sel) & (df_proj['scenario_id'] == 'scenario_baseline')].copy()
    if area_reg:
        sub_reg = sub_reg[sub_reg['area'].isin(area_reg)]

    # Sommario Regione
    stk_tot = sub_reg['stock_medici_attivi'].sum()
    usc_tot = sub_reg['uscite_totali_ssn_5y'].sum()
    ing_tot = sub_reg['nuovi_diplomati_effettivi_5y'].sum()
    sal_tot = sub_reg['saldo_netto_ssn'].sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Medici Attivi Censiti 2026", f"{stk_tot:,.0f}")
    m2.metric("Uscite Stimate al 2031", f"{usc_tot:,.0f}")
    m3.metric("Nuovi Specialisti Formati", f"{ing_tot:,.0f}")
    sal_label = f"+{sal_tot:,.0f}" if sal_tot > 0 else f"{sal_tot:,.0f}"
    m4.metric("Saldo Netto Regionale SSN", sal_label)

    st.markdown(f"### Dettaglio delle Specializzazioni in **{reg_sel}** (Scenario Baseline)")

    reg_table = sub_reg[[
        'disciplina', 'area', 'stock_medici_attivi', 'uscite_totali_ssn_5y',
        'nuovi_diplomati_effettivi_5y', 'saldo_netto_ssn', 'isoo', 'verdetto_carriera_2031'
    ]].sort_values('isoo', ascending=True)

    reg_table.columns = ['Disciplina', 'Area', 'Stock 2026', 'Uscite 5y', 'Nuovi Ingressi', 'Saldo Netto', 'ISOO Regionale', 'Verdetto']

    st.dataframe(
        reg_table.style.format({
            'Stock 2026': '{:,.0f}',
            'Uscite 5y': '{:,.0f}',
            'Nuovi Ingressi': '{:,.0f}',
            'Saldo Netto': '{:+,.0f}',
            'ISOO Regionale': '{:.2f}'
        }),
        use_container_width=True,
        height=550
    )

# ==============================================================================
# MODULO 3: CALCOLATORE QoL PERSONALIZZATO
# ==============================================================================
elif menu == "⚖️ Calcolatore QoL Personalizzato":
    st.title("⚖️ Calcolatore Qualità della Vita Personalizzato")
    st.markdown(
        "Ogni persona ha priorità diverse. Usa gli slider sottostanti per definire **quanto conta per te** "
        "ciascun fattore dello stile di vita. Il modello ricalcolerà la tua graduatoria ideale su misura!"
    )

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        w_notti = st.slider("Quanto ti pesano le Notti di Guardia?", 0, 100, 30, help="0 = non mi importa lavorare di notte, 100 = non voglio assolutamente fare notti")
        w_rep = st.slider("Quanto ti pesano le Reperibilità Notturne/Festive?", 0, 100, 20, help="Reperibilità al telefono e urgenze da casa")
        w_ore = st.slider("Importanza di avere Orari Fissi e Regolari?", 0, 100, 20, help="Evitare straordinari e turni oltre le 38h")
    with col_w2:
        w_legale = st.slider("Quanto temi il Rischio Medico-Legale / Denunce?", 0, 100, 15, help="Serenità rispetto a contenziosi penali e civili")
        w_burnout = st.slider("Importanza di un Basso Stress Mentale / Burnout?", 0, 100, 15, help="Discipline ad alto contatto emotivo o emergenza")

    tot_weight = w_notti + w_rep + w_ore + w_legale + w_burnout
    if tot_weight == 0:
        tot_weight = 1

    # Ricalcolo score personalizzato
    custom_df = df_disc.copy()
    
    # Normalizzazione singoli indicatori tra 0 e 100
    norm_notti = 100.0 - (custom_df['notti_mese'] / 6.0 * 100.0).clip(0, 100)
    norm_rep = 100.0 - (custom_df['rep_mese'] / 8.0 * 100.0).clip(0, 100)
    norm_ore = 100.0 - ((custom_df['ore_sett'] - 36) / 20.0 * 100.0).clip(0, 100)
    norm_legale = 100.0 - ((custom_df['rischio_legale'] - 1) / 4.0 * 100.0)
    norm_burnout = 100.0 - custom_df['burnout']

    custom_df['my_qol_score'] = (
        norm_notti * (w_notti / tot_weight) +
        norm_rep * (w_rep / tot_weight) +
        norm_ore * (w_ore / tot_weight) +
        norm_legale * (w_legale / tot_weight) +
        norm_burnout * (w_burnout / tot_weight)
    )

    st.markdown("---")
    st.subheader("🏆 La Tua Top 15 Specializzazioni su Misura per Stile di Vita")

    top_custom = custom_df.sort_values('my_qol_score', ascending=False).head(15)
    st.dataframe(
        top_custom[['nome', 'area', 'my_qol_score', 'notti_mese', 'rep_mese', 'ore_sett', 'rischio_legale', 'burnout', 'rep_lorda_annua_stimata']].rename(columns={
            'nome': 'Specializzazione',
            'area': 'Area',
            'my_qol_score': 'Tuo QoL Score Personale',
            'notti_mese': 'Notti/Mese',
            'rep_mese': 'Reperib./Mese',
            'ore_sett': 'Ore/Sett.',
            'rischio_legale': 'Classe Rischio (1-5)',
            'burnout': 'Indice Burnout',
            'rep_lorda_annua_stimata': 'Reddito Lordo Stimato'
        }).style.format({
            'Tuo QoL Score Personale': '{:.1f} / 100',
            'Reddito Lordo Stimato': '{:,.0f} €'
        }),
        use_container_width=True
    )

# ==============================================================================
# MODULO 4: CONFRONTO TESTA A TESTA
# ==============================================================================
elif menu == "🥊 Confronto Testa a Testa":
    st.title("🥊 Confronto Diretto Testa a Testa")
    st.markdown("Sei indeciso tra 2 o 3 scuole? Selezionale qui per confrontare all'istante indicatori, carichi e prospettive.")

    all_specs = sorted(df_proj['disciplina'].unique())
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        s1 = st.selectbox("Scelta A:", all_specs, index=all_specs.index("Malattie dell'apparato cardiovascolare") if "Malattie dell'apparato cardiovascolare" in all_specs else 0)
    with col_c2:
        s2 = st.selectbox("Scelta B:", all_specs, index=all_specs.index("Radiodiagnostica") if "Radiodiagnostica" in all_specs else 1)
    with col_c3:
        s3 = st.selectbox("Scelta C (Opzionale):", ["Nessuna"] + all_specs, index=0)

    selected_compare = [s1, s2]
    if s3 != "Nessuna" and s3 not in selected_compare:
        selected_compare.append(s3)

    comp_df = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_baseline') & (df_proj['disciplina'].isin(selected_compare))].copy()
    comp_base = df_base[(df_base['tipo_territorio'] == 'Nazionale') & (df_base['disciplina'].isin(selected_compare))].set_index('disciplina')

    cols = st.columns(len(selected_compare))
    for idx, d_name in enumerate(selected_compare):
        row = comp_df[comp_df['disciplina'] == d_name].iloc[0]
        b_row = comp_base.loc[d_name]
        slug = safe_filename(d_name)

        with cols[idx]:
            st.subheader(d_name)
            st.caption(f"Area {row['area']} | Durata: {row['durata_anni']} anni")
            
            # Radar chart
            radar_path = f"reports/figures/radar/{slug}.svg"
            if os.path.exists(radar_path):
                with open(radar_path, "r", encoding="utf-8") as f_svg:
                    svg_code = f_svg.read()
                st.image(radar_path, use_column_width=True)

            st.markdown(f"""
            - **Indice ISOO 2031**: `{row['isoo']:.2f}` ({row['verdetto_carriera_2031']})
            - **Probabilità Concorso SSN**: `{row['probabilita_bando_ssn_pct']:.0f}%`
            - **Qualità della Vita (QoL)**: `{row['qol_score_base']:.0f} / 100`
            - **Notti al Mese**: `{b_row['notti_mese']} turni`
            - **Reperibilità al Mese**: `{b_row['reperibilita_mese']} turni`
            - **Ore Settimanali Medie**: `{b_row['ore_settimanali']} h`
            - **Rischio Medico-Legale**: `Classe {b_row['classe_rischio_legale']} / 5`
            - **Reddito Lordo Stimato**: `~{row['rep_lorda_annua']:,.0f} €`
            - **Potenziale Privato**: `~{row['rep_privato_stimato']:,.0f} €`
            """)

# ==============================================================================
# MODULO 5: ESPLORATORE SCHEDE MONOGRAFICHE
# ==============================================================================
elif menu == "📄 Esploratore Schede Monografiche":
    st.title("📄 Esploratore Schede Monografiche")
    st.markdown("Consulta l'intero dossier monografico di orientamento clinico-professionale per la specializzazione prescelta.")

    all_specs = sorted(df_proj['disciplina'].unique())
    sel_spec = st.selectbox("Seleziona la Scuola di Specializzazione:", all_specs)

    slug = safe_filename(sel_spec)
    md_file = f"reports/specializzazioni/{slug}.md"

    if os.path.exists(md_file):
        with open(md_file, "r", encoding="utf-8") as f_md:
            text_md = f_md.read()
        
        # Sostituzione link relativi alle immagini per visualizzazione corretta in streamlit
        text_md = text_md.replace("../figures/radar/", "reports/figures/radar/")
        st.markdown(text_md, unsafe_allow_html=True)
    else:
        st.error(f"Scheda non trovata al percorso {md_file}")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 MedCareer 2031 — Progetto Open Science per l'orientamento medico.")
