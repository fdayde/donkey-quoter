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

# Modèle Claude à utiliser
CLAUDE_MODEL=claude-3-haiku-20240307

# Limites de tokens
MAX_TOKENS_INPUT=200
MAX_TOKENS_OUTPUT=100

# Limites d'utilisation
SESSION_LIMIT=10
DAILY_LIMIT=10
```

## Architecture

### Modules principaux

- **`claude_api.py`** : Client pour l'API Claude
- **`api_limiter.py`** : Gestion des limites (10/session, 10/jour)
- **`haiku_storage.py`** : Stockage persistant des haïkus
- **`haiku_generator.py`** : Logique de génération avec fallback

### Flux de génération

1. L'utilisateur clique sur "Créer un haïku"
2. Vérification des limites d'usage
3. Si OK → Appel API Claude → Stockage du haïku
4. Si limite atteinte → Utilisation d'un haïku stocké
5. Affichage du compteur d'usage

## Utilisation

### Interface utilisateur

- **Bouton "Créer un haïku"** : Génère un haïku pour la citation courante
- **Bouton "Régénérer"** : Apparaît quand un haïku est affiché, force une nouvelle génération
- **Compteur d'usage** : Affiche les générations restantes (session/jour)

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

Les compteurs sont stockés dans `data/api_limits.json` :

```json
{
  "2024-03-20": 5
}
```

## Comportement sans API

Si la clé API n'est pas configurée :
- Utilisation des haïkus pré-générés uniquement
- Pas de compteur d'usage affiché
- Pas de bouton "Régénérer"

## Coûts estimés

Avec Claude 3 Haiku :
- ~0.001$ par génération
- Limite quotidienne de 10 = max 0.01$/jour
- Réutilisation des haïkus stockés = coûts réduits
