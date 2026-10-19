<?php
require_once __DIR__ . '/includes/functions.php';

$pageTitle = 'À propos';
$pageDescription = getParam('description');
$pageActive = 'about';
require_once __DIR__ . '/includes/header.php';
?>

<section class="bandeau-page bandeau-apropos">
    <div class="conteneur">
        <nav class="fil-ariane" aria-label="Fil d’Ariane"><a href="<?= BASE_URL ?>">Accueil</a> / À propos</nav>
        <h1 class="titre-affiche">Qui sommes-nous ?</h1>
        <p><?= e(getParam('description')) ?></p>
    </div>
</section>

<section class="section">
    <div class="conteneur apropos">
        <div class="apropos-texte">
            <h2 class="titre-section">Notre histoire</h2>
            <p>Marin’Or Ivoire est née d’une conviction simple : bien manger ivoirien ne devrait pas demander des heures de préparation. Nos marinades et nos épices sont pensées pour sublimer la cuisine de chez nous, dans le respect de ses vraies saveurs.</p>
            <p>De la marinade pour le poulet braisé à la poudre de djoumblé, chaque produit répond à un geste du quotidien des cuisines ivoiriennes, pour que chacun puisse retrouver le goût authentique des plats de famille, simplement.</p>
        </div>
        <?php $photoApropos = imageLocale('accueil/apropos'); ?>
        <img src="<?= e($photoApropos ?: imageParDefaut()) ?>" alt="<?= $photoApropos ? 'La boutique Marin’Or Ivoire' : '' ?>" class="apropos-visuel<?= $photoApropos ? ' a-photo' : '' ?>" width="360" height="360" loading="lazy">
    </div>
</section>

<section class="section section-creme">
    <div class="conteneur">
        <dl class="valeurs">
            <div>
                <dt>Notre mission</dt>
                <dd>Mettre les saveurs authentiques de la cuisine ivoirienne à la portée de tous, au quotidien.</dd>
            </div>
            <div>
                <dt>Notre vision</dt>
                <dd>Devenir la marque de marinades et d’épices de référence dans les foyers ivoiriens, puis dans la sous-région.</dd>
            </div>
            <div>
                <dt>Nos valeurs</dt>
                <dd>L’authenticité des recettes, le partage autour de la table et la simplicité pour celles et ceux qui cuisinent.</dd>
            </div>
        </dl>
    </div>
</section>

<section class="section bande-appel">
    <div class="conteneur bande-appel-grille">
        <h2 class="titre-affiche">Le goût qui rassemble</h2>
        <a href="<?= BASE_URL ?>boutique.php" class="bouton bouton-or">Découvrir nos produits</a>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
