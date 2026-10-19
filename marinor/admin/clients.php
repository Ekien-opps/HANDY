<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();
$q = trim((string) ($_GET['q'] ?? ''));
$params = [];
$where = '';
if ($q !== '') {
    $where = 'WHERE u.nom LIKE ? OR u.prenom LIKE ? OR u.email LIKE ? OR u.telephone LIKE ?';
    $params = array_fill(0, 4, '%' . $q . '%');
}
$stmt = $pdo->prepare(
    "SELECT u.*, COUNT(o.id) AS nb_commandes,
            COALESCE(SUM(CASE WHEN o.statut IN ('payee','en_preparation','expediee','livree') THEN o.total END), 0) AS total_achats
     FROM users u LEFT JOIN orders o ON o.user_id = u.id $where
     GROUP BY u.id ORDER BY u.created_at DESC"
);
$stmt->execute($params);
$clients = $stmt->fetchAll();
$nbAbonnes = (int) $pdo->query('SELECT COUNT(*) FROM subscribers')->fetchColumn();

$adminTitre = 'Clients';
$adminActif = 'clients.php';
require __DIR__ . '/_debut.php';
?>
<div class="barre-outils">
    <form method="get" class="filtres-admin">
        <label class="visuellement-cache" for="q">Rechercher</label>
        <input id="q" name="q" value="<?= e($q) ?>" placeholder="Nom, e-mail ou téléphone">
        <button type="submit" class="bouton bouton-secondaire">Rechercher</button>
    </form>
    <span class="aide"><?= count($clients) ?> client(s), <?= $nbAbonnes ?> abonné(s) à la lettre d’information</span>
</div>

<section class="panneau">
    <table class="tableau">
        <thead><tr><th>Client</th><th>Contact</th><th>Commune</th><th>Commandes</th><th>Total acheté</th><th>Inscrit le</th></tr></thead>
        <tbody>
        <?php foreach ($clients as $c): ?>
            <tr>
                <td><strong><?= e($c['prenom'] . ' ' . $c['nom']) ?></strong></td>
                <td><a href="mailto:<?= e($c['email']) ?>"><?= e($c['email']) ?></a><br><small><?= e($c['telephone']) ?></small></td>
                <td><?= e($c['commune'] ?: '—') ?></td>
                <td><?= (int) $c['nb_commandes'] ?></td>
                <td><?= formatPrix((int) $c['total_achats']) ?></td>
                <td><?= formatDate($c['created_at']) ?></td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php if (!$clients): ?><p class="vide">Aucun client trouvé.</p><?php endif; ?>
</section>
<?php require __DIR__ . '/_fin.php';
