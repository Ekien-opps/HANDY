<?php
require_once __DIR__ . '/includes/functions.php';

$pdo = getDB();
$pageActive = 'accueil';

$gammes = $pdo->query(
    'SELECT c.*, COUNT(p.id) AS nb_produits FROM categories c
     LEFT JOIN products p ON p.category_id = c.id AND p.actif = 1
     GROUP BY c.id ORDER BY c.ordre, c.nom'
)->fetchAll();

$vedettes = $pdo->query(
    'SELECT * FROM products WHERE actif = 1 AND en_vedette = 1 ORDER BY updated_at DESC LIMIT 4'
)->fetchAll();

$nbProduits = (int) $pdo->query('SELECT COUNT(*) FROM products WHERE actif = 1')->fetchColumn();

// Photos de l'accueil : déposez-les dans assets/images/accueil/ (voir le fichier LISEZ-MOI.txt du dossier)
$photoPrincipale = imageLocale('accueil/hero-principale');
$photoSecondaire = imageLocale('accueil/hero-secondaire');
$imageEtapes = imageLocale('accueil/etapes');

require_once __DIR__ . '/includes/header.php';
?>

<section class="accueil-hero">
    <div class="conteneur accueil-hero-grille">
        <div class="accueil-hero-texte">
            <h1 class="titre-affiche">Le vrai goût de chez nous</h1>
            <p><?= e(getParam('description')) ?></p>
            <div class="groupe-boutons">
                <a href="<?= BASE_URL ?>boutique.php" class="bouton bouton-or">Découvrir les produits</a>
                <a href="<?= BASE_URL ?>about.php" class="bouton bouton-contour-clair">Notre histoire</a>
            </div>
        </div>
        <div class="vitrine">
            <figure class="vitrine-arche<?= $photoPrincipale ? ' a-photo' : '' ?>">
                <img src="<?= e($photoPrincipale ?: BASE_URL . 'assets/images/pot.svg') ?>"
                     alt="<?= $photoPrincipale ? 'Produits Marin’Or Ivoire' : '' ?>" width="420" height="520" fetchpriority="high">
            </figure>
            <figure class="vitrine-medaillon<?= $photoSecondaire ? ' a-photo' : '' ?>">
                <img src="<?= e($photoSecondaire ?: BASE_URL . 'assets/images/sachet.svg') ?>"
                     alt="<?= $photoSecondaire ? 'Plat préparé avec Marin’Or Ivoire' : '' ?>" width="220" height="220">
            </figure>
            <p class="vitrine-etiquette"><strong><?= $nbProduits ?></strong> saveurs de chez nous</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="conteneur">
        <h2 class="titre-section">Trois gammes pour toute votre cuisine</h2>
        <div class="gammes">
            <?php foreach ($gammes as $g): ?>
            <a href="<?= BASE_URL ?>boutique.php?categorie=<?= e($g['slug']) ?>" class="gamme gamme-<?= e($g['slug']) ?>">
                <img src="<?= e(imageCategorie($g)) ?>" alt="" loading="lazy">
                <span class="gamme-nom"><?= e($g['nom']) ?></span>
                <span class="gamme-texte"><?= e($g['description']) ?></span>
                <span class="gamme-compte"><?= (int) $g['nb_produits'] ?> produit<?= $g['nb_produits'] > 1 ? 's' : '' ?></span>
            </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="section section-creme">
    <div class="conteneur">
        <h2 class="titre-section">Pourquoi choisir Marin’Or Ivoire ?</h2>
        <ul class="arguments">
            <li>
                <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 6c8 6 12 12 12 19a12 12 0 0 1-24 0c0-7 4-13 12-19z"/><path d="M24 20v18"/></svg>
                <strong>Les vraies saveurs de chez nous</strong>
                <span>Des recettes qui respectent la cuisine ivoirienne traditionnelle.</span>
            </li>
            <li>
                <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M10 38c0-16 12-26 28-28-2 16-12 28-28 28z"/><path d="M10 38l16-16"/></svg>
                <strong>Des ingrédients choisis, fabriqués ici</strong>
                <span>Piment, gingembre, ail, akpi : des ingrédients que vous connaissez.</span>
            </li>
            <li>
                <svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="16"/><path d="M24 14v10l7 5"/></svg>
                <strong>Prêts à l’emploi, cuisinez sans effort</strong>
                <span>Ouvrez, badigeonnez, cuisez : le goût du chef au quotidien.</span>
            </li>
            <li>
                <svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="16" cy="18" r="6"/><circle cx="32" cy="18" r="6"/><path d="M6 38c1-7 5-10 10-10s9 3 10 10M22 38c1-7 5-10 10-10s9 3 10 10"/></svg>
                <strong>Le goût qui rassemble la famille</strong>
                <span>Pour les repas du dimanche, les grillades et les fêtes.</span>
            </li>
        </ul>
    </div>
</section>

<?php if ($vedettes): ?>
<section class="section">
    <div class="conteneur">
        <div class="entete-section">
            <h2 class="titre-section">Nos incontournables</h2>
            <a href="<?= BASE_URL ?>boutique.php" class="lien-fort">Voir tous les produits</a>
        </div>
        <div class="grille-produits">
            <?php foreach ($vedettes as $p): ?>
                <?= carteProduit($p) ?>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php endif; ?>

<section class="section bande-etapes">
    <div class="conteneur etapes-grille">
        <div>
            <h2 class="titre-section">Marinez. Cuisez. Régalez-vous.</h2>
            <ol class="etapes">
                <li><strong>Ouvrez</strong> votre pot de marinade Marin’Or.</li>
                <li><strong>Badigeonnez</strong> votre viande ou votre poisson.</li>
                <li><strong>Cuisez</strong> : c’est prêt, il ne reste qu’à servir.</li>
            </ol>
        </div>
        <figure class="etapes-visuel<?= $imageEtapes ? ' a-photo' : '' ?>">
            <img src="<?= e($imageEtapes ?: BASE_URL . 'assets/images/etapes.svg') ?>"
                 alt="Ouvrir le pot, badigeonner la viande, puis servir le plat" width="600" height="460" loading="lazy">
        </figure>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
