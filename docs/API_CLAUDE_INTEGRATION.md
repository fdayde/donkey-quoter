# Intégration API Claude pour génération de haïkus

Cette documentation décrit la nouvelle fonctionnalité de génération de haïkus personnalisés via l'API Claude.

## Vue d'ensemble

Le système génère maintenant des haïkus personnalisés pour chaque citation en utilisant Claude Haiku. Les haïkus sont stockés et réutilisés pour optimiser les coûts.

## Configuration

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Configuration de l'API

Créez un fichier `.env` à la racine du projet (basé sur `.env.example`) :

```env
# Configuration API Claude
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...

# Modèle Claude à utiliser (claude-3-haiku-20240307 ou claude-3-5-haiku-20241022)
CLAUDE_MODEL=claude-3-haiku-20240307

# Limites de tokens
MAX_TOKENS_INPUT=200
MAX_TOKENS_OUTPUT=100

# (Optionnel) Tier API Anthropic (1, 2, 3, 4, ou 5)
# Utilisé pour optimiser le throttling de count_tokens()
# Si non spécifié, utilise des limites conservatrices (Tier 1)
ANTHROPIC_TIER=1
```

## Architecture

### Modules principaux

- **`claude_api.py`** : Client pour l'API Claude
- **`haiku_storage.py`** : Stockage persistant des haïkus
- **`haiku_generator.py`** : Logique de génération avec fallback et gestion des limites

### Flux de génération

1. L'utilisateur clique sur "Créer un haïku"
2. Vérification de la limite de session (5 générations)
3. Si OK → Appel API Claude → Stockage du haïku
4. Si limite atteinte → Utilisation d'un haïku stocké
5. Affichage du compteur d'usage

## Utilisation

### Interface utilisateur

- **Bouton "Créer un haïku"** : Génère un haïku pour la citation courante
- **Compteur d'usage** : Affiche les générations restantes (limite de session : 5)

### Génération automatique

- Lors de l'ajout d'une nouvelle citation, un haïku est généré automatiquement
- Si la limite est atteinte, la génération est reportée

### Script batch

Pour générer des haïkus pour toutes les citations :

```bash
# Générer pour toutes les langues
python scripts/generate_missing_haikus.py

# Limiter à 5 générations
python scripts/generate_missing_haikus.py --limit 5

# Générer uniquement en français
python scripts/generate_missing_haikus.py --languages fr
```

## Données

### Stockage des haïkus

Les haïkus sont stockés dans `data/haikus.json` :

```json
{
  "c1": {
    "fr": ["Haïku 1 en français", "Haïku 2 en français"],
    "en": ["Haiku 1 in English", "Haiku 2 in English"]
  }
}
```

### Limites d'usage

La limite de session est gérée via `st.session_state.haiku_generation_count` (maximum 5 générations par session).

## Comportement sans API

Si la clé API n'est pas configurée :
- Utilisation des haïkus pré-générés uniquement
- Pas de compteur d'usage affiché

## Optimisation et coûts

### Script de régénération optimisé

Le script `regenerate_haikus.py` utilise une approche de "pseudo-batch" qui groupe 5 citations par appel API :
- Génération bilingue simultanée (FR + EN)
- Réduction significative du nombre d'appels API
- Économies estimées : ~30% vs génération individuelle

### Comptage précis des tokens

Pour améliorer la précision des estimations, le script utilise l'API `count_tokens()` d'Anthropic :

#### Avantages
- **Gratuit** : Aucun coût supplémentaire
- **Précision parfaite** : Compte exact des tokens au lieu d'estimations
- **Optimisation `max_tokens`** : Évite de réserver trop de tokens inutilement

#### Gestion des limites de débit

L'API `count_tokens()` a des limites par tier :
- Tier 1 : 100 appels/minute
- Tier 2 : 1 000 appels/minute
- Tier 3+ : 2 000+ appels/minute

Le système utilise un compteur intelligent :
```python
# Vérifie si on peut appeler count_tokens()
if counter.can_count_tokens():
    token_count = client.messages.count_tokens(messages)
else:
    # Fallback vers estimation simple
    token_count = len(prompt) // 4
```

#### Mécanismes de protection
- **Throttling préventif** : Limite à 80% du quota pour éviter les erreurs
- **Reset automatique** : Compteur réinitialisé chaque minute
- **Fallback gracieux** : Utilise les estimations si limite atteinte
- **Retry automatique** : Le SDK gère les erreurs 429 avec backoff exponentiel

### Pourquoi pas le batch processing d'Anthropic ?

Bien que l'API d'Anthropic offre un vrai batch processing avec 50% de réduction, nous ne l'utilisons pas car :

1. **Volume modeste** : 51 citations seulement = ~10 batchs avec l'approche actuelle
2. **Coût total négligeable** : ~0.02$ pour régénérer toutes les citations
3. **Délai inacceptable** : Le batch processing peut prendre jusqu'à 24h
4. **Usage occasionnel** : Les régénérations massives sont rares
5. **Complexité injustifiée** : L'implémentation nécessiterait un système de suivi des jobs

Notre approche actuelle offre le meilleur équilibre entre optimisation des coûts et simplicité d'implémentation.

### Coûts estimés

Avec Claude 3 Haiku ou Claude 3.5 Haiku :
- ~0.001$ par génération
- Limite de session de 5 = max 0.005$/session
- Réutilisation des haïkus stockés = coûts réduits
