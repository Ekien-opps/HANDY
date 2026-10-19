<?php
require_once __DIR__ . '/includes/functions.php';

$pdo = getDB();
$slug = (string) ($_GET['slug'] ?? '');

$stmt = $pdo->prepare(
    'SELECT p.*, c.nom AS categorie_nom, c.slug AS categorie_slug
     FROM products p JOIN categories c ON c.id = p.category_id
     WHERE p.slug = ? AND p.actif = 1'
);
$stmt->execute([$slug]);
$produit = $stmt->fetch();

if (!$produit) {
    flash('erreur', "Ce produit n'existe pas ou n'est plus disponible.");
    redirect(BASE_URL . 'boutique.php');
}

// Produits de la même gamme, complétés par d'autres gammes si nécessaire
$stmt = $pdo->prepare(
    'SELECT * FROM products WHERE actif = 1 AND id <> ?
     ORDER BY (category_id = ?) DESC, en_vedette DESC, RAND() LIMIT 4'
);
$stmt->execute([$produit['id'], $produit['category_id']]);
$similaires = $stmt->fetchAll();

$stock = (int) $produit['stock'];
$pageTitle = $produit['nom'];
$pageDescription = $produit['description_courte'];
$pageActive = 'cat-' . $produit['categorie_slug'];

require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur">
        <nav class="fil-ariane" aria-label="Fil d’Ariane">
            <a href="<?= BASE_URL ?>">Accueil</a> /
            <a href="<?= BASE_URL ?>boutique.php?categorie=<?= e($produit['categorie_slug']) ?>"><?= e($produit['categorie_nom']) ?></a> /
            <?= e($produit['nom']) ?>
        </nav>

        <div class="fiche">
            <div class="fiche-visuel carte-<?= e($produit['conditionnement']) ?>">
                <img src="<?= e(imageProduit($produit)) ?>" alt="<?= e($produit['nom']) ?>" width="560" height="560">
            </div>

            <div class="fiche-infos">
                <p class="fiche-gamme"><?= e($produit['categorie_nom']) ?></p>
                <h1 class="titre-affiche"><?= e($produit['nom']) ?></h1>
                <?php if ($produit['contenance']): ?><p class="fiche-contenance"><?= e($produit['contenance']) ?></p><?php endif; ?>
                <p class="fiche-prix"><?= formatPrix((int) $produit['prix']) ?></p>
                <p class="fiche-accroche"><?= e($produit['description_courte']) ?></p>

                <?php if ($stock > 0): ?>
                    <form action="<?= BASE_URL ?>panier.php" method="post" class="fiche-achat" data-ajout-panier>
                        <?= champCSRF() ?>
                        <input type="hidden" name="action" value="ajouter">
                        <input type="hidden" name="produit_id" value="<?= (int) $produit['id'] ?>">
                        <div class="selecteur-quantite" data-selecteur-quantite>
                            <button type="button" data-moins aria-label="Retirer un">−</button>
                            <label class="visuellement-cache" for="quantite">Quantité</label>
                            <input type="number" id="quantite" name="quantite" value="1" min="1" max="<?= min($stock, QUANTITE_MAX_PAR_PRODUIT) ?>" inputmode="numeric">
                            <button type="button" data-plus aria-label="Ajouter un">+</button>
                        </div>
                        <button type="submit" class="bouton bouton-bordeaux bouton-large">Ajouter au panier</button>
                    </form>
                    <p class="fiche-stock<?= $stock <= 5 ? ' stock-faible' : '' ?>">
                        <?= $stock <= 5 ? 'Plus que ' . $stock . ' en stock' : 'En stock, livré à domicile' ?>
                    </p>
                <?php else: ?>
                    <p class="rupture">Ce produit est momentanément indisponible.</p>
                <?php endif; ?>

                <div class="fiche-onglets">
                    <details open>
                        <summary>Description</summary>
                        <p><?= nl2br(e($produit['description'])) ?></p>
                    </details>
                    <details>
                        <summary>Ingrédients</summary>
                        <p><?= $produit['ingredients'] ? nl2br(e($produit['ingredients'])) : 'La liste complète des ingrédients figure sur l’emballage du produit.' ?></p>
                    </details>
                    <details>
                        <summary>Conseils d’utilisation</summary>
                        <p><?= $produit['conseils'] ? nl2br(e($produit['conseils'])) : 'Contactez-nous pour des idées de recettes.' ?></p>
                    </details>
                </div>
            </div>
        </div>
    </div>
</section>

<?php if ($similaires): ?>
<section class="section section-creme">
    <div class="conteneur">
        <h2 class="titre-section">À associer avec</h2>
        <div class="grille-produits">
            <?php foreach ($similaires as $p): ?>
                <?= carteProduit($p) ?>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php endif; ?>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
