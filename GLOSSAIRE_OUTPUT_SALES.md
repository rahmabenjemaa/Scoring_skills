# 📋 GLOSSAIRE - GUIDE D'EXPLICATION DE L'OUTPUT
## Pour l'Équipe Commerciale

---

## 🎯 Vue d'Ensemble
Ce document explique chaque colonne et métrique du fichier `ranked_jobs_output.csv` - le fichier contenant les opportunités d'emploi classées et notées par notre système IA.

---

## 📊 COLONNES DU FICHIER OUTPUT

### 1. **title** (Titre du poste)
- **Définition**: Le titre du poste d'emploi
- **Exemple**: "Staff Data Engineer", "Senior ML Engineer"
- **Utilité**: Identifier rapidement le type de poste
- **Conseil sales**: Vérifier que le titre correspond aux ambitions du candidat

---

### 2. **company_name** (Nom de l'entreprise)
- **Définition**: Nom de l'entreprise qui recrute
- **Exemple**: "PrizePicks", "TechCorp AI"
- **Utilité**: Identifier l'employeur et sa notoriété
- **Conseil sales**: Utiliser pour personnaliser l'approche commerciale par entreprise

---

### 3. **location** (Localisation)
- **Définition**: Localisation géographique du poste
- **Exemple**: "Remote, OR", "Paris", "Île-de-France"
- **Utilité**: Filtrer par zone géographique
- **Conseil sales**: Vérifier la compatibilité avec les contraintes du candidat (télétravail, déplacement, etc.)

---

### 4. **source** (Source d'annonce)
- **Définition**: Plateforme d'où provient l'annonce
- **Exemple**: "Indeed", "LinkedIn", "Glassdoor"
- **Utilité**: Tracer l'origine de chaque opportunité
- **Conseil sales**: Adapter le message selon le contexte de la source

---

### 5. **description** & **full_text** (Descriptions complètes)
- **Définition**: Texte intégral de l'annonce d'emploi
- **Utilité**: Analyser les détails du poste, les responsabilités et exigences
- **Conseil sales**: Source de base pour les discussions de qualification

---

### 6. **job_highlights** (Points forts du poste)
- **Définition**: Caractéristiques principales mises en évidence
- **Exemple**: "Remote work", "Fast-growing company", "Competitive salary"
- **Utilité**: Résumer rapidement les avantages du poste
- **Conseil sales**: Utiliser pour le "pitch" commercial

---

### 7. **schedule_type** (Type de planning)
- **Définition**: Type d'horaire/contrat du poste
- **Exemple**: "Full-time", "Part-time", "Contract"
- **Utilité**: Vérifier la compatibilité avec les préférences du candidat
- **Conseil sales**: Point de négociation potentiel

---

### 8. **qualifications** (Qualifications requises)
- **Définition**: Prérequis et compétences demandées
- **Exemple**: "5+ years experience in Python", "AWS certified"
- **Utilité**: Vérifier l'alignement avec le profil du candidat
- **Conseil sales**: Identifier les écarts de compétences à adresser

---

### 9. **apply_options** (Options de candidature)
- **Définition**: Moyens pour postuler et contacts
- **Utilité**: Faciliter la mise en relation
- **Conseil sales**: Vérifier si contact direct possible ou via plateforme

---

## 🎯 LES SCORES - LES MÉTRIQUES CLÉS

> **Les scores vont de 0 à 1 (ou 0% à 100%)**
> - **0.0** = Pas du tout adapté
> - **0.5** = Modérément adapté
> - **1.0** = Parfaitement adapté

### **pre_score** (Score de pré-filtrage)
**Responsable**: Système de qualification initial

#### Qu'est-ce que c'est ?
Résultat du filtre d'élimination automatique qui détermine si l'annonce mérite d'être analysée plus profondément.

#### Valeurs possibles:
- **0** = Annonce rejetée (ne correspond pas aux critères minimums)
- **1** = Annonce qualifiée (passe à la phase de scoring détaillée)

#### Critères d'élimination appliqués:
- S'il s'agit d'une source autorisée (ex: Indeed)
- Si le texte contient des informations minimales (durée suffisante)
- Filtres géographiques ou sectoriels basiques

#### 💡 Utilité pour les sales:
- Les annonces avec `pre_score = 0` sont **ignorées** (déjà filtrées)
- Les annonces avec `pre_score = 1` **entrent en analyse détaillée**

---

### **skill_score** (Score de correspondance des compétences)
**Responsable**: Moteur de matching des compétences IA

#### Qu'est-ce que c'est ?
Mesure du pourcentage de compétences du CV du candidat présentes dans l'annonce.

#### Calcul simplifié:
```
Compétences du CV trouvées dans l'annonce / Total des compétences du CV
```

#### Exemple:
- CV du candidat: Python, SQL, AWS, Spark (4 compétences)
- Annonce demande: Python, SQL, Tableau
- Compétences en commun: Python, SQL (2 compétences)
- **Skill Score = 2/4 = 0.5**

#### Interprétation:
| Score | Signification |
|-------|---------------|
| 0.0 - 0.2 | Très peu de compétences en commun ❌ |
| 0.3 - 0.5 | Compétences partielles ⚠️ |
| 0.6 - 0.8 | Bonne correspondance ✅ |
| 0.9 - 1.0 | Correspondance excellente 🌟 |

#### 💡 Utilité pour les sales:
- **Score bas?** Vérifier si le candidat peut apprendre rapidement
- **Score haut?** Mettre en avant la **compatibilité immédiate**
- C'est le signal le plus direct du "fit technique"

---

### **semantic_score** (Score de pertinence sémantique)
**Responsable**: Modèle IA de compréhension du langage (SentenceTransformers)

#### Qu'est-ce que c'est ?
Mesure de la **similarité conceptuelle** entre le profil du candidat et le job, au-delà des mots clés simples.

#### Fonctionnement:
- On extrait le "sens" du CV du candidat
- On extrait le "sens" de l'annonce
- On compare les deux concepts (même si les mots sont différents)

#### Exemples où semantic_score joue:
✅ CV dit "gestion de bases de données relationnelles" → Annonce dit "SQL expertise"  
✅ CV dit "consulting IT" → Annonce dit "solution architect"  
✅ CV dit "équipe agile" → Annonce dit "DevOps & collaboration"

#### Interprétation:
| Score | Signification |
|-------|---------------|
| 0.0 - 0.3 | Concepts très différents ❌ |
| 0.4 - 0.6 | Quelques concepts alignés ⚠️ |
| 0.7 - 0.85 | Concepts bien alignés ✅ |
| 0.86 - 1.0 | Alignement conceptuel quasi-parfait 🌟 |

#### 💡 Utilité pour les sales:
- Détecte les **transferts de compétences** possibles
- Montre si le candidat comprendra le **contexte métier**
- Excellent pour justifier des postes "pas exactement le même titre"

---

### **cross_score** (Score de ré-classement Cross-Encoder)
**Responsable**: Modèle de ré-classement avancé (Cross-Encoder ML)

#### Qu'est-ce que c'est ?
Score d'un modèle IA **plus sophistiqué** qui analyse ENSEMBLE le CV et l'annonce, pour donner un jugement global de qualité du match.

#### Pourquoi "Cross-Encoder" ?
- Bi-Encoder = comparer deux choses séparément ➡️ rapide mais moins nuancé
- Cross-Encoder = analyser les deux ensemble ➡️ plus lent mais plus intelligent

#### Qu'est-ce qu'il détecte ?
- Les **interactions subtiles** entre le profil et le poste
- Les **contrastes** (ex: excellentes skills mais niveau seniority pas bon)
- Les **opportunités d'apprentissage** (junior en montée?)
- La **cohérence globale** du match

#### Interprétation:
| Score | Signification |
|-------|---------------|
| 0.0 - 0.3 | Match pas recommandé ❌ |
| 0.4 - 0.6 | Match possible selon le candidat ⚠️ |
| 0.7 - 0.85 | Très bon match ✅ |
| 0.86 - 1.0 | Match exceptionnel 🌟 |

#### 💡 Utilité pour les sales:
- **Le score le plus "intelligent"** - capture la nuance
- Bon pour les **décisions difficiles** (quand d'autres scores sont mitigés)
- Valider si une candidature "contre-intuitive" peut fonctionner

---

### **final_score** (Score final - LE SCORE CLEF!)
**Responsable**: Combinaison pondérée des trois scores ci-dessus

#### Qu'est-ce que c'est ?
**L'indicateur principal** qui classe les annonces. C'est LE score à surveiller.

#### Calcul:
```
Final Score = (40% × skill_score) + (30% × semantic_score) + (30% × cross_score)
```

#### Pondérations expliquées:
- **40% Skill Score** = Les compétences techniques sont les plus importantes
- **30% Semantic Score** = La pertinence conceptuelle compte
- **30% Cross Score** = L'intelligence globale affine le jugement

#### Interprétation (guide de référence):
| Score | Signification | Action recommandée |
|-------|---------------|-------------------|
| 0.0 - 0.40 | Match faible | ❌ Ne pas proposer |
| 0.41 - 0.60 | Match modéré | ⚠️ Proposer si intéressé (risque d'inadéquation) |
| 0.61 - 0.80 | Bon match | ✅ Proposer en priorité |
| 0.81 - 1.0 | Excellent match | 🌟 Proposer d'urgence (top opportunity) |

#### 💡 Utilité pour les sales:
- **C'est votre métrique d'efficacité** - proposez les jobs avec final_score élevé
- **Score bas?** L'IA dit "ce n'est probablement pas adapté"
- **Score élevé?** L'IA dit "très bonne opportunité"
- Justifier votre démarche commerciale avec des scores objectifs

---

## 🎁 BONUS: CAS D'USAGE TYPIQUES POUR LES SALES

### Cas 1: "Ce job m'intéresse mais les skills ne correspondent pas"
```
Exemple: skill_score = 0.45, semantic_score = 0.80, cross_score = 0.72, final_score = 0.63
→ Le job a du potentiel! Le candidat peut apprendre les skills manquantes?
→ Vérifier: est-ce un growth opportunity ou un risque?
```

### Cas 2: "Excellente annonce de rêve"
```
Exemple: skill_score = 0.95, semantic_score = 0.92, cross_score = 0.88, final_score = 0.91
→ TOP PRIORITY! Passer à l'action immédiatement
→ Risque: forte concurrence - présenter le candidat en urgence
```

### Cas 3: "Pourquoi ce score est bas?"
```
Si final_score est bas mais skill_score est correct:
→ Probablement semantic_score ou cross_score est faible
→ Le "fit global" n'est pas bon (domaine différent, niveau seniority différent, etc.)
```

### Cas 4: "Exécuter rapidement sur les top scores"
```
Triez par final_score (descendant)
- Top 20%: Votre meilleures opportunités
- Entre 60-80%: Bonnes propositions
- En dessous 40%: À exclure de votre pipeline
```

---

## 📈 STRATÉGIE RECOMMANDÉE POUR LES SALES

### 1️⃣ **Phase de Qualification Rapide**
- Filtrer sur `final_score > 0.65`
- Triez par score décroissant
- Commencez par les top 3-5

### 2️⃣ **Phase de Personnalisation**
- Si `skill_score` bas mais `semantic_score` haut:
  - **Message**: "Rôle différent mais excellente transition"
  - Insister sur l'apprentissage rapide possible
  
- Si tous les scores sont hauts:
  - **Message**: "Match IA quasi-parfait"
  - Créer urgence (présenter rapidement)
  
- Si `semantic_score` bas:
  - **Message**: "Domaine nouveau"
  - Évaluer les ambitions cachées du candidat

### 3️⃣ **Phase de Suivi**
- Tracker le taux de conversion par**fourchette de final_score**
- Ajuster le seuil de final_score selon vos résultats réels
- Partager les "succès/échecs" pour améliorer le système

---

## ❓ FAQ - QUESTIONS FRÉQUENTES

### Q: "Quel score minimum dois-je proposer?"
**A**: Recommandé: `final_score > 0.60`
- 0.60-0.70: Bonne opportunité, mais risque d'inadéquation
- 0.70+: Forte recommandation

### Q: "Pourquoi skill_score bas mais final_score correct?"
**A**: Parce que semantic_score + cross_score compensent. Le contexte global est bon même si les skills exacts ne correspondent pas.

### Q: "Dois-je ignorer un job avec low skill_score?"
**A**: Pas nécessairement! Si semantic_score + cross_score sont élevés, c'est une vraie opportunité d'apprentissage pour le candidat.

### Q: "Comment expliquer un score au candidat?"
**A**: 
- Skill Score = "Vos compétences techniques correspondent à X%"
- Semantic Score = "Votre profil conceptuel match avec ce rôle à X%"
- Cross Score = "Le jugement IA global dit que c'est une bonne opportunité (X%)"
- Final Score = "Score global: si > 0.70, c'est une très bonne opportunité!"

### Q: "Les scores peuvent-ils être faux?"
**A**: Oui, occasionnellement. L'IA n'est pas parfaite. Toujours appliquer votre jugement commercial:
- Vérifier les détails manuellement
- Ne pas proposer uniquement parce que le final_score est haut
- Utiliser l'IA comme guide, pas comme oracle

---

## 📞 CONTACT / SUPPORT
Pour questions sur la méthodologie ou sur un score spécifique:
- Contactez l'équipe IA/Data
- Incluez le job_id ou le row number du ranked_jobs_output.csv

---

**Dernière mise à jour**: Mars 2026  
**Version**: 1.0 - Sales Ready
