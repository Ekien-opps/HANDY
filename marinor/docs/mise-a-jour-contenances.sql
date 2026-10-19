-- Marin'Or Ivoire — alignement des fiches produits sur les emballages (facultatif)
-- À exécuter une seule fois dans phpMyAdmin, base marinor_db, onglet SQL.
-- Les prix, stocks et textes ne sont pas modifiés.

-- Contenances indiquées sur les emballages
UPDATE products SET contenance = '500 g' WHERE slug IN ('marinade-poulet', 'marinade-poisson', 'marinade-mixte');
UPDATE products SET contenance = '100 g' WHERE slug IN (
  'epice-speciale-poulet', 'epice-speciale-poisson', 'paprika', 'piment-en-poudre', 'graines-d-akpi',
  'poudre-de-djoumble', 'poudre-de-crevettes-sechees', 'poudre-de-poisson-sec', 'puree-d-ail', 'bouillon-bio-de-poulet'
);
UPDATE products SET contenance = '1 kg' WHERE slug = 'pate-d-arachide';

-- La purée d'ail est vendue en sachet (fond crème de la charte derrière la photo, comme les autres sachets)
UPDATE products SET conditionnement = 'sachet' WHERE slug = 'puree-d-ail';
