# Conception de la base de données — Méthode MERISE
## Boutique en ligne Marin’Or Ivoire (base `marinor_db`)

---

## I. Règles de gestion

**Règle 1** : Une gamme regroupe zéro (0) ou plusieurs (n) produits, tandis qu’un produit appartient à une (1) et une (1) seule gamme.

**Règle 2** : Un client passe zéro (0) ou plusieurs (n) commandes, tandis qu’une commande est passée par zéro (0) ou un (1) client. Une commande reste enregistrée lorsque le client supprime son compte, pour les besoins de la comptabilité.

**Règle 3** : Une commande contient une (1) ou plusieurs (n) lignes de commande, tandis qu’une ligne de commande appartient à une (1) et une (1) seule commande.

**Règle 4** : Un produit figure dans zéro (0) ou plusieurs (n) lignes de commande, tandis qu’une ligne de commande concerne zéro (0) ou un (1) produit. Le nom et le prix du produit sont recopiés dans la ligne au moment de l’achat, afin que l’historique reste exact même si le produit est modifié ou supprimé.

**Règle 5** : Une commande est réglée par un (1) et un (1) seul paiement, tandis qu’un paiement règle une (1) et une (1) seule commande. Le paiement se fait par Wave, Orange Money, Moov Money ou Djamo.

**Règle 6** : Un client possède une (1) et une (1) seule adresse e-mail, qui lui sert d’identifiant de connexion ; deux clients ne peuvent pas partager la même adresse.

**Règle 7** : Un visiteur, inscrit ou non, envoie zéro (0) ou plusieurs (n) messages par le formulaire de contact ; un message n’est rattaché à aucun compte.

**Règle 8** : Un abonné à la lettre d’information est identifié par une (1) seule adresse e-mail, enregistrée une seule fois.

**Règle 9** : Un administrateur gère l’ensemble de la boutique (gammes, produits, commandes, paiements, messages et paramètres). Les paramètres du site sont enregistrés sous forme de couples clé / valeur.

**Règle 10** : Une commande ne peut être validée que si la quantité demandée de chaque produit est disponible en stock ; le stock est diminué au moment de la commande et rétabli si la commande est annulée.

---

## II. Dictionnaire de données

| N° | Description | Code | Type | Taille |
|---|---|---|---|---|
| 1 | Identifiant de l’administrateur | id | INT | 10 |
| 2 | Nom de l’administrateur | nom | VARCHAR | 60 |
| 3 | E-mail de l’administrateur | email | VARCHAR | 120 |
| 4 | Mot de passe haché | mot_de_passe | VARCHAR | 255 |
| 5 | Identifiant du client | id | INT | 10 |
| 6 | Nom du client | nom | VARCHAR | 60 |
| 7 | Prénom du client | prenom | VARCHAR | 60 |
| 8 | E-mail du client | email | VARCHAR | 120 |
| 9 | Téléphone du client | telephone | VARCHAR | 20 |
| 10 | Adresse habituelle du client | adresse | VARCHAR | 255 |
| 11 | Commune du client | commune | VARCHAR | 60 |
| 12 | Ville du client | ville | VARCHAR | 60 |
| 13 | Identifiant de la gamme | id | INT | 10 |
| 14 | Nom de la gamme | nom | VARCHAR | 60 |
| 15 | Identifiant URL de la gamme | slug | VARCHAR | 80 |
| 16 | Description de la gamme | description | TEXT | — |
| 17 | Image de la gamme | image | VARCHAR | 100 |
| 18 | Ordre d’affichage de la gamme | ordre | TINYINT | 3 |
| 19 | Identifiant du produit | id | INT | 10 |
| 20 | Nom du produit | nom | VARCHAR | 80 |
| 21 | Identifiant URL du produit | slug | VARCHAR | 100 |
| 22 | Présentation courte du produit | description_courte | VARCHAR | 160 |
| 23 | Description complète du produit | description | TEXT | — |
| 24 | Ingrédients du produit | ingredients | TEXT | — |
| 25 | Conseils d’utilisation | conseils | TEXT | — |
| 26 | Prix du produit (FCFA) | prix | INT | 10 |
| 27 | Contenance (ex. 500 g) | contenance | VARCHAR | 30 |
| 28 | Conditionnement (pot, sachet, bidon) | conditionnement | ENUM | — |
| 29 | Quantité en stock | stock | INT | 10 |
| 30 | Photo du produit | image | VARCHAR | 100 |
| 31 | Visibilité sur le site | actif | TINYINT | 1 |
| 32 | Mise en avant sur l’accueil | en_vedette | TINYINT | 1 |
| 33 | Identifiant de la commande | id | INT | 10 |
| 34 | Référence de la commande | reference | VARCHAR | 20 |
| 35 | Nom du destinataire | nom_livraison | VARCHAR | 120 |
| 36 | Téléphone du destinataire | telephone_livraison | VARCHAR | 20 |
| 37 | Adresse de livraison | adresse_livraison | VARCHAR | 255 |
| 38 | Commune de livraison | commune | VARCHAR | 60 |
| 39 | Instructions pour le livreur | instructions | VARCHAR | 255 |
| 40 | Sous-total de la commande | sous_total | INT | 10 |
| 41 | Frais de livraison | frais_livraison | INT | 10 |
| 42 | Montant total | total | INT | 10 |
| 43 | Statut de la commande | statut | ENUM | — |
| 44 | Identifiant de la ligne de commande | id | INT | 10 |
| 45 | Nom du produit au moment de l’achat | nom_produit | VARCHAR | 80 |
| 46 | Prix unitaire au moment de l’achat | prix_unitaire | INT | 10 |
| 47 | Quantité commandée | quantite | SMALLINT | 5 |
| 48 | Total de la ligne | total_ligne | INT | 10 |
| 49 | Identifiant du paiement | id | INT | 10 |
| 50 | Moyen de paiement | methode | ENUM | — |
| 51 | Montant du paiement | montant | INT | 10 |
| 52 | Numéro ayant payé | numero_payeur | VARCHAR | 20 |
| 53 | Référence de la transaction | reference_transaction | VARCHAR | 60 |
| 54 | Statut du paiement | statut | ENUM | — |
| 55 | Date de validation du paiement | validated_at | DATETIME | — |
| 56 | Identifiant du message | id | INT | 10 |
| 57 | Nom de l’expéditeur | nom | VARCHAR | 120 |
| 58 | E-mail de l’expéditeur | email | VARCHAR | 120 |
| 59 | Téléphone de l’expéditeur | telephone | VARCHAR | 20 |
| 60 | Sujet du message | sujet | VARCHAR | 80 |
| 61 | Contenu du message | message | TEXT | — |
| 62 | Message lu | lu | TINYINT | 1 |
| 63 | Identifiant de l’abonné | id | INT | 10 |
| 64 | E-mail de l’abonné | email | VARCHAR | 120 |
| 65 | Clé du paramètre | cle | VARCHAR | 50 |
| 66 | Valeur du paramètre | valeur | TEXT | — |

Les dates de création et de mise à jour (`created_at`, `updated_at`) sont présentes dans la plupart des tables et générées automatiquement.

---

## III. Modèle Conceptuel de Données (MCD)

Le MCD comprend dix entités : Administrateur, Client, Gamme, Produit, Commande, Ligne_Commande, Paiement, Message, Abonné et Paramètre. Le schéma complet figure dans le fichier `MCD_MarinOr.png`.

| Association | Entité A | Cardinalités A | Cardinalités B | Entité B |
|---|---|---|---|---|
| regroupe | Gamme | (0,n) | (1,1) | Produit |
| passe | Client | (0,n) | (0,1) | Commande |
| contient | Commande | (1,n) | (1,1) | Ligne_Commande |
| figure dans | Produit | (0,n) | (0,1) | Ligne_Commande |
| est réglée par | Commande | (1,1) | (1,1) | Paiement |

Administrateur, Message, Abonné et Paramètre sont des entités indépendantes : elles ne sont reliées à aucune autre par une clé étrangère.

---

## IV. Règles de passage du MCD au MLD

1. Chaque entité devient une table ; ses propriétés deviennent des colonnes et son identifiant devient la clé primaire.
2. Une association de type 1:N se traduit par la migration de la clé primaire de l’entité côté « 1 » dans la table côté « N », où elle devient clé étrangère.
3. Une association de type 1:1 se traduit par la migration de la clé primaire d’une des deux entités dans l’autre, où elle devient clé étrangère unique.
4. Une association de type N:N se traduit par une table dont la clé primaire est composée des deux clés étrangères. Ici, la relation N:N entre Commande et Produit a été décomposée en entité Ligne_Commande, qui porte les attributs quantité et prix.

---

## V. Modèle Logique de Données (MLD)

Clé primaire **en gras**, clé étrangère précédée de **#**.

- admins (**id**, nom, email, mot_de_passe, created_at)
- users (**id**, nom, prenom, email, telephone, mot_de_passe, adresse, commune, ville, created_at, updated_at)
- categories (**id**, nom, slug, description, image, ordre)
- products (**id**, #category_id, nom, slug, description_courte, description, ingredients, conseils, prix, contenance, conditionnement, stock, image, actif, en_vedette, created_at, updated_at)
- orders (**id**, reference, #user_id, nom_livraison, telephone_livraison, adresse_livraison, commune, ville, instructions, sous_total, frais_livraison, total, statut, created_at, updated_at)
- order_items (**id**, #order_id, #product_id, nom_produit, prix_unitaire, quantite, total_ligne)
- payments (**id**, #order_id, methode, montant, numero_payeur, reference_transaction, statut, created_at, validated_at)
- messages (**id**, nom, email, telephone, sujet, message, lu, created_at)
- subscribers (**id**, email, created_at)
- settings (**cle**, valeur)

---

## VI. Modèle Physique de Données (MPD)

Le MPD correspond au script `database.sql`, exécuté par `install.php`. Points notables :

| Table | Contraintes principales |
|---|---|
| users | `email` unique ; mot de passe haché avec `password_hash()` |
| products | clé étrangère `category_id` → categories(id), suppression interdite si la gamme contient des produits (RESTRICT) ; `slug` unique |
| orders | `reference` unique ; `user_id` → users(id), mis à NULL si le client supprime son compte (SET NULL) |
| order_items | `order_id` → orders(id), supprimé avec la commande (CASCADE) ; `product_id` → products(id), mis à NULL si le produit est supprimé |
| payments | `order_id` unique (un seul paiement par commande) → orders(id) (CASCADE) |
| subscribers | `email` unique |
| settings | clé primaire `cle` |

Toutes les tables utilisent le moteur InnoDB (transactions et clés étrangères) et l’encodage utf8mb4.
