<?php
/**
 * header.php — En-tête commun aux pages publiques.
 * Variables attendues (facultatives) : $pageTitle, $pageDescription, $pageActive.
 */
$pageTitle = $pageTitle ?? '';
$pageDescription = $pageDescription ?? getParam('slogan', 'Marinades et épices de Côte d’Ivoire');
$pageActive = $pageActive ?? '';
$titreComplet = $pageTitle !== '' ? $pageTitle . ' | ' . SITE_NAME : SITE_NAME . ' — ' . getParam('slogan', 'Le vrai goût de chez nous');
$nbPanier = panierNombreArticles();
$categoriesMenu = getDB()->query('SELECT nom, slug FROM categories ORDER BY ordre, nom')->fetchAll();

function lienActif(string $page, string $actif): string
{
    return $page === $actif ? ' aria-current="page" class="actif"' : '';
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= e($titreComplet) ?></title>
<meta name="description" content="<?= e($pageDescription) ?>">
<meta property="og:title" content="<?= e($titreComplet) ?>">
<meta property="og:description" content="<?= e($pageDescription) ?>">
<meta property="og:type" content="website">
<link rel="icon" href="<?= BASE_URL ?>assets/images/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="<?= BASE_URL ?>assets/css/style.css" rel="stylesheet">
</head>
<body data-base-url="<?= e(BASE_URL) ?>" data-csrf="<?= e(genererTokenCSRF()) ?>">
<a class="lien-evitement" href="#contenu">Aller au contenu</a>

<header class="entete">
    <div class="entete-bandeau">
        <?php $seuil = (int) getParam('livraison_offerte_des', '0'); ?>
        <?php if ($seuil > 0): ?>
            Livraison offerte à Abidjan dès <?= e(formatPrix($seuil)) ?> d’achat
        <?php else: ?>
            Livraison à domicile à Abidjan
        <?php endif; ?>
    </div>
    <div class="conteneur entete-barre">
        <a href="<?= BASE_URL ?>" class="logo" aria-label="Accueil <?= e(SITE_NAME) ?>"><?= getLogo() ?></a>

        <button class="menu-bouton" type="button" aria-expanded="false" aria-controls="menu-principal">
            <span class="menu-bouton-barres" aria-hidden="true"></span>
            <span class="visuellement-cache">Ouvrir le menu</span>
        </button>

        <nav id="menu-principal" class="menu" aria-label="Navigation principale">
            <a href="<?= BASE_URL ?>"<?= lienActif('accueil', $pageActive) ?>>Accueil</a>
            <?php foreach ($categoriesMenu as $cat): ?>
                <a href="<?= BASE_URL ?>boutique.php?categorie=<?= e($cat['slug']) ?>"<?= lienActif('cat-' . $cat['slug'], $pageActive) ?>><?= e($cat['nom']) ?></a>
            <?php endforeach; ?>
            <a href="<?= BASE_URL ?>about.php"<?= lienActif('about', $pageActive) ?>>À propos</a>
            <a href="<?= BASE_URL ?>contact.php"<?= lienActif('contact', $pageActive) ?>>Contact</a>
        </nav>

        <div class="entete-actions">
            <a href="<?= BASE_URL ?><?= clientConnecte() ? 'compte.php' : 'connexion.php' ?>" class="action-icone" title="<?= clientConnecte() ? 'Mon compte' : 'Se connecter' ?>">
                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg>
                <span class="visuellement-cache"><?= clientConnecte() ? 'Mon compte' : 'Se connecter' ?></span>
            </a>
            <a href="<?= BASE_URL ?>panier.php" class="action-icone action-panier" title="Mon panier">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h2l2.4 11.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6.2"/><circle cx="10" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/></svg>
                <span class="compteur-panier" data-compteur-panier <?= $nbPanier ? '' : 'hidden' ?>><?= $nbPanier ?></span>
                <span class="visuellement-cache">Mon panier</span>
            </a>
        </div>
    </div>
</header>

<main id="contenu">
<?php $messagesFlash = afficherFlash(); ?>
<?php if ($messagesFlash): ?><div class="conteneur zone-flash"><?= $messagesFlash ?></div><?php endif; ?>
