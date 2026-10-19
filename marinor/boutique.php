<?php
require_once __DIR__ . '/includes/functions.php';

$pdo = getDB();
$categories = $pdo->query('SELECT * FROM categories ORDER BY ordre, nom')->fetchAll();

$slug = valeurTexte($_GET, 'categorie');
$categorie = null;
foreach ($categories as $c) {
    if ($c['slug'] === $slug) {
        $categorie = $c;
    }
}

$q = trim(valeurTexte($_GET, 'q'));
$tris = ['pertinence' => 'p.en_vedette DESC, p.nom ASC', 'prix_asc' => 'p.prix ASC', 'prix_desc' => 'p.prix DESC', 'nom' => 'p.nom ASC'];
$tri = valeurTexte($_GET, 'tri');
$tri = array_key_exists($tri, $tris) ? $tri : 'pertinence';
$page = max(1, (int) ($_GET['page'] ?? 1));

$where = ['p.actif = 1'];
$params = [];
if ($categorie) {
    $where[] = 'p.category_id = ?';
    $params[] = $categorie['id'];
}
if ($q !== '') {
    $where[] = '(p.nom LIKE ? OR p.description_courte LIKE ?)';
    $params[] = '%' . $q . '%';
    $params[] = '%' . $q . '%';
}
$whereSql = implode(' AND ', $where);

$stmt = $pdo->prepare("SELECT COUNT(*) FROM products p WHERE $whereSql");
$stmt->execute($params);
$total = (int) $stmt->fetchColumn();
$nbPages = max(1, (int) ceil($total / PRODUITS_PAR_PAGE));
$page = min($page, $nbPages);
$offset = ($page - 1) * PRODUITS_PAR_PAGE;

$stmt = $pdo->prepare("SELECT p.* FROM products p WHERE $whereSql ORDER BY {$tris[$tri]} LIMIT " . PRODUITS_PAR_PAGE . " OFFSET $offset");
$stmt->execute($params);
$produits = $stmt->fetchAll();

$pageTitle = $categorie ? $categorie['nom'] : 'Tous nos produits';
$pageDescription = $categorie ? $categorie['description'] : 'Marinades, épices et essentiels de la cuisine ivoirienne.';
$pageActive = $categorie ? 'cat-' . $categorie['slug'] : '';

require_once __DIR__ . '/includes/header.php';
?>

<section class="bandeau-page bandeau-<?= e($categorie['slug'] ?? 'tous') ?>">
    <div class="conteneur">
        <nav class="fil-ariane" aria-label="Fil d’Ariane"><a href="<?= BASE_URL ?>">Accueil</a> / <?= e($pageTitle) ?></nav>
        <h1 class="titre-affiche"><?= e($pageTitle) ?></h1>
        <p><?= e($pageDescription) ?></p>
    </div>
</section>

<section class="section">
    <div class="conteneur">
        <div class="filtres">
            <nav class="filtres-gammes" aria-label="Gammes">
                <a href="<?= BASE_URL ?>boutique.php" class="pastille<?= $categorie ? '' : ' actif' ?>">Tout</a>
                <?php foreach ($categories as $c): ?>
                    <a href="<?= BASE_URL ?>boutique.php?categorie=<?= e($c['slug']) ?>" class="pastille<?= $categorie && $categorie['id'] === $c['id'] ? ' actif' : '' ?>"><?= e($c['nom']) ?></a>
                <?php endforeach; ?>
            </nav>
            <form method="get" class="filtres-recherche">
                <?php if ($categorie): ?><input type="hidden" name="categorie" value="<?= e($categorie['slug']) ?>"><?php endif; ?>
                <label class="visuellement-cache" for="recherche">Rechercher un produit</label>
                <input type="search" id="recherche" name="q" value="<?= e($q) ?>" placeholder="Rechercher un produit">
                <label class="visuellement-cache" for="tri">Trier</label>
                <select id="tri" name="tri" data-soumission-auto>
                    <option value="pertinence"<?= $tri === 'pertinence' ? ' selected' : '' ?>>Nos recommandations</option>
                    <option value="prix_asc"<?= $tri === 'prix_asc' ? ' selected' : '' ?>>Prix croissant</option>
                    <option value="prix_desc"<?= $tri === 'prix_desc' ? ' selected' : '' ?>>Prix décroissant</option>
                    <option value="nom"<?= $tri === 'nom' ? ' selected' : '' ?>>Nom (A à Z)</option>
                </select>
                <button type="submit" class="bouton bouton-bordeaux bouton-petit">Rechercher</button>
            </form>
        </div>

        <p class="resultats"><?= $total ?> produit<?= $total > 1 ? 's' : '' ?></p>

        <?php if ($produits): ?>
            <div class="grille-produits">
                <?php foreach ($produits as $p): ?>
                    <?= carteProduit($p) ?>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="etat-vide">
                <p>Aucun produit ne correspond à « <?= e($q) ?> ».</p>
                <a href="<?= BASE_URL ?>boutique.php" class="bouton bouton-bordeaux">Voir tous les produits</a>
            </div>
        <?php endif; ?>

        <?php if ($nbPages > 1): ?>
        <nav class="pagination" aria-label="Pages">
            <?php for ($i = 1; $i <= $nbPages; $i++): ?>
                <a href="?<?= e(http_build_query(array_merge($_GET, ['page' => $i]))) ?>"<?= $i === $page ? ' aria-current="page" class="actif"' : '' ?>><?= $i ?></a>
            <?php endfor; ?>
        </nav>
        <?php endif; ?>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
