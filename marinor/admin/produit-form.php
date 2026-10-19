<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();
$categories = $pdo->query('SELECT id, nom FROM categories ORDER BY ordre, nom')->fetchAll();
$id = (int) ($_GET['id'] ?? 0);

$produit = [
    'category_id' => $categories[0]['id'] ?? 0, 'nom' => '', 'slug' => '', 'description_courte' => '',
    'description' => '', 'ingredients' => '', 'conseils' => '', 'prix' => '', 'contenance' => '',
    'conditionnement' => 'sachet', 'stock' => 0, 'image' => null, 'actif' => 1, 'en_vedette' => 0,
];
if ($id) {
    $stmt = $pdo->prepare('SELECT * FROM products WHERE id = ?');
    $stmt->execute([$id]);
    $produit = $stmt->fetch();
    if (!$produit) {
        flash('erreur', 'Produit introuvable.');
        redirect(BASE_URL . 'admin/produits.php');
    }
}

$erreurs = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    foreach (['nom', 'description_courte', 'description', 'ingredients', 'conseils', 'contenance'] as $champ) {
        $produit[$champ] = trim((string) ($_POST[$champ] ?? ''));
    }
    $produit['category_id'] = (int) ($_POST['category_id'] ?? 0);
    $produit['prix'] = (int) ($_POST['prix'] ?? 0);
    $produit['stock'] = max(0, (int) ($_POST['stock'] ?? 0));
    $produit['conditionnement'] = in_array($_POST['conditionnement'] ?? '', ['pot', 'sachet', 'bidon'], true) ? $_POST['conditionnement'] : 'sachet';
    $produit['actif'] = isset($_POST['actif']) ? 1 : 0;
    $produit['en_vedette'] = isset($_POST['en_vedette']) ? 1 : 0;

    if (mb_strlen($produit['nom']) < 2 || mb_strlen($produit['nom']) > 80) {
        $erreurs['nom'] = 'Le nom doit contenir entre 2 et 80 caractères.';
    }
    if (!in_array($produit['category_id'], array_map('intval', array_column($categories, 'id')), true)) {
        $erreurs['category_id'] = 'Choisissez une gamme.';
    }
    if (mb_strlen($produit['description_courte']) < 10 || mb_strlen($produit['description_courte']) > 160) {
        $erreurs['description_courte'] = 'La présentation courte doit contenir entre 10 et 160 caractères.';
    }
    if (mb_strlen($produit['description']) < 20) {
        $erreurs['description'] = 'La description doit contenir au moins 20 caractères.';
    }
    if ($produit['prix'] < 100) {
        $erreurs['prix'] = 'Indiquez un prix en FCFA (100 minimum).';
    }

    $slug = slugify($produit['nom']);
    $stmt = $pdo->prepare('SELECT id FROM products WHERE slug = ? AND id <> ?');
    $stmt->execute([$slug, $id]);
    if ($stmt->fetch()) {
        $erreurs['nom'] = 'Un autre produit porte déjà ce nom.';
    }

    $nouvelleImage = null;
    if (!$erreurs && ($_FILES['image']['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
        try {
            $nouvelleImage = uploadImage($_FILES['image'], 'produits');
        } catch (RuntimeException $ex) {
            $erreurs['image'] = $ex->getMessage();
        }
    }

    if (!$erreurs) {
        $ancienneImage = $produit['image'];
        if ($nouvelleImage || isset($_POST['retirer_image'])) {
            $produit['image'] = $nouvelleImage;
        }
        $valeurs = [$produit['category_id'], $produit['nom'], $slug, $produit['description_courte'], $produit['description'],
                    $produit['ingredients'] ?: null, $produit['conseils'] ?: null, $produit['prix'], $produit['contenance'] ?: null,
                    $produit['conditionnement'], $produit['stock'], $produit['image'], $produit['actif'], $produit['en_vedette']];
        if ($id) {
            $pdo->prepare('UPDATE products SET category_id = ?, nom = ?, slug = ?, description_courte = ?, description = ?, ingredients = ?, conseils = ?,
                           prix = ?, contenance = ?, conditionnement = ?, stock = ?, image = ?, actif = ?, en_vedette = ? WHERE id = ?')
                ->execute(array_merge($valeurs, [$id]));
        } else {
            $pdo->prepare('INSERT INTO products (category_id, nom, slug, description_courte, description, ingredients, conseils,
                           prix, contenance, conditionnement, stock, image, actif, en_vedette) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
                ->execute($valeurs);
        }
        if ($ancienneImage !== $produit['image']) {
            supprimerImage($ancienneImage, 'produits');
        }
        flash('succes', 'Le produit « ' . $produit['nom'] . ' » a été enregistré.');
        redirect(BASE_URL . 'admin/produits.php');
    } elseif ($nouvelleImage) {
        supprimerImage($nouvelleImage, 'produits');
    }
}

$adminTitre = $id ? 'Modifier : ' . $produit['nom'] : 'Ajouter un produit';
$adminActif = 'produits.php';
require __DIR__ . '/_debut.php';

function erreurAdmin(array $erreurs, string $champ): string
{
    return isset($erreurs[$champ]) ? '<p class="erreur-champ">' . e($erreurs[$champ]) . '</p>' : '';
}
?>
<form method="post" enctype="multipart/form-data" class="formulaire-admin" novalidate>
    <?= champCSRF() ?>
    <section class="panneau">
        <h2>Informations</h2>
        <div class="champ"><label for="nom">Nom du produit</label><input id="nom" name="nom" value="<?= e($produit['nom']) ?>" maxlength="80" required><?= erreurAdmin($erreurs, 'nom') ?></div>
        <div class="champs-trio">
            <div class="champ"><label for="category_id">Gamme</label>
                <select id="category_id" name="category_id">
                    <?php foreach ($categories as $c): ?>
                        <option value="<?= (int) $c['id'] ?>"<?= (int) $produit['category_id'] === (int) $c['id'] ? ' selected' : '' ?>><?= e($c['nom']) ?></option>
                    <?php endforeach; ?>
                </select><?= erreurAdmin($erreurs, 'category_id') ?></div>
            <div class="champ"><label for="conditionnement">Conditionnement</label>
                <select id="conditionnement" name="conditionnement">
                    <?php foreach (['pot' => 'Pot', 'sachet' => 'Sachet', 'bidon' => 'Bidon'] as $v => $l): ?>
                        <option value="<?= $v ?>"<?= $produit['conditionnement'] === $v ? ' selected' : '' ?>><?= $l ?></option>
                    <?php endforeach; ?>
                </select></div>
            <div class="champ"><label for="contenance">Contenance (ex. 500 g)</label><input id="contenance" name="contenance" value="<?= e($produit['contenance']) ?>" maxlength="30"></div>
        </div>
        <div class="champ"><label for="description_courte">Présentation courte (160 caractères max.)</label><input id="description_courte" name="description_courte" value="<?= e($produit['description_courte']) ?>" maxlength="160" required><?= erreurAdmin($erreurs, 'description_courte') ?></div>
        <div class="champ"><label for="description">Description complète</label><textarea id="description" name="description" rows="5" required><?= e($produit['description']) ?></textarea><?= erreurAdmin($erreurs, 'description') ?></div>
        <div class="champ"><label for="ingredients">Ingrédients</label><textarea id="ingredients" name="ingredients" rows="3"><?= e($produit['ingredients']) ?></textarea></div>
        <div class="champ"><label for="conseils">Conseils d’utilisation</label><textarea id="conseils" name="conseils" rows="3"><?= e($produit['conseils']) ?></textarea></div>
    </section>

    <div class="pile">
        <section class="panneau">
            <h2>Prix et stock</h2>
            <div class="champ"><label for="prix">Prix (FCFA)</label><input id="prix" name="prix" type="number" min="100" step="50" value="<?= e($produit['prix']) ?>" required><?= erreurAdmin($erreurs, 'prix') ?></div>
            <div class="champ"><label for="stock">Quantité en stock</label><input id="stock" name="stock" type="number" min="0" value="<?= (int) $produit['stock'] ?>"></div>
            <label class="case"><input type="checkbox" name="actif"<?= $produit['actif'] ? ' checked' : '' ?>> Visible sur le site</label>
            <label class="case"><input type="checkbox" name="en_vedette"<?= $produit['en_vedette'] ? ' checked' : '' ?>> Afficher sur la page d’accueil</label>
        </section>
        <section class="panneau">
            <h2>Photo</h2>
            <img src="<?= e(imageProduit($produit)) ?>" alt="" class="apercu-image" data-apercu>
            <div class="champ"><label for="image">Nouvelle photo (JPG, PNG ou WEBP, 5 Mo max.)</label><input id="image" name="image" type="file" accept="image/jpeg,image/png,image/webp" data-fichier-apercu><?= erreurAdmin($erreurs, 'image') ?></div>
            <?php if ($produit['image']): ?><label class="case"><input type="checkbox" name="retirer_image"> Retirer la photo actuelle</label><?php endif; ?>
        </section>
        <button type="submit" class="bouton bouton-large">Enregistrer le produit</button>
        <a href="produits.php" class="lien-retour">Annuler</a>
    </div>
</form>
<?php require __DIR__ . '/_fin.php';
