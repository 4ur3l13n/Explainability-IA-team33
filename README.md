# AttritionIQ - Offre SaaS conceptuelle

Ce document décrit la proposition de valeur, le parcours client, les aspects cyber et RGPD, la tarification, la roadmap, les contraintes et le plan de déploiement pour une solution SaaS de prédiction du turnover, basée sur le prototype local existant.

## Objectifs
- Prédire le turnover des salariés avec un modèle de machine learning explicable.
- Protéger les PII en traitant les données sensibles localement chez le client.
- Fournir des tableaux de bord SaaS anonymisés pour aider la DSI/RH à prioriser les actions.

## Scope
- In scope : pipeline local (ingestion, preprocessing, entraînement), export de features + hash, monitoring SaaS, conformité RGPD/NIS2, architecture data residency UE.
- Out of scope V1 : stockage de PII dans le cloud, intégration native avec SIRH, identification directe des employés, utilisation de données non-hachées.

## Instructions
### Prérequis (MVP local 2 jours)
- Python 3.10+ installé (ou version 3.11). 
- Docker (optionnel pour containers) ou environnement venv local.
- Accès au dataset CSV d’exemple (fichier `data/HRDataset_v14.csv` fourni dans ce dépôt).
- Connexion Internet pour installer dépendances.

### Installation
1. Cloner le dépôt :
   - `git clone <repo-url>`
   - `cd attrition-fixed`
2. Créer un environnement Python :
   - `python -m venv .venv`
   - `source .venv/Scripts/activate` (Windows) ou `source .venv/bin/activate` (Linux/Mac)
3. Installer les dépendances :
   - `pip install -r backend/requirements.txt`

### Exécution
- Pour lancer l’ingestion et entraîner le modèle local :
  - `python backend/main.py` (ou `python backend/model/train.py` selon implémentation).
- Pour servir un dashboard local (s’il existe, ex. Streamlit) :
  - `streamlit run frontend/src/App.jsx` ou `python backend/app.py`.

---

## 1) Présentation du persona

### 1.1 Notre entreprise (AttritionIQ)
- Positionnement : solution SaaS de prediction de turnover + analytics RH.
- Cible : PME/ETI (200 - 5 000 salariés), industries à forte rotation (logistique, santé, finance, manufacturing, services), France/UE.
- ADN : privacy-first, confidentialité, compliance RGPD, traitement local des données sensibles.

### 1.2 Client cible
- Acteurs RH + Data Science + DSI à enjeux de rétention du personnel.
- Objectif : prédire et réduire l’attrition, augmenter le bien-être au travail.
- Besoins : contrôle sur les données sensibles, modèle explicable, conformité RGPD.

---

## 2) Parcours utilisateur (processus type)

1. Qualification initiale via contact commercial.
2. Audit technique et conformité (données disponibles, variables, sensibilités).
3. POC local côté client (Infrastructure on-premise) :
   - Ingestion du dataset.
   - Préprocessing + entraînement modèle.
   - Export des colonnes de modèle + hash salarié.
4. Transmission vers SaaS via canal sécurisé (TLS, chiffrement, protocole signé).
5. Exploitation dans la plateforme SaaS : dashboards, scoring, alertes.
6. Déploiement production et suivi (MCO, support, KPI mensuels).

---

## 3) Architecture data et anonymisation

- Traitement local des données brutes.
- Export autorisé : variables métier utiles au modèle, identifiants pseudonymisés (hashs SHA-256 + salt).
- Interdiction d’envoyer des PII (nom, prénom, NIR, email, etc.).
- audit et logs : enregistrement de toutes les opérations de transformation / transfert.

---

## 4) Tailles géographiques et régulations

### Zone prioritaire
- France + UE.
- Avantages : RGPD, régulation claire, marché exigeant protection des données.

### Régulations clé
- RGPD (minimisation des données, privacy by design, DPIA).
- NIS2, ISO 27001, CNIL, LPM, data residency (EU-only).
- Attention Cloud Act : éviter stockage direct de données vers US. Clause contractuelle standard (SCC) si transfert hors UE.

---

## 5) Focus cybersécurité

- IAM : MFA, RBAC, least privilege.
- Chiffrement : AES-256 at rest, TLS1.2+ in transit.
- Processus : pentest, tests d’intrusion, vulnérabilité régulière, SOC.
- Collecte : uniquement données anonymisées possibles pour l’analyse globale.

---

## 6) Méthodologie / conformité selon pays

- France : Références DPO, CNIL, registre traitement, charte RH.
- Allemagne : BDSG + Datenschutz-Folgenabschätzung.
- Suisse/UK : règles locales dérivées + assurances.
- Cadence standard : inventaire, classification, pseudo/anonymisation, audit, gouvernance.

---

## 7) Objectifs de développement

### MVP (prototype local 2 jours)
- Ingestion CSV + preprocessing.
- Modèle prédictif (XGBoost/LightGBM).
- Module d’export minimal (features + employee_hash).
- Dashboard local basique.

### V1 (SaaS)
- Onboarding client.
- Architecture multi-tenant ou single-tenant avec data residency.
- API d’envoi sécurisé (HTTPS + auth token).
- Base de données analytics.
- Module explicabilité (SHAP-like).

### V2
- Benchmarks anonymisés multi-client.
- Recommandation et plan d’action RH.
- Monitoring en temps réel, alerting, incident management.

---

## 8) Plan séquencé commercial / opérationnel

1. Pré-vente : démo, RFI/RFP, workshop.
2. Contrat : NDA, SLA, clauses texte RGPD, garanties.
3. Installation : déploiement / configuration (cloud EU, ou mode hybride local/SaaS).
4. Formation + runbook.
5. Mise en production.
6. Support, suivi et évolution.

---

## 9) Tarification

### Frais d’installation initiaux
- 15 000 - 25 000 EUR (audit, paramétrage, formation, 3 mois d’accompagnement).

### Licence SaaS annuelle
- Pack standard : 8 000 EUR/an + 1 EUR/salarié/mois (200-2 000 salariés).
- Pack avancé : 15 000 EUR/an + 1,5 EUR/salarié/mois (recos, monitoring avancé).
- Option cybersécurité : 5 000 EUR/an (audit, conformité, rapport).
- Support premium 24/7 : 2 000 EUR/mois.
- Réentraînement modèle trimestriel : 2 000 EUR/trimestre.

---

## 10) Plus-values différenciantes

- Données sensibles restent chez le client, externe uniquement pseudo/anonymes.
- Conception privacy by design.
- Accompagnement conformité RGPD + sécurité.
- Rapidité de MVP (2 jours) puis production SaaS (3-6 mois).

---

## 11) Contraintes

- Qualité des données côté client.
- Risques de ré-identification malgré pseudonymisation (à gérer contractuellement).
- Nécessité d’un DPO et d’un pilote métier.
- Limitation si clients imposent localisation hors UE.
- Simulation locale ne couvre pas encore toutes les exigences d’une production SaaS multi-tenant.

---

## 12) Messages clés à porter

- "On ne touche pas aux données personnelles des employés."
- "Stratégie cyber d’abord, code ensuite."
- "Pas de stockage Cloud act direct pour l’offre UE."
- "Procédure : vente → RFP → déploiement → suivi."
- "Prototype local possible en 2 jours, SaaS complet en 3-6 mois."

---

## 13) Annexes

- Architecture proposée (local + SaaS).
- Schéma de flux de données (hachage + export non-PII).
- Liste des variables à ne jamais exporter.
- Exemple de plan de montée en charge.

---

## 14) Étapes suivantes suggérées

1. Document technique détaillé (chemin de données, API, standards).
2. Cahier des charges sécurité + compliance.
3. Maquette fonctionnelle front + backend.
4. Revue juridique (RGPD/CloudAct).
5. POC client pilote.
