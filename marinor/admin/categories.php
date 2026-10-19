<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $action = $_POST['action'] ?? '';
    $id = (int) ($_POST['id'] ?? 0);
    $nom = trim((string) ($_POST['nom'] ?? ''));
    $description = trim((string) ($_POST['description'] ?? ''));
    $ordre = max(0, min(255, (int) ($_POST['ordre'] ?? 0)));

    if (in_array($action, ['ajouter', 'modifier'], true)) {
        $slug = slugify($nom);
        $stmt = $pdo->prepare('SELECT id FROM categories WHERE slug = ? AND id <> ?');
        $stmt->execute([$slug, $id]);
        if (mb_strlen($nom) < 2 || mb_strlen($nom) > 60) {
            flash('erreur', 'Le nom de la gamme doit contenir entre 2 et 60 caractères.');
        } elseif ($stmt->fetch()) {
            flash('erreur', 'Une gamme porte déjà ce nom.');
        } elseif ($action === 'ajouter') {
            $pdo->prepare('INSERT INTO categories (nom, slug, description, ordre) VALUES (?, ?, ?, ?)')->execute([$nom, $slug, $description ?: null, $ordre]);
            flash('succes', 'Gamme ajoutée.');
        } else {
            $pdo->prepare('UPDATE categories SET nom = ?, slug = ?, description = ?, ordre = ? WHERE id = ?')->execute([$nom, $slug, $description ?: null, $ordre, $id]);
            flash('succes', 'Gamme mise à jour.');
        }
    } elseif ($action === 'supprimer') {
        $stmt = $pdo->prepare('SELECT COUNT(*) FROM products WHERE category_id = ?');
        $stmt->execute([$id]);
        if ((int) $stmt->fetchColumn() > 0) {
            flash('erreur', 'Cette gamme contient encore des produits : déplacez-les ou supprimez-les d’abord.');
        } else {
            $pdo->prepare('DELETE FROM categories WHERE id = ?')->execute([$id]);
            flash('succes', 'Gamme supprimée.');
        }
    }
    redirect(BASE_URL . 'admin/categories.php');
}

$categories = $pdo->query(
    'SELECT c.*, COUNT(p.id) AS nb FROM categories c LEFT JOIN products p ON p.category_id = c.id GROUP BY c.id ORDER BY c.ordre, c.nom'
)->fetchAll();

$adminTitre = 'Gammes de produits';
$adminActif = 'categories.php';
require __DIR__ . '/_debut.php';
?>
<section class="panneau">
    <h2>Gammes existantes</h2>
    <?php foreach ($categories as $c): ?>
    <div class="ligne-edition">
        <form method="post" class="formulaire-ligne">
            <?= champCSRF() ?>
            <input type="hidden" name="action" value="modifier">
            <input type="hidden" name="id" value="<?= (int) $c['id'] ?>">
            <div class="champ"><label>Nom</label><input name="nom" value="<?= e($c['nom']) ?>" required></div>
            <div class="champ champ-large"><label>Description</label><input name="description" value="<?= e($c['description']) ?>"></div>
            <div class="champ champ-court"><label>Ordre</label><input name="ordre" type="number" min="0" value="<?= (int) $c['ordre'] ?>"></div>
            <button type="submit" class="bouton bouton-secondaire">Enregistrer</button>
        </form>
        <form method="post" data-confirmation="Supprimer la gamme « <?= e($c['nom']) ?> » ?">
            <?= champCSRF() ?>
            <input type="hidden" name="action" value="supprimer">
            <input type="hidden" name="id" value="<?= (int) $c['id'] ?>">
            <button type="submit" class="lien-danger"<?= $c['nb'] ? ' disabled title="Gamme non vide"' : '' ?>>Supprimer</button>
        </form>
        <span class="aide"><?= (int) $c['nb'] ?> produit(s)</span>
    </div>
    <?php endforeach; ?>
</section>

<section class="panneau">
    <h2>Ajouter une gamme</h2>
    <form method="post" class="formulaire-ligne">
        <?= champCSRF() ?>
        <input type="hidden" name="action" value="ajouter">
        <div class="champ"><label for="nouveau-nom">Nom</label><input id="nouveau-nom" name="nom" required></div>
        <div class="champ champ-large"><label for="nouvelle-description">Description</label><input id="nouvelle-description" name="description"></div>
        <div class="champ champ-court"><label for="nouvel-ordre">Ordre</label><input id="nouvel-ordre" name="ordre" type="number" min="0" value="<?= count($categories) + 1 ?>"></div>
        <button type="submit" class="bouton">Ajouter la gamme</button>
    </form>
</section>
<?php require __DIR__ . '/_fin.php';
