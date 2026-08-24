# DAX 500 Court Casebook Final Evaluation Matrix

**Protocol ID:** DAX-PRED-LEGAL-500  
**Engine Lock:** DAXDA_V11.4_FROZEN  
**Protocol Hash:** `3654b7d544e05ee1c000c4615705b823b19aa2aae98d3a7ee99e083caca9a090`  
**Total Court Cases Evaluated:** 500  
**Permissible Final Verdict:** `DOMAIN-LIMITED PREDICTIVE SIGNAL`  

---

## 1. 500 Court Cases Comparative Performance

| Model / Baseline | Mean Brier Score | Log Loss | ECE | Top-1 Acc | Top-2 Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **DAXDA Frozen V11.4** | **0.579463** | **1.039123** | **0.1238** | **0.6** | **0.8** |
| Baseline 1 (Uniform Random) | 0.8 | 1.609438 | 0.0 | 0.2 | 0.4 |
| Baseline 2 (Historical Base Rate) | 0.589 | 1.070744 | 0.14 | 0.6 | 0.8 |
| Baseline 3 (Statistical Model) | 0.592536 | 1.053947 | 0.15152 | 0.6 | 0.784 |
| Baseline 4 (ML Classifier) | 0.585349 | 1.063195 | 0.132 | 0.6 | 0.8 |
| Baseline 5 (Frontier LLM) | 0.57484 | 1.047744 | 0.0899 | 0.6 | 0.8 |

---

## 2. 10 Legal Subject Areas Evaluated (50 Cases Each)

1. **Civil Procedure**: Personal jurisdiction, Pleading standards, Erie doctrine, Summary judgment, Class action certification.
2. **Constitutional Law**: Judicial review, Commerce clause limits, Equal protection, Substantive due process, Executive immunity.
3. **Contracts**: Objective theory of assent, Consideration, Promissory estoppel, Parol evidence, Consequential damages.
4. **Torts**: Intentional battery, Negligence duty/proximate cause, Alternative liability, Products liability, Defamation actual malice.
5. **Criminal Law & Procedure**: Actus reus/mens rea, Necessity, 4th Amendment search/seizure, 5th Amendment Miranda, 6th Amendment right to counsel.
6. **Property Law**: First possession, Adverse possession, Habitability, Eminent domain takings, Copyright originality.
7. **Corporate & Securities Law**: Business judgment rule, Antitakeover defenses, Securities fraud 10b-5, Insider trading tippee liability, Section 220 inspection.
8. **Evidence Law**: Rule 403 balancing, Hearsay exceptions, Daubert expert gatekeeping, Attorney-client privilege, Rule 404(b) propensity.
9. **Administrative Law**: Agency deference, Arbitrary/capricious review, Lujan standing, Procedural due process, Non-delegation doctrine.
10. **Intellectual Property**: Fair use transformation, Patentable subject matter § 101, Likelihood of confusion, Trade secrets, Trade dress.
