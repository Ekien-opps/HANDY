# Marin’Or Ivoire — Boutique en ligne

Site e-commerce de marinades et d’épices ivoiriennes, en PHP 8 natif, MySQL et JavaScript sans dépendance.

## Prérequis

- WampServer (Apache + MySQL), PHP 8.1 ou supérieur, extensions `pdo_mysql` et `fileinfo` activées
- Apache avec `mod_rewrite` (recommandé, pour les règles de sécurité du `.htaccess`)

## Installation en 5 étapes

1. Copier le dossier `marinor` dans `C:\wamp64\www\`.
2. Vérifier `includes/config.php` : `DB_HOST`, `DB_NAME` (`marinor_db`), `DB_USER` (`root`), `DB_PASS` (vide) et `BASE_URL` (`http://localhost/marinor/`, avec le `/` final).
3. Lancer WampServer (icône verte), puis ouvrir `http://localhost/marinor/install.php` : la base, les tables et les 15 produits de démonstration sont créés.
4. Se connecter sur `http://localhost/marinor/admin/` avec `admin@marinor-ivoire.ci` / `MarinOr2026!`, puis changer le mot de passe dans **Paramètres**.
5. Supprimer `install.php`.

## Données à remplacer avant la mise en ligne

Les éléments suivants sont des **valeurs de démonstration** :

- **Prix et stocks** des 15 produits (Administration > Produits)
- **Ingrédients** : laissés vides, à compléter pour chaque produit
- **Photos des produits** : déposez-les dans `assets/images/produits/`, nommées comme indiqué dans le fichier `LISEZ-MOI.txt` du dossier (ex. `marinade-poulet.png`), ou envoyez-les depuis Administration > Produits
- **Images de l’accueil** (grande arche, médaillon, image des trois étapes) : `assets/images/accueil/`
- **Images des gammes** : `assets/images/gammes/`
- **Logo** : `assets/images/logo/logo.png` (et `logo-clair.png` pour le pied de page), ou Administration > Paramètres
- **Police Cream Heavy** : déposez `cream-heavy.otf` (ou `.ttf`, `.woff`, `.woff2`) dans `assets/fonts/`
- **Coordonnées, réseaux sociaux et numéros marchands** Wave, Orange Money, Moov Money et Djamo (Administration > Paramètres)

Chaque dossier contient un fichier `LISEZ-MOI.txt` avec les noms de fichiers attendus. Tant qu’une image est absente, l’illustration d’origine reste affichée.

## Fonctionnement du paiement

Le paiement fonctionne par **transfert mobile money avec vérification manuelle** :

1. le client choisit son moyen de paiement et valide sa commande ;
2. il reçoit le montant exact et le numéro marchand, effectue le transfert, puis saisit la référence reçue par SMS ;
3. l’administrateur vérifie la réception sur son compte et clique sur **Valider le paiement** : la commande passe en « Payée ».

Un paiement automatique (confirmation instantanée) nécessite un compte marchand et des clés d’accès auprès d’un opérateur ou d’un agrégateur de paiement. La table `payments` est déjà prévue pour accueillir ces informations.

## Structure

```
marinor/
├── admin/            Administration (produits, gammes, commandes, clients, messages, paramètres)
├── api/              Points d’entrée appelés en JavaScript (lettre d’information)
├── assets/           css/, js/, images/ (illustrations), fonts/
├── docs/             Dossier MERISE (règles de gestion, dictionnaire, MCD, MLD, MPD)
├── includes/         config, connexion PDO, fonctions, panier, sessions, en-tête et pied de page
├── uploads/          Photos envoyées (exécution de scripts interdite)
├── index.php         Accueil
├── boutique.php      Catalogue par gamme
├── product.php       Fiche produit
├── panier.php        Panier
├── commande.php      Livraison et choix du paiement
├── paiement.php      Instructions de paiement et confirmation
├── inscription.php, connexion.php, compte.php, deconnexion.php
├── about.php, contact.php, confidentialite.php
├── database.sql      Modèle physique de données
└── install.php       Installation (à supprimer après usage)
```

## Sécurité

- Requêtes préparées PDO sur toutes les requêtes contenant des données saisies
- Échappement de tout affichage avec `htmlspecialchars` (fonction `e()`)
- Mots de passe hachés avec `password_hash()` et vérifiés avec `password_verify()`
- Jeton CSRF sur tous les formulaires, y compris la déconnexion
- Limitation des tentatives de connexion (5 en 15 minutes) et des envois de messages
- Sessions client et administrateur séparées, identifiant de session régénéré à chaque connexion
- Envoi d’images contrôlé par type réel (finfo) et taille, noms de fichiers aléatoires
- En-têtes HTTP de sécurité, dont une politique de sécurité du contenu (CSP) sans script en ligne
- Dossiers `includes/` et `docs/` inaccessibles depuis le navigateur, exécution de PHP bloquée dans `uploads/`
