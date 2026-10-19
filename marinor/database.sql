-- =====================================================================
-- Marin'Or Ivoire — Script de la base de données (Modèle Physique)
-- Base : marinor_db | Moteur : InnoDB | Encodage : utf8mb4
-- Les prix, stocks et coordonnées ci-dessous sont des données de
-- démonstration à remplacer depuis l'espace d'administration.
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS payments, order_items, orders, messages, subscribers, products, categories, users, admins, settings;

SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- Administrateurs du site
-- ---------------------------------------------------------------------
CREATE TABLE admins (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(60) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  mot_de_passe VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Clients (espace client)
-- ---------------------------------------------------------------------
CREATE TABLE users (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(60) NOT NULL,
  prenom VARCHAR(60) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  telephone VARCHAR(20) NOT NULL,
  mot_de_passe VARCHAR(255) NOT NULL,
  adresse VARCHAR(255) DEFAULT NULL,
  commune VARCHAR(60) DEFAULT NULL,
  ville VARCHAR(60) DEFAULT 'Abidjan',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Gammes de produits
-- ---------------------------------------------------------------------
CREATE TABLE categories (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(60) NOT NULL,
  slug VARCHAR(80) NOT NULL UNIQUE,
  description TEXT DEFAULT NULL,
  image VARCHAR(100) DEFAULT NULL,
  ordre TINYINT UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Produits
-- ---------------------------------------------------------------------
CREATE TABLE products (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  category_id INT UNSIGNED NOT NULL,
  nom VARCHAR(80) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  description_courte VARCHAR(160) NOT NULL,
  description TEXT NOT NULL,
  ingredients TEXT DEFAULT NULL,
  conseils TEXT DEFAULT NULL,
  prix INT UNSIGNED NOT NULL,
  contenance VARCHAR(30) DEFAULT NULL,
  conditionnement ENUM('pot','sachet','bidon') NOT NULL DEFAULT 'sachet',
  stock INT UNSIGNED NOT NULL DEFAULT 0,
  image VARCHAR(100) DEFAULT NULL,
  actif TINYINT(1) NOT NULL DEFAULT 1,
  en_vedette TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
  INDEX idx_products_actif (actif, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Commandes (les commandes restent conservées si le client supprime son compte)
-- ---------------------------------------------------------------------
CREATE TABLE orders (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  reference VARCHAR(20) NOT NULL UNIQUE,
  user_id INT UNSIGNED DEFAULT NULL,
  nom_livraison VARCHAR(120) NOT NULL,
  telephone_livraison VARCHAR(20) NOT NULL,
  adresse_livraison VARCHAR(255) NOT NULL,
  commune VARCHAR(60) NOT NULL,
  ville VARCHAR(60) NOT NULL DEFAULT 'Abidjan',
  instructions VARCHAR(255) DEFAULT NULL,
  sous_total INT UNSIGNED NOT NULL,
  frais_livraison INT UNSIGNED NOT NULL DEFAULT 0,
  total INT UNSIGNED NOT NULL,
  statut ENUM('en_attente','payee','en_preparation','expediee','livree','annulee') NOT NULL DEFAULT 'en_attente',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX idx_orders_statut (statut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Lignes de commande (nom et prix figés au moment de l'achat)
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id INT UNSIGNED NOT NULL,
  product_id INT UNSIGNED DEFAULT NULL,
  nom_produit VARCHAR(80) NOT NULL,
  prix_unitaire INT UNSIGNED NOT NULL,
  quantite SMALLINT UNSIGNED NOT NULL,
  total_ligne INT UNSIGNED NOT NULL,
  CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Paiements par mobile money (une commande = un paiement)
-- ---------------------------------------------------------------------
CREATE TABLE payments (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id INT UNSIGNED NOT NULL UNIQUE,
  methode ENUM('wave','orange_money','moov_money','djamo') NOT NULL,
  montant INT UNSIGNED NOT NULL,
  numero_payeur VARCHAR(20) DEFAULT NULL,
  reference_transaction VARCHAR(60) DEFAULT NULL,
  statut ENUM('en_attente','en_verification','valide','refuse') NOT NULL DEFAULT 'en_attente',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  validated_at DATETIME DEFAULT NULL,
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Messages du formulaire de contact
-- ---------------------------------------------------------------------
CREATE TABLE messages (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL,
  telephone VARCHAR(20) DEFAULT NULL,
  sujet VARCHAR(80) NOT NULL,
  message TEXT NOT NULL,
  lu TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Abonnés à la lettre d'information
-- ---------------------------------------------------------------------
CREATE TABLE subscribers (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(120) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Paramètres du site (clé / valeur)
-- ---------------------------------------------------------------------
CREATE TABLE settings (
  cle VARCHAR(50) PRIMARY KEY,
  valeur TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- Données initiales
-- =====================================================================

-- Le mot de passe réel est défini par install.php
INSERT INTO admins (nom, email, mot_de_passe) VALUES
('Administrateur', 'admin@marinor-ivoire.ci', 'a-definir-par-install');

INSERT INTO categories (id, nom, slug, description, ordre) VALUES
(1, 'Marinades', 'marinades', 'Des marinades prêtes à l’emploi pour vos viandes et vos poissons, braisés, rôtis ou grillés.', 1),
(2, 'Épices', 'epices', 'Épices et condiments pour relever, parfumer et lier toutes vos sauces ivoiriennes.', 2),
(3, 'Essentiels', 'essentiels', 'Les bases de la cuisine de chez nous : pâte d’arachide et huile rouge.', 3);

INSERT INTO products (category_id, nom, slug, description_courte, description, conseils, prix, contenance, conditionnement, stock, en_vedette) VALUES
(1, 'Marinade Poulet', 'marinade-poulet',
 'Pour un poulet braisé, rôti ou grillé, savoureux et parfaitement assaisonné.',
 'Notre marinade poulet est prête à l’emploi : elle parfume et attendrit la viande pour un poulet braisé, rôti ou grillé, sans avoir à doser chaque épice.',
 'Badigeonnez généreusement le poulet, laissez reposer au moins 30 minutes au frais, puis faites cuire au four, à la poêle ou au feu de bois.',
 3500, '500 g', 'pot', 40, 1),
(1, 'Marinade Poisson', 'marinade-poisson',
 'Sublime vos poissons braisés, frits ou fumés en un seul geste.',
 'Pensée pour le poisson, cette marinade relève sa saveur sans la masquer, que vous le prépariez braisé, frit ou fumé.',
 'Incisez le poisson, enduisez-le de marinade à l’intérieur comme à l’extérieur, laissez reposer 20 minutes avant la cuisson.',
 3500, NULL, 'pot', 40, 0),
(1, 'Marinade Mixte', 'marinade-mixte',
 'Une seule marinade pour parfumer toutes vos viandes et vos poissons.',
 'Polyvalente, la marinade mixte accompagne toutes vos grillades : poulet, bœuf, mouton ou poisson.',
 'Idéale pour les grillades en famille : préparez toutes vos viandes avec le même pot.',
 3500, NULL, 'pot', 40, 0),
(2, 'Épice Spéciale Poulet', 'epice-speciale-poulet',
 'Le mélange idéal pour relever toutes vos volailles avec caractère.',
 'Un mélange d’épices pensé pour la volaille, à saupoudrer avant la cuisson ou à incorporer dans vos sauces.',
 'Saupoudrez sur le poulet avant la cuisson ou ajoutez une cuillerée dans la sauce en fin de préparation.',
 1500, NULL, 'sachet', 60, 0),
(2, 'Épice Spéciale Poisson', 'epice-speciale-poisson',
 'Un assaisonnement pensé pour révéler la saveur de tous vos poissons.',
 'Notre assaisonnement spécial poisson accompagne vos poissons grillés, frits ou fumés et révèle leur goût.',
 'Frottez le poisson avec le mélange avant la cuisson, ou ajoutez-le directement dans votre sauce.',
 1500, '300 g', 'sachet', 60, 1),
(2, 'Paprika', 'paprika',
 'Couleur et douce chaleur pour vos sauces, grillades et marinades maison.',
 'Le paprika apporte une belle couleur et une chaleur douce à vos sauces, grillades et marinades.',
 'Ajoutez-le en fin de cuisson pour préserver sa couleur et son arôme.',
 1000, NULL, 'sachet', 60, 0),
(2, 'Piment en poudre', 'piment-en-poudre',
 'Le piment de chez nous, pour relever vos plats à volonté.',
 'Un piment en poudre au goût franc pour relever vos sauces, soupes et grillades selon vos envies.',
 'Commencez par une petite pincée et ajustez selon votre goût.',
 1000, NULL, 'sachet', 60, 0),
(2, 'Graines d’akpi', 'graines-d-akpi',
 'L’akpi traditionnel, pour parfumer et lier naturellement vos sauces ivoiriennes.',
 'Les graines d’akpi parfument et épaississent naturellement les sauces de la cuisine ivoirienne.',
 'Faites griller légèrement les graines, écrasez-les, puis incorporez-les à votre sauce.',
 1500, NULL, 'sachet', 50, 0),
(2, 'Poudre de djoumblé', 'poudre-de-djoumble',
 'Préparez une sauce djoumblé authentique, simplement et sans longue préparation.',
 'La poudre de djoumblé vous permet de préparer une sauce djoumblé authentique, sans les longues étapes de préparation traditionnelles.',
 'Délayez la poudre dans un peu d’eau chaude, puis ajoutez-la à votre préparation en remuant.',
 1500, NULL, 'sachet', 50, 1),
(2, 'Poudre de crevettes séchées', 'poudre-de-crevettes-sechees',
 'Le goût iodé des crevettes séchées pour enrichir sauces et ragoûts.',
 'La poudre de crevettes séchées apporte une saveur iodée et profonde à vos sauces et ragoûts.',
 'Une cuillerée suffit pour parfumer une sauce pour toute la famille.',
 2000, NULL, 'sachet', 40, 0),
(2, 'Poudre de poisson sec', 'poudre-de-poisson-sec',
 'La saveur profonde du poisson sec, prête pour vos sauces traditionnelles.',
 'Toute la saveur du poisson sec, déjà réduite en poudre, pour vos sauces traditionnelles.',
 'Ajoutez-la en début de cuisson pour qu’elle parfume toute la sauce.',
 2000, NULL, 'sachet', 40, 0),
(2, 'Purée d’ail', 'puree-d-ail',
 'L’ail déjà prêt, pour vos marinades, sauces et grillades sans épluchage.',
 'Notre purée d’ail vous évite l’épluchage et le pilage, pour des marinades, sauces et grillades parfumées en un instant.',
 'Une cuillère à café de purée remplace environ deux gousses d’ail. Refermez bien le pot après usage.',
 1500, NULL, 'pot', 50, 0),
(2, 'Bouillon bio de poulet', 'bouillon-bio-de-poulet',
 'Une base savoureuse pour réussir soupes, sauces et ragoûts en famille.',
 'Une base savoureuse au goût de poulet pour réussir vos soupes, sauces et ragoûts.',
 'Ajoutez le bouillon au début de la cuisson et goûtez avant de saler.',
 1500, NULL, 'sachet', 60, 0),
(3, 'Pâte d’arachide', 'pate-d-arachide',
 'Une pâte onctueuse pour une sauce arachide riche, comme à la maison.',
 'Une pâte d’arachide onctueuse, prête à l’emploi, pour une sauce arachide riche et généreuse.',
 'Délayez la pâte dans un peu de bouillon chaud avant de l’ajouter à votre sauce.',
 2500, NULL, 'pot', 40, 0),
(3, 'Huile rouge', 'huile-rouge',
 'L’huile rouge de nos traditions, pour des sauces colorées et généreuses.',
 'L’huile rouge, incontournable de nos sauces traditionnelles, pour des plats colorés et généreux.',
 'Conservez le bidon à l’abri de la lumière et de la chaleur.',
 3000, NULL, 'bidon', 30, 1);

INSERT INTO settings (cle, valeur) VALUES
('slogan', 'Le vrai goût de chez nous'),
('description', 'Marin’Or Ivoire est une marque ivoirienne de marinades et d’épices. Élaborés à partir d’ingrédients naturels, nos produits subliment les saveurs authentiques de chez nous et simplifient votre cuisine du quotidien, pour des repas savoureux à partager en famille.'),
('adresse', 'Abidjan, Côte d’Ivoire'),
('telephone', '+225 00 00 00 00 00'),
('whatsapp', '+225 00 00 00 00 00'),
('email', 'contact@marinor-ivoire.ci'),
('horaires', 'Du lundi au samedi, de 8 h à 18 h'),
('facebook', ''),
('instagram', ''),
('tiktok', ''),
('logo', ''),
('frais_livraison', '1500'),
('livraison_offerte_des', '20000'),
('wave_numero', '+225 00 00 00 00 00'),
('orange_money_numero', '+225 00 00 00 00 00'),
('moov_money_numero', '+225 00 00 00 00 00'),
('djamo_numero', '+225 00 00 00 00 00');
