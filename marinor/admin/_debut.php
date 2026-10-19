<?php
/** _debut.php — Début de mise en page de l'administration (barre latérale). */
exigerAdmin();
$adminTitre = $adminTitre ?? 'Administration';
$adminActif = $adminActif ?? '';
$pdoMenu = getDB();
$nbAVerifier = (int) $pdoMenu->query("SELECT COUNT(*) FROM payments WHERE statut = 'en_verification'")->fetchColumn();
$nbMessages = (int) $pdoMenu->query('SELECT COUNT(*) FROM messages WHERE lu = 0')->fetchColumn();
$liens = [
    'index.php'      => ['Tableau de bord', 0],
    'commandes.php'  => ['Commandes', $nbAVerifier],
    'produits.php'   => ['Produits', 0],
    'categories.php' => ['Gammes', 0],
    'clients.php'    => ['Clients', 0],
    'messages.php'   => ['Messages', $nbMessages],
    'parametres.php' => ['Paramètres', 0],
];
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title><?= e($adminTitre) ?> | Administration <?= e(SITE_NAME) ?></title>
<link rel="icon" href="<?= BASE_URL ?>assets/images/favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="<?= BASE_URL ?>assets/css/admin.css" rel="stylesheet">
</head>
<body>
<div class="admin">
    <aside class="admin-barre">
        <a href="<?= BASE_URL ?>admin/" class="admin-logo">Marin’Or <small>Administration</small></a>
        <nav aria-label="Administration">
            <?php foreach ($liens as $fichier => [$libelle, $badge]): ?>
                <a href="<?= BASE_URL ?>admin/<?= $fichier ?>"<?= $adminActif === $fichier ? ' aria-current="page"' : '' ?>>
                    <?= e($libelle) ?><?php if ($badge): ?> <span class="badge"><?= $badge ?></span><?php endif; ?>
                </a>
            <?php endforeach; ?>
        </nav>
        <div class="admin-barre-pied">
            <a href="<?= BASE_URL ?>" target="_blank" rel="noopener">Voir le site</a>
            <form method="post" action="<?= BASE_URL ?>admin/logout.php">
                <?= champCSRF() ?>
                <button type="submit">Se déconnecter</button>
            </form>
        </div>
    </aside>
    <main class="admin-contenu">
        <header class="admin-entete">
            <h1><?= e($adminTitre) ?></h1>
            <span>Connecté : <?= e($_SESSION['admin_nom'] ?? '') ?></span>
        </header>
        <?= afficherFlash() ?>
