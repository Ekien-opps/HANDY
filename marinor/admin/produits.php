<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $id = (int) ($_POST['id'] ?? 0);
    $action = $_POST['action'] ?? '';

    if ($action === 'basculer') {
        $pdo->prepare('UPDATE products SET actif = 1 - actif WHERE id = ?')->execute([$id]);
        flash('succes', 'Visibilité du produit mise à jour.');
    } elseif ($action === 'supprimer') {
        $stmt = $pdo->prepare('SELECT image FROM products WHERE id = ?');
        $stmt->execute([$id]);
        if ($produit = $stmt->fetch()) {
            // Les lignes de commandes passées conservent le nom et le prix (product_id passe à NULL)
            $pdo->prepare('DELETE FROM products WHERE id = ?')->execute([$id]);
            supprimerImage($produit['image'], 'produits');
            flash('succes', 'Produit supprimé.');
        }
    }
    redirect(BASE_URL . 'admin/produits.php');
}

$categories = $pdo->query('SELECT id, nom FROM categories ORDER BY ordre, nom')->fetchAll();
$filtreCategorie = (int) ($_GET['categorie'] ?? 0);
$q = trim(valeurTexte($_GET, 'q'));

$where = ['1 = 1'];
$params = [];
if ($filtreCategorie) {
    $where[] = 'p.category_id = ?';
    $params[] = $filtreCategorie;
}
if ($q !== '') {
    $where[] = 'p.nom LIKE ?';
    $params[] = '%' . $q . '%';
}
$stmt = $pdo->prepare('SELECT p.*, c.nom AS categorie_nom FROM products p JOIN categories c ON c.id = p.category_id WHERE '
    . implode(' AND ', $where) . ' ORDER BY c.ordre, p.nom');
$stmt->execute($params);
$produits = $stmt->fetchAll();

$adminTitre = 'Produits';
$adminActif = 'produits.php';
require __DIR__ . '/_debut.php';
?>
<div class="barre-outils">
    <form method="get" class="filtres-admin">
        <label class="visuellement-cache" for="q">Rechercher</label>
        <input id="q" name="q" value="<?= e($q) ?>" placeholder="Rechercher un produit">
        <label class="visuellement-cache" for="categorie">Gamme</label>
        <select id="categorie" name="categorie">
            <option value="0">Toutes les gammes</option>
            <?php foreach ($categories as $c): ?>
                <option value="<?= (int) $c['id'] ?>"<?= $filtreCategorie === (int) $c['id'] ? ' selected' : '' ?>><?= e($c['nom']) ?></option>
            <?php endforeach; ?>
        </select>
        <button type="submit" class="bouton bouton-secondaire">Filtrer</button>
    </form>
    <a href="produit-form.php" class="bouton">Ajouter un produit</a>
</div>

<section class="panneau">
    <table class="tableau">
        <thead><tr><th></th><th>Produit</th><th>Gamme</th><th>Prix</th><th>Stock</th><th>Visible</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($produits as $p): ?>
            <tr>
                <td><img src="<?= e(imageProduit($p)) ?>" alt="" class="miniature"></td>
                <td><strong><?= e($p['nom']) ?></strong><?= $p['en_vedette'] ? ' <span class="statut statut-valide">Vedette</span>' : '' ?></td>
                <td><?= e($p['categorie_nom']) ?></td>
                <td><?= formatPrix((int) $p['prix']) ?></td>
                <td><span class="<?= (int) $p['stock'] <= 5 ? 'texte-alerte' : '' ?>"><?= (int) $p['stock'] ?></span></td>
                <td>
                    <form method="post">
                        <?= champCSRF() ?>
                        <input type="hidden" name="id" value="<?= (int) $p['id'] ?>">
                        <input type="hidden" name="action" value="basculer">
                        <button type="submit" class="interrupteur" aria-pressed="<?= $p['actif'] ? 'true' : 'false' ?>"><?= $p['actif'] ? 'En ligne' : 'Masqué' ?></button>
                    </form>
                </td>
                <td class="actions">
                    <a href="produit-form.php?id=<?= (int) $p['id'] ?>">Modifier</a>
                    <form method="post" data-confirmation="Supprimer définitivement « <?= e($p['nom']) ?> » ?">
                        <?= champCSRF() ?>
                        <input type="hidden" name="id" value="<?= (int) $p['id'] ?>">
                        <input type="hidden" name="action" value="supprimer">
                        <button type="submit" class="lien-danger">Supprimer</button>
                    </form>
                </td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php if (!$produits): ?><p class="vide">Aucun produit ne correspond à ces filtres.</p><?php endif; ?>
</section>
<?php require __DIR__ . '/_fin.php';
