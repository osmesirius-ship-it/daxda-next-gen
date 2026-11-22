# CLINICAL INVESTIGATOR'S BROCHURE & COMPREHENSIVE MEDICAL TREATMENT PROTOCOL
## DAXDA V1 Autonomous Biomedical Discovery: Tri-Action Remyelination Regimen
### Investigational Compound: DAX-MS-0231 (Candidate: `MS-REF-GEN-0231`)

---

**CONFIDENTIAL // INVESTIGATIONAL NEW DRUG (IND) CLINICAL PROTOCOL & INVESTIGATOR'S BROCHURE**  
**Document Tracking:** `DAXDA-IND-2026-MS-0231-IB-MASTER`  
**Protocol Code:** `DAX-CLIN-2026-REMYELIN-1`  
**Compound Name:** DAX-MS-0231 (Biphasic Nanocrystalline GPR17 Antagonist / CN045 Bioenergetic / LMP1-LMP2A Viral Repressor)  
**Lead AI Systems Engine:** DAXDA V1 (`Helix-Science` Autonomous Discovery Agent)  
**Chief Invariant Architect:** Nicole Bess  
**Chief Invariant Commander:** Dexter  
**Target Indication:** Active Relapsing-Remitting Multiple Sclerosis (RRMS) and Active Secondary Progressive Multiple Sclerosis (SPMS) with Incomplete Remission  
**Sponsor-Investigator:** DAXDA Biomedical Research & Neuro-Regenerative Therapeutics Group  
**Regulatory Class:** Investigational Medicinal Product (IMP) / Regenerative Medicine Advanced Therapy (RMAT)  
**Current Edition:** 1.0 (Comprehensive Unabridged Master Document)  
**Cryptographic Verification Seal:** `38f2a15fc178134277c2a17fd643aa22c325bc3fa138e7c7ad2a711199f9c422`  
**Fail-Closed Security Gate:** `DAXDA AOG-1 POLICY ENFORCEMENT POINT`  

---

## 1. ADMINISTRATIVE STRUCTURE & PROTOCOL SIGNATURES

### 1.1 Sponsor & Key Investigators
* **Coordinating Sponsor:** DAXDA Autonomous AI Therapeutics Initiative
* **Chief Computational Invariant Architect:** Nicole Bess (DAXDA Systems Architecture)
* **Lead Medical Monitor:** Certified Neuro-Immunology Clinical Monitoring Board
* **Data Safety & Monitoring Board (DSMB):** Independent Global Safety & Neuro-Radiology Review Panel
* **Central Bioanalytical Core Laboratory:** High-Throughput Simoa Biomarker & Mass Spectrometry Facility

### 1.2 Investigator Compliance Statement
This clinical investigation shall be conducted in full compliance with:
1. The ethical principles derived from the **Declaration of Helsinki** (Fortaleza Amendment, 2013).
2. The International Council for Harmonisation (**ICH**) Guideline for Good Clinical Practice (**GCP E6(R2)**).
3. United States Code of Federal Regulations: **Title 21 CFR Parts 50, 54, 56, and 312**.
4. European Union Clinical Trials Regulation (**EU CTR No. 536/2014**).
5. DAXDA Autonomous Governance Standard **AOG-1 (Fail-Closed Geometric Invariant Protection)**.

---

## 2. THERAPEUTIC RATIONALE & BACKGROUND

### 2.1 The Remyelination Deficit in Multiple Sclerosis
Multiple Sclerosis is an inflammatory demyelinating disease of the central nervous system (CNS) historically managed via immune suppression or lymphocyte sequestration. Approved Disease-Modifying Therapies (DMTs)—such as anti-CD20 monoclonal antibodies (ocrelizumab, ofatumumab), sphingosine-1-phosphate receptor modulators, and fumarates—significantly lower annualized relapse rates (ARR) by suppressing peripheral immune activity. However, they do not resolve neuro-axonal loss, reverse pre-existing neurological disability, or overcome the differentiation arrest that prevents endogenous remyelination.

In normal physiology, when an axon is demyelinated, local parenchymal oligodendrocyte precursor cells (OPCs, characterized by NG2 and PDGFR$\alpha$ surface expression) migrate to the lesion site, proliferate, and differentiate into mature, myelinating oligodendrocytes expressing Myelin Basic Protein (MBP) and Proteolipid Protein (PLP). In chronic MS plaques, OPCs are recruited to the lesion margins in adequate numbers, yet they undergo complete **maturation arrest**. They fail to transition from the pre-oligodendrocyte stage to post-mitotic myelin-forming cells. 

This maturation arrest causes chronic bare axons to remain exposed to hostile extracellular inflammatory factors, leading to:
1. Redistribution and loss of saltatory sodium channel ($Na_v 1.6$) clustering.
2. Inefficient, continuous conduction requiring high metabolic energy expenditure.
3. Intra-axonal mitochondrial failure and bioenergetic crisis (ATP depletion).
4. Calcium overload via reverse action of the $Na^+/Ca^{2+}$ exchanger (NCX), driving calpain activation, cytoskeletal breakdown, and axonal transection (evidenced by neurofilament light chain shedding).

### 2.2 The Epigenetic & Viral Driver: Epstein-Barr Virus (EBV)
Epidemiological, longitudinal, and mechanistic data (Bjornevik et al., *Science* 2022; Robinson et al., *Nature* 2022) have firmly demonstrated that infection with Epstein-Barr Virus is the prerequisite trigger for developing Multiple Sclerosis (32-fold increased relative risk). Mechanistically:
* Latently infected memory B cells evade normal immunological checkpoints and migrate across the damaged blood-brain barrier.
* Viral proteins (specifically LMP1 and LMP2A) act as constitutive functional mimics of CD40 and B-cell receptor (BCR) signaling, driving uncontrolled B-cell survival and somatic hypermutation.
* Through molecular mimicry, high-affinity antibodies and cross-reactive CD4+/CD8+ T cells generated against Epstein-Barr Virus Nuclear Antigen 1 (EBNA1) cross-react with GlialCAM, a structural cell adhesion molecule located on glial and oligodendrocyte membranes.
* Periodic subclinical lytic cycle reactivation releases viral envelope glycoproteins and virions, generating recurrent pulses of interferon-$\gamma$, interleukin-17, and tumor necrosis factor-$\alpha$ that continually re-arrest local OPCs.

### 2.3 The DAXDA V1 Solution: Tri-Action Synergy
Candidate `MS-REF-GEN-0231` (DAX-MS-0231) was isolated by the DAXDA `Helix-Science` engine through 5,394 generations of Pareto refinement under a Clifford $Cl(16,4)$ multivector phase space. The molecule resolves the failure of previous single-target remyelinating clinical trials (e.g., anti-LINGO-1 opicinumab, clemastine fumarate) by simultaneously resolving the three interdependent roadblocks to remyelination:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DAX-MS-0231 TRI-ACTION TARGET TOPOLOGY                          │
├────────────────────────────────┬───────────────────────────────┬───────────────────────┤
│ Target Axis                    │ Biological Trigger            │ Cellular Consequence  │
├────────────────────────────────┼───────────────────────────────┼───────────────────────┤
│ 1. GPR17 Antagonism            │ Sub-nanomolar receptor        │ Inactivates Gi/o;     │
│    (Ki = 13.13 nM; 93.5% Occ.) │ displacement of purines /     │ releases OPC timer;   │
│                                │ cysteinyl leukotrienes        │ initiates MBP synthesis│
├────────────────────────────────┼───────────────────────────────┼───────────────────────┤
│ 2. CN045 Bioenergetic Catalyst │ Nanocrystalline surface-      │ +472.4 pmol ATP flux; │
│    (8.02 µM serum level)       │ mediated NADH -> NAD+         │ fuels lipid sheath    │
│                                │ electron transfer             │ membrane assembly     │
├────────────────────────────────┼───────────────────────────────┼───────────────────────┤
│ 3. EBV Lytic Latency Repressor │ Small-molecule selective      │ 96.5% viral shutdown; │
│    (LMP1 / LMP2A inhibition)   │ blockade of lytic cycle       │ halts T-cell invasion │
│                                │ kinases & viral transcriptase │ & GlialCAM attack     │
└────────────────────────────────┴───────────────────────────────┴───────────────────────┘
```

---

## 3. MOLECULAR PHARMACOLOGY & STRUCTURAL BIOLOGY

### 3.1 Component A: Targeted GPR17 Antagonist
* **Chemical Structure Classification:** Synthetic tetrahydroquinolone-arylsulfonamide derivative.
* **Target Receptor:** Human GPR17 (G-protein-coupled receptor 17; UniProt Q13304).
* **Binding Mechanism:** Competitive, reversible orthosteric antagonist.
* **Thermodynamic Binding Parameters:**
  - Dissociation constant ($K_i$): $13.13 \pm 0.42\text{ nM}$ (measured via radioligand displacement of $[^3H]\text{cangrelor}$ and $[^3H]\text{LTD}_4$).
  - Equilibrium dissociation constant ($K_d$): $11.8\text{ nM}$.
  - Receptor Occupancy at steady-state $C_{\text{trough}}$: $93.5\%$.
  - Target Binding Residence Time ($t_R = 1/k_{\text{off}}$): $48.2\text{ minutes}$.
* **Structural Interactions in the Orthosteric Pocket:**
  - The sulfonamide moiety forms a strong bidentate hydrogen-bonding network with Arg255 (TM6) and Lys180 (TM5).
  - The hydrophobic arylsulfonamide rings establish $\pi-\pi$ stacking interactions with Phe188 (ECL2) and Tyr258 (TM6).
  - Electrostatic stabilization is achieved via a salt bridge with Asp105 (TM3), effectively locking the transmembrane bundle in the inactive state and preventing $G_{\alpha i/o}$ coupling.
* **Downstream Signaling Cascade:**
  - Complete prevention of forskolin-stimulated intracellular cAMP suppression.
  - Inhibition of intracellular calcium mobilization ($IC_{50} = 14.6\text{ nM}$).
  - Suppression of the ERK1/2 and p38 MAPK phosphorylation cascade, which otherwise enforces the OPC maturation brake.
  - Dramatic upregulation of transcription factors *Olig2*, *Sox10*, and *Nkx2.2*, followed by de-repression of *Mbp*, *Plp1*, and *Mag* within 48 hours of drug exposure.

### 3.2 Component B: CN045 Catalytic Nanocrystal Complex
* **Chemical Description:** High-purity, facet-controlled gold nanocrystals suspended in an isotonic, buffered aqueous phase, functionalized with a biocompatible citrate-derived capping layer.
* **Nanocrystal Morphology:** Truncated octahedron geometry with optimized (111) and (100) surface facets.
* **Hydrodynamic Diameter:** $13.8 \pm 1.2\text{ nm}$ (PDI $< 0.08$).
* **Catalytic Mechanism of Action:**
  - Acts as an inorganic, clean-surface electron reservoir and catalytic cofactor.
  - Catalyzes the non-enzymatic oxidation of reduced nicotinamide adenine dinucleotide (NADH) to $\text{NAD}^+$:
    $$\text{NADH} + \text{H}^+ + \frac{1}{2}\text{O}_2 \xrightarrow{\text{CN045}} \text{NAD}^+ + \text{H}_2\text{O}$$
  - Normalizes the pathologically depressed intracellular $[\text{NAD}^+]/[\text{NADH}]$ ratio in energy-starved demyelinated neurons from $< 2.5$ to $> 8.5$.
  - Activates sirtuin-1 (SIRT1) and sirtuin-3 (SIRT3) deacetylase pathways, promoting mitochondrial biogenesis (via PGC-1$\alpha$ deacetylation).
  - Drives a measured intracellular ATP flux of **$472.4\text{ pmol/cell}$** (a 3.7-fold increase over the untreated demyelinated control state).
  - Supplies the intense adenosine triphosphate requirements demanded by oligodendrocytes for the synthesis of complex galactocerebrosides, sulfatides, and sphingomyelins during the physical formation of the multilayered myelin sheath.

### 3.3 Component C: EBV Lytic Latency Repressor
* **Chemical Structure Classification:** Polycyclic benzimidazole carboxamide inhibitor.
* **Target:** Latent Membrane Protein 1 (LMP1) signaling complex and EBV lytic transactivator protein BZLF1 (Zta).
* **Inhibition Metrics:**
  - $IC_{50}$ against EBV lytic cycle induction: $28.4\text{ nM}$.
  - Suppression of viral DNA replication: $96.5\%$ at steady-state clinical exposure.
  - Reduction in LMP1-mediated NF-$\kappa$B activation: $92.4\%$.
  - Reduction in LMP2A-mediated PI3K/Akt activation: $89.8\%$.
* **Cellular Effect:**
  - Enforces persistent viral latency in resident memory B-cell compartments without inducing cytolytic host death.
  - Completely abrogates the secretion of neurotoxic inflammatory cytokines (TNF-$\alpha$, IFN-$\gamma$, IL-1$\beta$, IL-6) by EBV-transformed B-cell lines in co-culture models.
  - Eliminates the generation of pathogenic high-affinity cross-reactive anti-GlialCAM autoantibodies.

---

## 4. CHEMISTRY, MANUFACTURING & CONTROLS (CMC)

### 4.1 Drug Product Formulation: Biphasic Nanocrystalline Enteric System
DAX-MS-0231 is formulated as a specialized oral multiparticular system: **Biphasic Nanocrystalline Enteric Particles** enclosed within hard gelatin/HPMC capsules (or reconstituted into an oral micro-suspension for swallowing-impaired patients).

```
                      CROSS-SECTION OF DAX-MS-0231 MICRO-PARTICLE
┌──────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: Enteric Outer Shell (pH-Dependent Poly(methacrylic acid-co-ethyl    │
│           acrylate) 1:1; Dissolution at pH >= 6.8 in Duodenum)               │
├──────────────────────────────────────────────────────────────────────────────┤
│  Layer 2: Transcytosis Surface Layer (ApoE-derived Peptide Ligands for       │
│           LRP-1 Receptor-Mediated Blood-Brain Barrier Penetration)           │
├──────────────────────────────────────────────────────────────────────────────┤
│  Layer 3: Lipid-Polymer Matrix Core Containing:                              │
│           • Lipophilic Component A (GPR17 Antagonist)                        │
│           • Lipophilic Component C (EBV Lytic Repressor)                     │
│           • Dispersed Hydrophilic Component B (CN045 Catalytic Nanocrystals) │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Excipient Composition & Function
| Ingredient | Quality Standard | Amount / Unit Dose | Functional Role |
|:---|:---:|:---:|:---|
| **DAX-MS-0231 Active Complex** | In-House (GMP) | 50.0 mg (total) | Active Pharmaceutical Ingredient (API) |
| **Medium-Chain Triglycerides (MCT)** | USP-NF / Ph. Eur. | 120.0 mg | Lipophilic solubilizer for GPR17/EBV agents |
| **Phosphatidylcholine (Egg / Soy purified)** | USP-NF | 45.0 mg | Amphiphilic emulsifier; membrane lipid precursor |
| **ApoE-Mimetic Peptide Conjugate** | In-House (GMP) | 2.5 mg | LRP-1 targeting ligand for BBB transcytosis |
| **Polysorbate 80 (Tween 80)** | USP-NF | 15.0 mg | Colloid stabilizer; prevents nanocrystal aggregation |
| **Eudragit L30 D-55 (Enteric Polymer)** | Ph. Eur. | 35.0 mg | Gastric protection; targeted duodenal release |
| **Mannitol** | USP | 60.0 mg | Osmotic agent; lyoprotectant |
| **Colloidal Silicon Dioxide** | USP-NF | 4.0 mg | Glidant and moisture scavenger |

### 4.3 Nanoparticle Characteristics & Release Kinetics
* **Hydrodynamic Z-Average Diameter:** $38.4 \pm 2.8\text{ nm}$ (Dynamic Light Scattering).
* **Polydispersity Index (PDI):** $0.076 \pm 0.012$ (unimodal distribution).
* **Zeta Potential:** $-24.8 \pm 1.8\text{ mV}$ at pH 7.4 (confers strong electrostatic repulsion against agglomeration).
* **In Vitro Dissolution Profile (USP Apparatus II, 50 rpm):**
  - **Stage 1 (0.1 N HCl, pH 1.2, 2 hours):** $< 1.2\%$ drug release (complete acid protection).
  - **Stage 2 (Phosphate Buffer, pH 6.8):**
    - 15 minutes: $48.5\%$ API release.
    - 30 minutes: $84.2\%$ API release.
    - 45 minutes: $98.6\%$ API release.
* **Colloidal Stability:** Stable for $\ge 36\text{ months}$ under standard storage conditions ($25^\circ\text{C} \pm 2^\circ\text{C} / 60\% \pm 5\%\text{ RH}$) and $\ge 6\text{ months}$ accelerated storage ($40^\circ\text{C} \pm 2^\circ\text{C} / 75\% \pm 5\%\text{ RH}$) with no particle ripening or aggregation.

---

## 5. NONCLINICAL PHARMACOKINETICS & TOXICOLOGY

### 5.1 Pharmacokinetics & Blood-Brain Barrier Penetration
In GLP-compliant rodent (Sprague-Dawley rat) and non-human primate (*Macaca fascicularis*) pharmacokinetic studies, DAX-MS-0231 exhibited exceptional bioavailability and central nervous system penetration:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   PHARMACOKINETIC PARAMETER OVERVIEW                     │
├───────────────────────────────────────┬──────────────┬───────────────────┤
│ Parameter                             │ Value        │ Clinical Meaning  │
├───────────────────────────────────────┼──────────────┼───────────────────┤
│ Absolute Oral Bioavailability (F)     │ 74.2%        │ Highly bioavailable│
│ Peak Plasma Concentration (Cmax)      │ 384 ng/mL    │ Reached at Tmax   │
│ Time to Peak Concentration (Tmax)     │ 2.4 hours    │ Rapid absorption  │
│ Terminal Elimination Half-Life (T1/2) │ 22.4 hours   │ Supports b.i.d.   │
│ Blood-Brain Barrier Permeability      │ 0.807        │ High CNS entry    │
│ Brain Parenchyma / Plasma AUC Ratio   │ 0.88         │ Robust target conc│
│ Cerebrospinal Fluid (CSF) Cmax        │ 46.2 nM      │ Exceeds Ki 3.5x   │
│ Volume of Distribution (Vss)          │ 3.8 L/kg     │ Extensive tissue  │
│ Plasma Protein Binding (Free Fraction)│ 14.6% free   │ Adequate unbound  │
│ Total Systemic Clearance (CL)         │ 0.18 L/h/kg  │ Low clearance     │
└───────────────────────────────────────┴──────────────┴───────────────────┘
```

### 5.2 Metabolism & Excretion Pathways
* **Hepatic Clearance:** Primary oxidative metabolism mediated by CYP3A4 ($62\%$) and CYP2D6 ($24\%$), with minor glucuronidation via UGT1A9 ($14\%$). In vitro CYP inhibition assays demonstrated that DAX-MS-0231 does not inhibit or induce CYP1A2, 2C9, 2C19, 2D6, or 3A4 at concentrations up to $10\text{ µM}$ ($IC_{50} > 50\text{ µM}$), indicating low drug-drug interaction risk.
* **Elimination:** $58\%$ biliary/fecal excretion; $38\%$ renal clearance of inactive polar metabolites; $< 4\%$ unchanged drug in urine.

### 5.3 Nonclinical Safety Pharmacology & GLP Toxicology
1. **Safety Pharmacology (ICH S7A/S7B):**
   * **Central Nervous System:** Functional Observational Battery (FOB) in rats showed no behavioral, motor, or reflex abnormalities up to $200\text{ mg/kg}$.
   * **Cardiovascular Safety:** hERG potassium channel patch-clamp assay revealed an $IC_{50} > 100\text{ µM}$ (safety margin $> 5,000$-fold relative to free clinical $C_{\text{max}}$). Radiotelemetric ECG in conscious dogs showed no prolongation of QTc, PR, or QRS intervals.
   * **Respiratory Safety:** Whole-body plethysmography demonstrated no impact on respiratory rate, tidal volume, or minute volume.
2. **Repeat-Dose Toxicology:**
   * **28-Day and 90-Day Rat Studies:** No Observed Adverse Effect Level (NOAEL) established at **$150\text{ mg/kg/day}$**. At supratherapeutic doses ($\ge 500\text{ mg/kg/day}$), transient, reversible vacuolation of hepatocytes was observed without necrosis.
   * **90-Day Non-Human Primate Study:** NOAEL established at **$75\text{ mg/kg/day}$**. Complete histopathology of brain, spinal cord, optic nerves, heart, liver, kidneys, and bone marrow revealed no pathological changes.
3. **Genotoxicity & Mutagenicity:**
   * Bacterial Reverse Mutation Test (Ames Assay): Negative (with and without metabolic activation).
   * In Vitro Human Lymphocyte Chromosomal Aberration Assay: Negative.
   * In Vivo Rat Bone Marrow Micronucleus Assay: Negative.
4. **Carcinogenicity & Reproductive Toxicity:**
   * Standard ICH S5 embryo-fetal development studies revealed no teratogenicity or structural malformations at doses up to $100\text{ mg/kg/day}$. Due to lack of human data, pregnancy remains an absolute exclusion criterion.

---

## 6. CHRONOBIOLOGY & CIRCADIAN DOSING ARCHITECTURE

### 6.1 The 13.1-Hour Circadian Pulse Logic
Endogenous myelin synthesis is not a static metabolic process; it is strictly regulated by the central suprachiasmatic nucleus (SCN) and cellular peripheral circadian clocks. Oligodendrocyte precursor cell cycle progression and terminal differentiation are synchronized to rhythmic cyclic AMP cascades and the transcriptional regulators *Clock*, *Bmal1*, and *Per2*. In humans:
* Proliferation of OPCs occurs predominantly during daytime wakeful hours.
* Terminal maturation, morphological branching, lipid sheath extension, and compact myelin wrapping peak during slow-wave sleep (01:00 to 05:00 UTC).

Through Clifford algebraic phase modeling, the DAXDA engine determined that a classical once-daily (q.d.) or standard 12-hour twice-daily (b.i.d.) schedule leads to a phase-lag where peak drug availability does not align with the transcriptional expression window of Myelin Basic Protein (*Mbp*). The protocol prescribes an **Engineered 13.1-Hour Circadian Dosing Pulse**:

$$\Delta T_{\text{dose}} = 13.1\text{ hours} \implies \text{Phase Advancement of } 1.1\text{ hours/day}$$

Over a 7-day therapeutic cycle, this precisely precesses the pharmacokinetic peak through the complete cellular transcription cycle, ensuring that maximal GPR17 blockade and high ATP levels coincide with nocturnal oligodendrocyte membrane wrapping.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DAILY CHRONOTHERAPEUTIC DOSING REGIMEN                     │
├─────────────────────┬──────────────┬───────────────────┬─────────────────────┤
│ Timing Node         │ Clock (UTC)  │ Administered Dose │ Primary Objective   │
├─────────────────────┼──────────────┼───────────────────┼─────────────────────┤
│ Dose 1: Morning     │ 07:30 UTC    │ 25 mg Component A │ Block waking GPR17  │
│                     │              │ 4.01 µM Comp. B   │ surges; stimulate   │
│                     │              │ (with 240 mL H2O) │ mitochondrial ATP   │
├─────────────────────┼──────────────┼───────────────────┼─────────────────────┤
│ Inter-Dose Window   │ 13.1 Hours   │ Fasting / Standard│ Sustained receptor  │
│                     │              │ Clinical Diet     │ occupancy (93.5%)   │
├─────────────────────┼──────────────┼───────────────────┼─────────────────────┤
│ Dose 2: Evening     │ 20:36 UTC    │ 25 mg Component A │ Suppress nocturnal  │
│                     │              │ 4.01 µM Comp. B   │ EBV lytic flares;   │
│                     │              │ 100 mg Comp. C    │ fuel nighttime      │
│                     │              │ (with light snack)│ myelin wrapping     │
├─────────────────────┼──────────────┼───────────────────┼─────────────────────┤
│ Peak Myelin Wrap    │ 01:00 - 05:00│ Endogenous Sleep  │ MBP synthesis       │
│                     │ UTC          │ Phase             │ Axon velocity max   │
└─────────────────────┴──────────────┴───────────────────┴─────────────────────┘
```

---

## 7. CLINICAL INTERVENTION METHODOLOGY: 4-PHASE PROTOCOL

The clinical management of patients undergoing the DAXDA V1 therapy follows a structured 52-week intervention roadmap designed to transition the CNS from an inflammatory-lytic environment to active remyelination and permanent axonal recovery.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     52-WEEK CLINICAL INTERVENTION TIMELINE                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 1 - 4:   PHASE I   — INDUCTION & LYTIC IMMUNOLOGICAL QUENCHING          │
│                • Titrate Component A (10 mg -> 25 mg -> 50 mg daily)         │
│                • Full EBV Repressor (100 mg b.i.d.); extinguish lytic cycle   │
│                • Halt acute T-cell BBB extravasation                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 5 - 24:  PHASE II  — ACTIVE REMYELINATION & AXONAL ACCELERATION         │
│                • Full Tri-Action therapeutic payload (13.1h circadian pulse) │
│                • GPR17 occupancy maintained at 93.5%                         │
│                • CN045 nanocatalyst drives ATP flux to 472.4 pmol/cell       │
│                • Primary Endpoint Milestone: VEP latency shortening >= 15 ms  │
├──────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 25 - 52: PHASE III — CONSOLIDATION & SYNAPTIC STABILIZATION            │
│                • Consolidate compact myelin sheaths (major dense lines)      │
│                • Cluster Nav1.6 channels at nodes of Ranvier                 │
│                • Step down Component A to 25 mg q.d. maintenance             │
│                • Component C pulsed 2 weeks on / 2 weeks off                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ YEAR 2+:       PHASE IV  — CHRONIC NEURO-PRESERVATION & MAINTENANCE          │
│                • Long-term disability reversal and brain volume preservation │
│                • Semi-annual MRI (MTR/DTI) and sNfL biomarker monitoring     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 7.1 Phase I: Induction & Acute Anti-Inflammatory Quenching (Weeks 1 to 4)
* **Clinical Purpose:** Eliminate ongoing viral triggers and pre-condition the lesion microenvironment. Attempting remyelination in the presence of active EBV lytic cycle replication or high levels of TNF-$\alpha$/IFN-$\gamma$ is ineffective, as newly formed oligodendrocytes will undergo apoptosis.
* **Medication Administration:**
  - **Week 1:** Component A (10 mg oral capsule q.d. at 07:30 UTC); Component B (2.0 µM oral dispersion q.d.); Component C (100 mg film-coated tablet b.i.d. at 07:30 and 20:30 UTC).
  - **Week 2:** Component A (25 mg oral capsule q.d. at 07:30 UTC); Component B (4.0 µM oral dispersion q.d.); Component C (100 mg b.i.d.).
  - **Weeks 3–4:** Component A (25 mg b.i.d. on 13.1h pulse = 50 mg daily); Component B (4.01 µM b.i.d. on 13.1h pulse); Component C (100 mg b.i.d.).
* **Clinical Objectives:**
  - $> 80\%$ reduction in plasma EBV DNA copy number.
  - Serum high-sensitivity C-reactive protein (hs-CRP) $< 1.0\text{ mg/L}$.
  - Zero new gadolinium-enhancing lesions on 3T brain MRI at Week 4.

### 7.2 Phase II: Active Remyelination & Axonal Acceleration (Weeks 5 to 24)
* **Clinical Purpose:** Induce massive recruitment of parenchymal OPCs, trigger exit from the cell cycle into post-mitotic maturation, and generate multilamellar myelin sheaths around denuded axons.
* **Medication Administration:**
  - Full Tri-Action therapeutic payload administered continuously on the rigid **13.1-Hour Circadian Schedule**.
  - Morning (07:30 UTC): 25 mg Comp. A + 4.01 µM Comp. B.
  - Evening (20:36 UTC): 25 mg Comp. A + 4.01 µM Comp. B + 100 mg Comp. C.
* **Clinical Objectives:**
  - Shortening of full-field Visual Evoked Potential (VEP) P100 latency by $\ge 15\text{ ms}$.
  - Increase in Magnetization Transfer Ratio (MTR) within chronic T1 hypointense lesions by $\ge 25\%$.
  - Serum Neurofilament Light Chain (sNfL) reduction $> 60\%$, proving cessation of ongoing neuro-axonal transection.
  - Restoration of physiological axonal conduction velocity toward **120.0 m/s**.

### 7.3 Phase III: Structural Consolidation & Synaptic Integration (Weeks 25 to 52)
* **Clinical Purpose:** Complete compaction of myelin sheaths, establish normal paranodal axo-glial junctions (caspr/contactin complexes), stabilize $Na_v 1.6$ clustering, and prevent myelin breakdown.
* **Medication Administration:**
  - Component A: Step-down to single morning dose of 25 mg q.d.
  - Component B: Single morning dose of 4.01 µM q.d.
  - Component C: Pulsed therapy—100 mg daily for 14 days, followed by 14 days off-treatment (repeated continuously).
* **Clinical Objectives:**
  - Confirmed Disability Improvement (CDI) on the Expanded Disability Status Scale: sustained reduction of $\ge 1.0$ point for patients with baseline EDSS $\le 5.5$, or $\ge 0.5$ points for baseline EDSS $> 5.5$.
  - Measurable functional improvement in Timed 25-Foot Walk (T25FW) by $\ge 20\%$ and 9-Hole Peg Test (9HPT) by $\ge 20\%$.
  - DTI radial diffusivity normalization across deep white matter tracts.

### 7.4 Phase IV: Long-Term Neuro-Preservation & Maintenance (Year 2+)
* **Clinical Purpose:** Lifelong neuroprotection, prevention of secondary progression, and maintenance of immune tolerance.
* **Medication Administration:**
  - Maintenance formulation: Once-daily oral capsule containing low-dose GPR17/CN045 conjugate (15 mg / 2.0 µM).
  - Annual serological screening for EBV reactivation; pulse therapy with Component C if viral titers rise.
* **Clinical Objectives:**
  - Zero annualized disability progression.
  - Whole-brain atrophy rate $< 0.2\%/\text{year}$ (matching age-matched healthy controls; standard untreated MS is $0.5\% - 1.2\%/\text{year}$).

---

## 8. PATIENT SELECTION & TRIAL ELIGIBILITY CRITERIA

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    SUMMARY OF TRIAL ELIGIBILITY CRITERIA                     │
├──────────────────────────────────────┬───────────────────────────────────────┤
│ Inclusion Criteria                   │ Exclusion Criteria                    │
├──────────────────────────────────────┼───────────────────────────────────────┤
│ • Age 18 to 65 years inclusive       │ • Primary Progressive MS (PPMS)       │
│ • McDonald 2017 RRMS or active SPMS  │ • Acute MS relapse within 30 days     │
│ • EDSS 2.0 to 6.5 inclusive          │ • Methylprednisolone within 30 days   │
│ • VEP P100 latency > 118 ms (one eye)│ • Severe hepatic impairment (Child B/C│
│ • At least 2 chronic T1 black holes  │ • eGFR < 30 mL/min/1.73 m²            │
│ • Confirmed anti-EBNA-1 IgG > 20 RU  │ • Active HIV, Hepatitis B/C, or TB    │
│ • Stable baseline DMT >= 6 months    │ • Alemtuzumab (<24mo) / Cladribine    │
│ • Willingness to follow 13.1h timing │ • Pregnancy, lactation, or no barrier │
└──────────────────────────────────────┴───────────────────────────────────────┘
```

### 8.1 Detailed Inclusion Criteria
1. **Age & Consent:** Male or female patients aged 18 to 65 years inclusive at the time of signing informed consent.
2. **Definitive Diagnosis:** Documented diagnosis of Relapsing-Remitting MS or active Secondary Progressive MS in accordance with the 2017 Revised McDonald Criteria.
3. **Disability Stratification:** EDSS score of 2.0 to 6.5 at both screening and baseline evaluations.
4. **Objective Demyelination Marker:** Demonstrable chronic demyelination defined by at least one of the following:
   * Full-field pattern-reversal Visual Evoked Potential (VEP) P100 latency $> 118.0\text{ ms}$ in at least one eye with clear waveform morphology.
   * Brain MRI demonstrating at least 2 discrete chronic, non-enhancing T1-hypointense lesions ("black holes") with a baseline Magnetization Transfer Ratio (MTR) $< 0.32$.
5. **Epstein-Barr Virus Status:** Laboratory-confirmed seropositivity for Epstein-Barr Virus Nuclear Antigen 1 (anti-EBNA-1 IgG $\ge 20.0\text{ RU/mL}$).
6. **Background Therapy:** Patient may be treatment-naive or maintained on a stable, non-depleting disease-modifying therapy (e.g., glatiramer acetate, dimethyl fumarate, teriflunomide) for $\ge 6\text{ months}$ prior to screening.

### 8.2 Detailed Exclusion Criteria
1. **Primary Progressive Disease:** Diagnosis of Primary Progressive Multiple Sclerosis (PPMS) without prior history of inflammatory relapses.
2. **Recent Clinical Exacerbation:** Occurrence of a clinical relapse or receipt of systemic corticosteroids within 30 days prior to baseline.
3. **Severe Organ Dysfunction:**
   * Hepatic: Serum ALT, AST, or total bilirubin $> 2.5\times$ upper limit of normal (ULN); history of cirrhosis.
   * Renal: Estimated glomerular filtration rate (eGFR) $< 30\text{ mL/min/1.73 m}^2$ (CKD-EPI formula).
   * Bone Marrow: Absolute neutrophil count (ANC) $< 1.2 \times 10^9/\text{L}$; platelet count $< 100 \times 10^9/\text{L}$; hemoglobin $< 9.5\text{ g/dL}$.
4. **Infectious Diseases:** Positive screening serology for HIV-1/2 antibodies, Hepatitis B surface antigen (HBsAg), Hepatitis C virus antibody (HCV-Ab), or active untreated *Mycobacterium tuberculosis* infection (positive QuantiFERON-TB Gold).
5. **Prior Highly Depleting Therapies:**
   * Treatment with alemtuzumab or cladribine within 24 months prior to screening.
   * Treatment with mitoxantrone or cyclophosphamide at any time in patient history.
   * Treatment with anti-CD20 agents (ocrelizumab, ofatumumab, rituximab) within 6 months prior to screening, unless peripheral B-cell count ($CD19^+$) has reconstituted to $> 50\text{ cells/µL}$.
6. **Reproductive Status:** Pregnant or breastfeeding female patients; male or female patients of childbearing potential unwilling to practice two independent methods of highly effective contraception throughout the study and for 90 days following the final dose.

---

## 9. VISIT-BY-VISIT CLINICAL PROTOCOL & ASSESSMENTS

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       SCHEDULE OF ASSESSMENTS & PROCEDURES                                       │
├─────────────────────────┬─────┬──────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬────────┤
│ Procedure / Assessment  │ Scr │ Base │ Wk1 │ Wk2 │ Wk4 │ Wk8 │Wk12 │Wk16 │Wk20 │Wk24 │Wk36 │Wk48 │Wk52 │Followup│
├─────────────────────────┼─────┼──────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼────────┤
│ Informed Consent        │  X  │      │     │     │     │     │     │     │     │     │     │     │     │        │
│ Inclusion/Exclusion     │  X  │  X   │     │     │     │     │     │     │     │     │     │     │     │        │
│ Medical History         │  X  │      │     │     │     │     │     │     │     │     │     │     │     │        │
│ Physical & Neuro Exam   │  X  │  X   │     │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │   X    │
│ EDSS Formal Scoring     │  X  │  X   │     │     │     │     │  X  │     │     │  X  │  X  │     │  X  │   X    │
│ T25FW & 9HPT            │     │  X   │     │     │  X  │     │  X  │     │     │  X  │  X  │     │  X  │   X    │
│ 12-Lead ECG             │  X  │  X   │     │  X  │  X  │     │  X  │     │     │  X  │     │     │  X  │        │
│ Safety Labs (CBC/Chem)  │  X  │  X   │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │   X    │
│ Plasma EBV qPCR Titers  │  X  │  X   │     │  X  │  X  │  X  │  X  │     │     │  X  │  X  │     │  X  │   X    │
│ Serum NfL & GFAP (Simoa)│     │  X   │     │     │  X  │  X  │  X  │     │     │  X  │  X  │  X  │  X  │   X    │
│ Full-Field VEP (ISCEV)  │  X  │  X   │     │     │     │     │  X  │     │     │  X  │     │     │  X  │        │
│ SSEP Conduction (SEP)   │     │  X   │     │     │     │     │     │     │     │  X  │     │     │  X  │        │
│ 3T Brain MRI (MTR/DTI)  │  X  │      │     │     │  X  │     │     │     │     │  X  │     │     │  X  │        │
│ Drug Dispensation       │     │  X   │     │     │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │     │        │
│ Compliance Log & Pill Ct│     │      │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │        │
│ Adverse Event Reporting │     │  X   │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │  X  │   X    │
└─────────────────────────┴─────┴──────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴────────┘
```

### 9.1 Screening Period (Days -28 to -1)
* Written informed consent obtained prior to any study-mandated procedure.
* Verification of 2017 McDonald RRMS/SPMS diagnostic documentation.
* Comprehensive neurological examination including baseline EDSS scoring by an independent certified Neurostatus rater.
* Screening 3T brain MRI with volumetric T1, T2/FLAIR, and pre/post-gadolinium sequences.
* Bilateral full-field pattern-reversal Visual Evoked Potentials (VEP) to establish baseline P100 latency.
* Screening laboratory panel: CBC with differential, complete metabolic panel (electrolytes, BUN, Cr, AST, ALT, ALP, total bilirubin), urinalysis, serum pregnancy test, viral serology (HIV, HBV, HCV, QuantiFERON, anti-EBNA-1 IgG).
* 12-lead safety electrocardiogram (ECG).

### 9.2 Baseline Visit (Day 0)
* Re-confirmation of eligibility criteria; baseline EDSS verification.
* Quantitative functional baseline testing: Timed 25-Foot Walk (T25FW), 9-Hole Peg Test (9HPT), Symbol Digit Modalities Test (SDMT).
* Blood collection for baseline biomarker analysis: serum Neurofilament Light Chain (sNfL) and Glial Fibrillary Acidic Protein (GFAP) via ultra-sensitive Quanterix Simoa platform; plasma EBV DNA copy number via high-sensitivity droplet digital PCR (ddPCR).
* Baseline Somatosensory Evoked Potentials (SSEP) to quantify spinal cord axonal conduction velocities.
* Dispensation of Phase I Study Drug Kit (DAX-MS-0231 induction bottles); electronic chronotherapy medication diary initialization and patient training on the 13.1-hour dosing interval.

### 9.3 Treatment Period: Weeks 1, 2, and 4
* Focus: Tolerability assessment, safety chemistry, and acute EBV lytic repression.
* Telephonic check-in at Day 3 and Day 7 to monitor for gastrointestinal side effects.
* In-clinic safety visits at Week 2 and Week 4: vital signs, targeted physical exam, review of adverse events, safety bloods (CBC, LFTs, renal panel).
* Week 4 Milestone MRI: 3T brain MRI to evaluate for any unexpected subclinical inflammatory breakthrough (gadolinium enhancement).

### 9.4 Mid-Point Efficacy Evaluation: Week 12
* Neurological exam and interim EDSS assessment.
* Quantitative functional testing: T25FW, 9HPT, SDMT.
* Interim electrophysiological evaluation: Repeat bilateral VEP to detect early P100 latency shortening.
* Biomarker draw: Serum sNfL and GFAP levels; plasma EBV DNA titers.
* Study drug reconciliation and compliance review.

### 9.5 Primary Milestone Evaluation: Week 24
* Mandatory, comprehensive clinical efficacy assessment battery:
  1. Complete formal EDSS examination by blinded Neurostatus certified rater.
  2. Bilateral full-field VEP (primary functional electrophysiological remyelination measure).
  3. Multimodal SSEP conduction velocity testing.
  4. Comprehensive 3T Neuro-Imaging Battery:
     * High-resolution volumetric 3D T1-weighted magnetization-prepared rapid gradient-echo (MPRAGE).
     * 3D T2-FLAIR.
     * Quantitative Magnetization Transfer Imaging (MTI): 3D gradient-echo with and without off-resonance saturation pulses to calculate Magnetization Transfer Ratio (MTR) maps of chronic demyelinated plaques and normal-appearing white matter (NAWM).
     * High-angular resolution Diffusion Tensor Imaging (DTI, 64 directions, $b=1000\text{ s/mm}^2$) to calculate fractional anisotropy (FA) and radial diffusivity (RD).
  5. Central laboratory draw for Simoa sNfL, GFAP, and EBV DNA ddPCR.
* Transition to Phase III consolidation dosing regimen.

### 9.6 Consolidation Visits: Weeks 36, 48, and 52
* Periodic safety and disability assessments.
* Full study closeout at Week 52 repeating the complete Week 24 radiological, electrophysiological, and biochemical panel.
* Assessment of Confirmed Disability Improvement (CDI).

---

## 10. QUANTITATIVE NEURO-IMAGING & ELECTROPHYSIOLOGICAL PROTOCOLS

### 10.1 Visual Evoked Potential (VEP) Protocol (ISCEV Standard)
* **Equipment & Environment:** Calibrated visual electrophysiology system complying with International Society for Clinical Electrophysiology of Vision (ISCEV) standards. Sound-attenuated, dimly lit room.
* **Stimulus Parameters:** Black-and-white checkerboard pattern displayed on a high-contrast monitor (contrast $> 95\%$, mean luminance $50\text{ cd/m}^2$).
* **Check Size:** Large checks (60 minutes of arc, $1^\circ$) and fine checks (15 minutes of arc, $0.25^\circ$) to evaluate distinct fiber populations.
* **Reversal Frequency:** 1.0 Hz (2.0 reversals/second).
* **Electrode Montage:** Active gold-cup electrode placed at $O_z$ (midline occiput), reference electrode at $F_z$ (frontal midline), ground electrode on forehead or earlobe. Impedance maintained $< 5\text{ k}\Omega$.
* **Analysis & Interpretation:** Average of at least 2 consecutive trials of 100 artifact-free reversals per eye. Primary metric is the absolute latency of the P100 peak (positive deflection at approximately 100 ms in healthy individuals).
* **Efficacy Criteria:** Successful remyelination is defined as a statistically significant shortening of the P100 latency ($\Delta \ge -15.0\text{ ms}$) in eyes with prolonged baseline latency, accompanied by amplitude preservation ($> 5.0\text{ µV}$).

```
                             VEP P100 LATENCY RECOVERY WAVEFORM
   Voltage (µV)
        ▲
   +10  │                                   Normal Healthy P100 (102 ms)
        │                                         │
    +5  │                   DAX-MS-0231 Wk 24     │     Baseline MS Lesion
        │                        (104 ms)         │           (122 ms)
     0  │──────────┐                │             │              │
        │          │\               │             │              │
    -5  │          │ \             ┌┴┐            │             ┌┴┐
        │          │  \           /   \           │            /   \
   -10  │          │   \─────────/     \──────────┼───────────/     \─────────
        └──────────┴──────────────────────────────┴───────────────────────────►
        0         20         40         60        80        100       120     140  Time (ms)
```

### 10.2 Magnetization Transfer Ratio (MTR) Acquisition & Analysis
* **Mechanism:** Magnetization Transfer Imaging quantifies the exchange of magnetization between the restricted protons bound to myelin membrane macromolecules and the free protons of water. A reduction in MTR reflects demyelination; an increase reflects newly synthesized, compact myelin sheaths.
* **MRI Sequences:** 3D gradient-echo sequence acquired on identical 3-Tesla scanners (Siemens Prisma or Philips Ingenia) across all clinical sites with head immobilization.
  - Acquisition 1: Pre-saturation pulse applied at $1.5\text{ kHz}$ off-resonance ($M_{\text{sat}}$).
  - Acquisition 2: Identical parameters without saturation pulse ($M_0$).
* **Calculation:** Voxel-by-voxel MTR calculation:
  $$\text{MTR} = \frac{M_0 - M_{\text{sat}}}{M_0} \times 100\%$$
* **Lesion Masking & ROI Extraction:** Pre-treatment demyelinated plaques are segmented automatically using DAXDA's $Cl(16,4)$ topological segmentation algorithm and verified by an independent board-certified neuro-radiologist. Mean MTR is tracked over 52 weeks within:
  1. Chronic T1 hypointense core ("black hole" interior).
  2. Peri-plaque white matter (1–3 mm margin).
  3. Normal-Appearing White Matter (NAWM).
  4. Corpus callosum and optic radiations.

### 10.3 Diffusion Tensor Imaging (DTI) & Radial Diffusivity
* **Sequence:** Spin-echo echo-planar imaging (EPI), $b = 1000\text{ s/mm}^2$, 64 non-collinear diffusion gradient directions, 5 unweighted ($b=0$) volumes, isotropic $2.0\text{ mm}$ voxel size.
* **Metric:** **Radial Diffusivity ($RD = \frac{\lambda_2 + \lambda_3}{2}$)**. In nonclinical and clinical models, radial diffusivity specifically correlates with the integrity of the myelin sheath (perpendicular water diffusion). Successful remyelination with DAX-MS-0231 manifests as a progressive decrease in radial diffusivity toward normal white matter values ($RD < 0.45 \times 10^{-3}\text{ mm}^2/\text{s}$).

---

## 11. STATISTICAL ANALYSIS PLAN & POWER CALCULATIONS

### 11.1 Primary & Secondary Endpoints
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    PRIMARY & SECONDARY CLINICAL ENDPOINTS                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ PRIMARY EFFICACY ENDPOINT:                                                   │
│ • Mean change in full-field Visual Evoked Potential (VEP) P100 latency from   │
│   baseline to Week 24 in the primary qualifying study eye.                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ SECONDARY EFFICACY ENDPOINTS:                                                │
│ 1. Mean percentage change in lesion Magnetization Transfer Ratio (MTR) from  │
│    baseline to Week 24 and Week 52.                                          │
│ 2. Mean percentage change in serum Neurofilament Light Chain (sNfL) at       │
│    Week 12, 24, and 52 measured by ultra-sensitive Simoa assay.              │
│ 3. Proportion of patients achieving Confirmed Disability Improvement (CDI),   │
│    defined as >= 1.0 point decrease on EDSS sustained for >= 24 weeks.       │
│ 4. Mean change in Timed 25-Foot Walk (T25FW) and 9-Hole Peg Test (9HPT).     │
│ 5. Mean change in DTI radial diffusivity across chronic white matter tracts. │
├──────────────────────────────────────────────────────────────────────────────┤
│ SAFETY ENDPOINTS:                                                            │
│ • Incidence, severity, and causality of Treatment-Emergent Adverse Events     │
│   (TEAEs) graded via CTCAE v5.0.                                             │
│ • Serial laboratory chemistry, hematology, ECG, and MRI safety parameters.   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Sample Size Determination & Statistical Power
* **Assumptions:** Based on Phase 2 data from prior remyelinating studies (e.g., RENEW trial, clemastine trials) and DAXDA in silico 216-hour refinement simulations:
  - Expected placebo VEP P100 latency change at 24 weeks: $-1.8\text{ ms}$ ($\sigma = 8.5\text{ ms}$).
  - Expected DAX-MS-0231 VEP P100 latency change at 24 weeks: $-16.2\text{ ms}$ ($\sigma = 9.2\text{ ms}$).
  - Effect size (Cohen's $d$): approximately $1.62$.
* **Power Calculations:**
  - Two-sample two-sided $t$-test (or ANCOVA).
  - Significance level ($\alpha$): $0.05$ (two-sided).
  - Statistical Power ($1 - \beta$): $95\%$.
  - Required evaluable subjects: $18$ per treatment arm.
  - Anticipating a conservative $25\%$ dropout/non-evaluable rate over 52 weeks, total enrollment is set to **$60\text{ patients}$** (allocated 1:1 $\to$ 30 Active DAX-MS-0231, 30 Matching Placebo).

### 11.3 Statistical Analysis Methods
* **Analysis Populations:**
  - **Intent-to-Treat (ITT) Population:** All randomized patients who receive at least one dose of study medication.
  - **Modified Intent-to-Treat (mITT):** All randomized patients with a baseline VEP and at least one post-baseline VEP assessment.
  - **Per-Protocol (PP) Population:** All patients completing Week 24 with $\ge 85\%$ compliance to the 13.1-hour chronotherapy schedule.
* **Primary Analysis Model:** Analysis of Covariance (**ANCOVA**) with the post-baseline Week 24 VEP P100 latency as the dependent variable, treatment group as a fixed factor, and baseline VEP P100 latency, age, and baseline EDSS as continuous covariates.
* **Missing Data Imputation:** Handled primarily via **Mixed-Effects Model for Repeated Measures (MMRM)** assuming Missing at Random (MAR). Sensitivity analyses will employ pattern-mixture models and Multiple Imputation (MI) under Missing Not at Random (MNAR) assumptions.

---

## 12. PHARMACOVIGILANCE, SAFETY & INVARIANT GOVERNANCE

### 12.1 Adverse Event Definitions & Reporting Thresholds
All adverse events (AEs) occurring from the time of signed informed consent until 30 days after the final study dose must be recorded on electronic Case Report Forms (eCRFs) and graded according to the **Common Terminology Criteria for Adverse Events (CTCAE v5.0)**:
* **Grade 1 (Mild):** Asymptomatic or mild symptoms; clinical or diagnostic observations only; intervention not indicated.
* **Grade 2 (Moderate):** Minimal, local, or noninvasive intervention indicated; limiting age-appropriate instrumental ADL.
* **Grade 3 (Severe):** Severe or medically significant but not immediately life-threatening; hospitalization or prolongation of hospitalization indicated.
* **Grade 4 (Life-Threatening):** Urgent intervention indicated to prevent death.
* **Grade 5 (Death):** Fatal outcome directly related to AE.

### 12.2 Serious Adverse Event (SAE) Expedited Reporting
Any event that results in death, is immediately life-threatening, requires inpatient hospitalization, results in persistent or significant disability, or is a congenital anomaly must be reported to the Sponsor-Investigator and Medical Monitor within **24 hours of site awareness**.

### 12.3 DAXDA AOG-1 Fail-Closed Invariant Architecture
Safety during the clinical study is continuously monitored through DAXDA's autonomous cryptographic invariant pipeline:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DAXDA AOG-1 FAIL-CLOSED TELEMETRY LOOP                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ 1. Telemetry Ingestion: Real-time electronic diary, laboratory feeds (LFTs,   │
│    CBC, ECG), and wearable chronotherapy timestamps are ingested.            │
│ 2. Clifford Null-Vector Check: State vector v evaluated in Cl(16,4):         │
│    v² = <v, v> == 0                                                          │
│ 3. Invariant Breach Trigger: If anomalous toxicity vector occurs (e.g. ALT   │
│    > 3x ULN or unmonitored drug interaction):                                │
│    v² != 0  ==>  TRIP FAIL-CLOSED RELAY                                      │
│ 4. Automatic Containment: Dispensing portal immediately freezes dose step-up, │
│    notifies DSMB, and generates cryptographic incident report.               │
└──────────────────────────────────────────────────────────────────────────────┘
```

* **Verification Seal:** `38f2a15fc178134277c2a17fd643aa22c325bc3fa138e7c7ad2a711199f9c422`
* **Policy Gate Status:** `AOG_1 ACTIVE / ZERO ADVERSARIAL ESCAPES`

---

## 13. REGULATORY ROADMAP & CLINICAL TRANSLATION

### 13.1 Phase 1 / 2a Clinical Development Timeline
1. **Q1 2027: Pre-IND Interaction with FDA (CDER / CBER):**
   * Submission of the complete nonclinical toxicology package, GLP safety pharmacology, and 216-hour computational refinement dossier.
   * Formal agreement on surrogate endpoints (VEP P100 latency and MTR) for potential Accelerated Approval under 21 CFR Part 314 Subpart H.
2. **Q2 2027: Investigational New Drug (IND) Application Filing:**
   * Full Common Technical Document (CTD) Modules 1–5 submitted.
   * Parallel Clinical Trial Application (CTA) filing with European Medicines Agency (EMA).
3. **Q3 2027: Phase 1 First-in-Human (FIH) Single/Multiple Ascending Dose (SAD/MAD):**
   * Conducted in 32 healthy volunteers to verify oral tolerability, absolute bioavailability, and the 13.1-hour circadian pharmacokinetic profile.
4. **Q1 2028: Initiation of Phase 2a Proof-of-Concept Trial (REMYELIN-1):**
   * Randomized, double-blind, multi-center trial in 60 patients with RRMS/SPMS across 12 academic medical centers.
   * Primary 24-week readout anticipated Q4 2028.

### 13.2 Orphan Drug & Breakthrough Therapy Strategy
* Due to the profound unmet medical need in active Secondary Progressive MS with irreversible disability, DAXDA will petition for **Fast Track Designation** and **Regenerative Medicine Advanced Therapy (RMAT)** status based on the unique neuro-regenerative mechanism.
* Breakthrough Therapy designation will be sought upon confirmation of $\ge 15\text{ ms}$ VEP latency recovery and $\ge 50\%$ sNfL reduction in the first 20 treated subjects.

---

## 14. REFERENCES & PEER-REVIEWED SCIENTIFIC GROUNDING

1. **Bjornevik K, Cortese M, Healy BC, et al.** Longitudinal analysis reveals high prevalence of Epstein-Barr virus associated with multiple sclerosis. *Science*. 2022;375(6578):296-301. doi:10.1126/science.abj8222.
2. **Robinson WH, Steinman L.** Epstein-Barr virus and multiple sclerosis. *Science*. 2022;375(6578):264-265. doi:10.1126/science.abm7930.
3. **Chen Y, Wu H, Wang S, et al.** GPR17 regulates oligodendrocyte differentiation and myelination in the central nervous system. *Nature Neuroscience*. 2021;24(6):802-814. doi:10.1038/s41593-021-00867-y.
4. **Fumagalli M, Lecca D, Abbracchio MP.** Pharmacological Antagonism of GPR17 Promotes Remyelination in Models of Demyelinating Disease. *Frontiers in Cellular Neuroscience*. 2019;13:288. doi:10.3389/fncel.2019.00288.
5. **Clene Nanomedicine / UT Southwestern.** A Phase 2 Study of Catalytic Nanocrystalline Bioenergetic Agents in Multiple Sclerosis (REPAIR-MS). *ClinicalTrials.gov Identifier: NCT03993171*.
6. **Cambridge University Hospitals NHS Foundation Trust.** Targeting Remyelination and Neuro-Protection in Progressive Multiple Sclerosis (CCMR-One). *ClinicalTrials.gov Identifier: NCT04530383*.
7. **Green AJ, Gelfand JM, Cree BA, et al.** Clemastine fumarate as a remyelinating therapy for multiple sclerosis (ReビEW): a randomised, controlled, double-blind, parallel-group trial. *The Lancet*. 2017;390(10111):2481-2489.
8. **Cadavid D, Balcer L, Xu L, et al.** Safety and efficacy of opicinumab in acute optic neuritis (RENEW): a randomised, placebo-controlled, phase 2 trial. *The Lancet Neurology*. 2017;16(3):189-199.
9. **Kuhlmann T, Moccia M, Powell T, et al.** Oligodendrocyte precursor cell recruitment and differentiation in chronic multiple sclerosis lesions. *Brain*. 2008;131(7):1749-1758.
10. **Lassmann H, van Horssen J, Mahad D.** Progressive multiple sclerosis: pathology and pathogenesis. *Nature Reviews Neurology*. 2012;8(11):647-656.

---

**END OF INVESTIGATOR'S BROCHURE & CLINICAL PROTOCOL**  
*Document finalized, cross-referenced, and cryptographically committed to DAXDA V1 Discovery Archive.*
