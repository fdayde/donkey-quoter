# FEATURES_AUDIT.md - Audit exhaustif des fonctionnalités existantes

## 📋 Vue d'ensemble
Ce document liste TOUTES les fonctionnalités actuelles de Donkey Quoter avant refactoring pour garantir qu'aucune ne sera perdue.

---

## 🎯 Fonctionnalités Quote (Gestion des Citations)

### QuoteAdapter (`src/donkey_quoter/core/quote_adapter.py`)
| Fonctionnalité | Méthode/Propriété | Dépendances | Utilisée |
|---|---|---|---|
| **Gestion des données quotes** | `quotes` (property) | `st.session_state` | OUI |
| **Citation courante** | `current_quote` (property/setter) | `st.session_state` | OUI |
| **Citations sauvegardées** | `saved_quotes` (property) | `st.session_state` | OUI |
| **Poèmes sauvegardés** | `saved_poems` (property) | `st.session_state` | OUI |
| **Citation originale** | `original_quote` (property/setter) | `st.session_state` | OUI |
| **Obtenir texte localisé** | `get_text(text_dict, language)` | QuoteService | OUI |
| **Ajouter citation** | `add_quote(quote_input, language)` | QuoteService | NON |
| **Mettre à jour citation** | `update_quote(quote_id, quote_input, language)` | QuoteService | NON |
| **Supprimer citation** | `delete_quote(quote_id)` | QuoteService | NON |
| **Citation aléatoire** | `get_random_quote()` | QuoteService | OUI |
| **Sauvegarder citation courante** | `save_current_quote()` | QuoteService | OUI |
| **Sauvegarder poème courant** | `save_current_poem()` | QuoteService | OUI |
| **Export données sauvegardées** | `export_saved_data()` | QuoteService | OUI |

### QuoteService (`src/donkey_quoter/core/quote_service.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Texte localisé** | `get_text(text_dict, language)` | Aucune | OUI |
| **Citation aléatoire** | `get_random_quote(quotes)` | `random` | OUI |
| **Filtrage par catégorie** | `filter_by_category(quotes, category)` | Aucune | NON |
| **Filtrage par type** | `filter_by_type(quotes, quote_type)` | Aucune | NON |
| **Créer quote depuis input** | `create_quote_from_input(quote_input, language)` | `datetime` | OUI |
| **Mettre à jour quote** | `update_quote_from_input(quote, quote_input, language)` | Aucune | NON |
| **Trouver quote par ID** | `find_quote_by_id(quotes, quote_id)` | Aucune | OUI |
| **Supprimer quote par ID** | `remove_quote_by_id(quotes, quote_id)` | Aucune | OUI |
| **Ajouter quote à liste** | `add_quote_to_list(quotes, quote)` | Aucune | OUI |
| **Vérifier présence quote** | `is_quote_in_list(quotes, quote)` | Aucune | OUI |
| **Ajouter si inexistant** | `add_quote_if_not_exists(quotes, quote)` | Aucune | OUI |
| **Export JSON** | `export_quotes_to_json(saved_quotes, saved_poems)` | `json`, `datetime` | OUI |

### DataLoader (`src/donkey_quoter/core/data_loader.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Chemin quotes par défaut** | `get_default_quotes_path()` | `Path` | OUI |
| **Charger quotes JSON** | `load_quotes(file_path)` | `json`, Quote | OUI |
| **Sauvegarder quotes** | `save_quotes(quotes, file_path)` | `json`, Quote | NON |

---

## 🎨 Fonctionnalités Haiku (Génération de Poésie)

### HaikuAdapter (`src/donkey_quoter/core/haiku_adapter.py`)
| Fonctionnalité | Méthode/Propriété | Dépendances | Utilisée |
|---|---|---|---|
| **Vérifier clé API** | `has_api_key` (property) | AnthropicClient | OUI |
| **Peut générer haiku** | `can_generate_haiku()` | HaikuService | OUI |
| **Générer haiku pour quote** | `generate_haiku_for_quote(quote, language, force_new)` | HaikuService, DataStorage | OUI |
| **Récupérer haiku stocké** | `get_stored_haiku_for_quote(quote, language)` | DataStorage | OUI |
| **Vérifier haiku existant** | `has_stored_haiku(quote, language)` | DataStorage | OUI |
| **Compteur génération** | `get_generation_count()` | `st.session_state` | OUI |
| **Générations restantes** | `get_remaining_generations()` | `st.session_state` | OUI |
| **Reset compteur** | `reset_generation_count()` | `st.session_state` | NON |
| **Affichage usage** | `get_usage_display(language)` | `st.session_state` | OUI |
| **Haiku existant (alias)** | `get_existing_haiku(quote, language)` | DataStorage | OUI |
| **Générer depuis quote (alias)** | `generate_from_quote(quote, language, force_new)` | HaikuService | OUI |

### HaikuService (`src/donkey_quoter/core/haiku_service.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Peut générer nouveau** | `can_generate_new_haiku(generation_count)` | Aucune | OUI |
| **Générer via API** | `generate_via_api(quote_text, quote_author, language)` | AnthropicClient, prompts | OUI |
| **Formater haiku** | `_format_haiku(haiku_text)` | Aucune | OUI |
| **Récupérer haiku stocké** | `get_stored_haiku(quote_id, language)` | DataStorage | OUI |
| **Haiku de fallback** | `get_fallback_haiku(language)` | `random` | OUI |
| **Créer Quote haiku** | `create_haiku_quote(haiku_text, language, model, source_quote_id)` | Quote, `datetime`, settings | OUI |
| **Stratégie génération** | `generate_haiku_strategy(quote, language, force_new, generation_count)` | Toutes les méthodes | OUI |

### HaikuManager (`src/donkey_quoter/core/haiku_manager.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Quotes pour batch** | `get_quotes_for_batch(regenerate_all)` | DataLoader | OUI (CLI) |
| **Génération batch** | `generate_batch(quotes)` | AnthropicClient | OUI (CLI) |
| **Estimation coût** | `calculate_cost_estimate(quote_count)` | TokenCounter | OUI (CLI) |
| **Statistiques** | `get_statistics()` | DataStorage | OUI (CLI) |
| **Export données** | `export_data(format_type)` | DataStorage | OUI (CLI) |

---

## 🖥️ Fonctionnalités UI (Interface Utilisateur)

### Pages principales (`src/donkey_quoter/ui/pages.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Afficher citation courante** | `render_current_quote(quote_manager, lang, t)` | QuoteAdapter, styles | OUI |
| **Boutons d'action** | `render_action_buttons(quote_manager, haiku_generator, lang, t)` | Adapters, StateManager | OUI |
| **Liste toutes citations** | `render_all_quotes_list(quote_manager, lang, t)` | QuoteAdapter, StateManager | OUI |

### Composants UI (`src/donkey_quoter/ui_components.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Badge catégorie** | `render_category_badge(category, lang)` | translations, styles | OUI |
| **Carte statistiques** | `render_stats_card(value, label, style_class)` | Aucune | NON |
| **Bouton d'action** | `render_action_button(label, key, on_click, disabled, use_container_width)` | streamlit | NON |
| **En-tête application** | `render_header(title, subtitle, lang, on_language_change)` | styles | OUI |
| **Élément liste quotes** | `render_quote_list_item(quote, lang, quote_text, quote_author, on_display, on_delete)` | Quote, styles | OUI |

### Styles UI (`src/donkey_quoter/ui/styles.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Style en-tête** | `get_header_style(title, subtitle)` | Aucune | OUI |
| **HTML badge catégorie** | `get_category_badge_html(category_label, category)` | settings | OUI |
| **HTML affichage quote** | `get_quote_display_html(quote_text, quote_author)` | Aucune | OUI |
| **HTML quote originale** | `get_original_quote_html(original_text, original_author, label)` | Aucune | OUI |
| **HTML élément liste** | `get_quote_list_item_html(quote_text, quote_author)` | Aucune | OUI |
| **HTML compteur usage** | `get_usage_display_html(usage_display)` | Aucune | OUI |
| **HTML footer** | `get_footer_html(version, contribute_message)` | Aucune | OUI |

### Composants CLI (`src/donkey_quoter/ui/cli_display.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Afficher erreur** | `print_error(message)` | Aucune | OUI (CLI) |
| **Afficher succès** | `print_success(message)` | Aucune | OUI (CLI) |
| **Afficher progrès** | `print_progress(current, total, message)` | Aucune | OUI (CLI) |
| **Afficher statistiques** | `print_stats(stats)` | Aucune | OUI (CLI) |

### Barre de progrès (`src/donkey_quoter/ui/progress_bar.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Barre progrès animée** | `create_animated_progress_bar(progress, message)` | time, settings | NON |

### Layouts (`src/donkey_quoter/ui/layouts.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Layout principal** | `main_layout()` | streamlit | NON |
| **Layout sidebar** | `sidebar_layout()` | streamlit | NON |

---

## 💾 Fonctionnalités Storage (Stockage des Données)

### DataStorage (`src/donkey_quoter/core/storage.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Charger haikus** | `_load_haikus()` | `json`, `Path` | OUI |
| **Migration format** | `_migrate_old_haiku_format(data)` | Aucune | OUI |
| **Sauvegarder haikus** | `_save_haikus()` | `json` | OUI |
| **Récupérer haiku** | `get_haiku(quote_id, language)` | `random` | OUI |
| **Haiku avec métadonnées** | `get_haiku_with_metadata(quote_id, language)` | `random` | OUI |
| **Ajouter haiku** | `add_haiku(quote_id, haiku, language, model)` | `datetime` | OUI |
| **Vérifier haiku existant** | `has_haiku(quote_id, language)` | Aucune | OUI |
| **Compter haikus** | `count_haikus(quote_id, language)` | Aucune | OUI |
| **Sauvegarder quotes utilisateur** | `save_user_quotes(quotes)` | `json`, Quote | NON |
| **Charger quotes utilisateur** | `load_user_quotes()` | `json`, Quote | NON |
| **Export toutes données** | `export_all_data()` | `datetime` | OUI (CLI) |
| **Import données** | `import_data(data)` | Quote | NON |

---

## ⚙️ Fonctionnalités Configuration & Infrastructure

### StateManager (`src/donkey_quoter/state_manager.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Initialiser état** | `initialize()` | DataLoader, `random` | OUI |
| **Langue courante** | `get_language()` | `st.session_state` | OUI |
| **Basculer langue** | `toggle_language()` | `st.session_state` | OUI |
| **État affichage toutes quotes** | `get_show_all_quotes()` | `st.session_state` | OUI |
| **Basculer affichage toutes** | `toggle_show_all_quotes()` | `st.session_state` | OUI |
| **Définir quote courante** | `set_current_quote(quote)` | `st.session_state` | NON |
| **Cacher toutes quotes** | `hide_all_quotes()` | `st.session_state` | OUI |

### Settings (`src/donkey_quoter/config/settings.py`)
| Fonctionnalité | Classe/Configuration | Utilisée |
|---|---|---|
| **AppSettings** | Configuration générale app | OUI |
| **PathSettings** | Chemins de fichiers | OUI |
| **UISettings** | Configuration interface | OUI |
| **ExportSettings** | Configuration export | OUI |
| **TokenSettings** | Estimation tokens | OUI (CLI) |
| **PricingSettings** | Prix API Claude | OUI (CLI) |
| **ModelSettings** | Mapping modèles-auteurs | OUI |

### Translations (`src/donkey_quoter/translations.py`)
| Fonctionnalité | Configuration | Utilisée |
|---|---|---|
| **TRANSLATIONS** | Textes FR/EN | OUI |
| **CATEGORY_LABELS** | Labels catégories | OUI |

### Infrastructure (`src/donkey_quoter/infrastructure/anthropic_client.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Client Anthropic** | `AnthropicClient()` | `anthropic` | OUI |
| **Appel Claude** | `call_claude(prompt)` | API Anthropic | OUI |

### Prompts (`src/donkey_quoter/prompts/haiku_prompts.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Construction prompt haiku** | `build_haiku_prompt(quote_text, quote_author, language)` | Aucune | OUI |

### Token Counter (`src/donkey_quoter/token_counter.py`)
| Fonctionnalité | Méthode | Dépendances | Utilisée |
|---|---|---|---|
| **Compter tokens** | `count_tokens(text, model)` | tiktoken | OUI (CLI) |
| **Estimation coût** | `estimate_cost(input_tokens, output_tokens, model)` | settings | OUI (CLI) |

---

## 📦 Fonctionnalités CLI (Interface en Ligne de Commande)

### Haiku CLI (`scripts/haiku_cli.py`)
| Fonctionnalité | Fonction | Dépendances | Utilisée |
|---|---|---|---|
| **Configuration UTF-8 Windows** | `setup_utf8_windows()` | `sys`, `io` | OUI |
| **Création client API** | `create_api_client(dry_run, model)` | AnthropicClient | OUI |
| **Commande generate** | `cmd_generate(args, manager, model)` | HaikuManager | OUI |
| **Commande stats** | `cmd_stats(manager)` | HaikuManager | OUI |
| **Commande export** | `cmd_export(args, manager)` | HaikuManager, `csv`, `json` | OUI |

---

## 🔍 Configurations et Dépendances Utilisées

### Dépendances Python principales
- `streamlit` - Interface web
- `anthropic` - Client API Claude
- `pydantic` - Validation données
- `tiktoken` - Comptage tokens (CLI)
- `python-dotenv` - Variables d'environnement

### Fichiers de configuration
- `pyproject.toml` - Configuration projet Python
- `requirements.txt` / `requirements-dev.txt` - Dépendances
- `.env` - Variables d'environnement (CLAUDE_API_KEY)

### Données
- `data/quotes.json` - Citations par défaut
- `data/haikus.json` - Haïkus générés (stockage)

### Assets
- `src/donkey_quoter/styles.css` - Styles CSS personnalisés

---

## ❌ Fonctionnalités NON utilisées (Candidates à la suppression)

### Fonctions définies mais non utilisées dans l'app principal:
1. **QuoteAdapter**: `add_quote()`, `update_quote()`, `delete_quote()`
2. **QuoteService**: `filter_by_category()`, `filter_by_type()`, `update_quote_from_input()`
3. **HaikuAdapter**: `reset_generation_count()`
4. **UI Components**: `render_stats_card()`, `render_action_button()`
5. **UI Layouts**: `main_layout()`, `sidebar_layout()`
6. **UI Progress**: `create_animated_progress_bar()`
7. **DataStorage**: Méthodes pour quotes utilisateur (`save_user_quotes()`, `load_user_quotes()`)
8. **StateManager**: `set_current_quote()`

### Remarques importantes:
- Certaines fonctions "non utilisées" dans l'app Streamlit sont utilisées dans le CLI
- Toutes les fonctionnalités listées comme "NON" pourraient être utiles pour de futures fonctionnalités
- **NE RIEN SUPPRIMER** pour l'instant - cette liste sert seulement à identifier les redondances potentielles

---

## 🔄 Redondances réelles identifiées

### Méthodes qui font exactement la même chose:

#### 1. Récupération haiku existant - 3 méthodes similaires:
- **HaikuAdapter.get_existing_haiku()** (`haiku_adapter.py:149`) - Alias complet avec métadonnées
- **HaikuAdapter.get_stored_haiku_for_quote()** (`haiku_adapter.py:93`) - Version simple sans métadonnées
- **HaikuService.get_stored_haiku()** (`haiku_service.py:106`) - Version bas niveau (string uniquement)

**Recommandation**: Conserver `get_existing_haiku()` comme interface principale, garder les autres pour compatibility interne.

#### 2. Gestion des quotes dans StateManager vs QuoteAdapter:
- **StateManager.set_current_quote()** vs **QuoteAdapter.current_quote setter**
- **StateManager.hide_all_quotes()** vs **StateManager.toggle_show_all_quotes()**

**Recommandation**: Centraliser dans StateManager, adapter QuoteAdapter pour utiliser StateManager.

#### 3. Chargement/sauvegarde quotes dans plusieurs endroits:
- **DataLoader.load_quotes()** + **DataLoader.save_quotes()**
- **DataStorage.save_user_quotes()** + **DataStorage.load_user_quotes()**

**Recommandation**: DataLoader pour quotes par défaut, DataStorage pour quotes utilisateur (logique métier différente).

#### 4. Méthodes d'export multiples:
- **QuoteAdapter.export_saved_data()** (via QuoteService)
- **DataStorage.export_all_data()** (plus complet)
- **HaikuManager.export_data()** (format CLI)

**Recommandation**: Spécialiser par usage - web app vs CLI vs stockage complet.

### Vraies redondances à consolider:

#### Pattern Adapter redondant:
- Les **Adapter classes** ne font que déléguer aux **Service classes**
- Beaucoup de méthodes sont des pass-through directs
- Complexité ajoutée sans valeur claire

**Impact refactoring**: Attention - les Adapters gèrent l'état Streamlit (`st.session_state`)

#### Méthodes alias non nécessaires:
- **HaikuAdapter.generate_from_quote()** = alias de **generate_haiku_for_quote()**
- **StateManager.get_show_all_quotes()** pourrait être une property
- **QuoteService.is_quote_in_list()** = simple `quote in quotes`

---

## ✅ Statut de l'audit

- [x] **Fonctionnalités Quote** : Auditées et documentées
- [x] **Fonctionnalités Haiku** : Auditées et documentées
- [x] **Fonctionnalités UI** : Auditées et documentées
- [x] **Fonctionnalités Storage** : Auditées et documentées
- [x] **Configurations** : Auditées et documentées
- [x] **CLI** : Audité et documenté
- [x] **Redondances** : Identifiées et analysées
- [ ] **Tests** : Aucun test implémenté actuellement
- [x] **Documentation** : Auditée

### Prochaines étapes recommandées:
1. ✅ Conserver toutes les fonctionnalités listées
2. ✅ Vraies redondances identifiées et analysées
3. 🔄 Planifier le refactoring en consolidant les redondances identifiées
4. ⚠️ Attention particulière aux Adapters qui gèrent l'état Streamlit
5. 🧪 Ajouter des tests pour les fonctionnalités critiques
