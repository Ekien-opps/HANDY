<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();
$statuts = ['en_attente', 'payee', 'en_preparation', 'expediee', 'livree', 'annulee'];
$filtre = in_array($_GET['statut'] ?? '', $statuts, true) ? $_GET['statut'] : '';
$aVerifier = isset($_GET['a_verifier']);

$where = ['1 = 1'];
$params = [];
if ($filtre) {
    $where[] = 'o.statut = ?';
    $params[] = $filtre;
}
if ($aVerifier) {
    $where[] = "pay.statut = 'en_verification'";
}
$stmt = $pdo->prepare(
    'SELECT o.*, pay.methode, pay.statut AS paiement_statut FROM orders o JOIN payments pay ON pay.order_id = o.id
     WHERE ' . implode(' AND ', $where) . ' ORDER BY o.created_at DESC LIMIT 200'
);
$stmt->execute($params);
$commandes = $stmt->fetchAll();

$adminTitre = 'Commandes';
$adminActif = 'commandes.php';
require __DIR__ . '/_debut.php';
?>
<nav class="filtres-pastilles" aria-label="Filtrer les commandes">
    <a href="commandes.php"<?= !$filtre && !$aVerifier ? ' aria-current="page"' : '' ?>>Toutes</a>
    <a href="commandes.php?a_verifier=1"<?= $aVerifier ? ' aria-current="page"' : '' ?>>Paiements à vérifier</a>
    <?php foreach ($statuts as $s): ?>
        <a href="commandes.php?statut=<?= $s ?>"<?= $filtre === $s ? ' aria-current="page"' : '' ?>><?= e(libelleStatutCommande($s)) ?></a>
    <?php endforeach; ?>
</nav>

<section class="panneau">
    <table class="tableau">
        <thead><tr><th>Référence</th><th>Date</th><th>Client</th><th>Commune</th><th>Total</th><th>Paiement</th><th>Statut</th></tr></thead>
        <tbody>
        <?php foreach ($commandes as $c): ?>
            <tr>
                <td><a href="commande.php?ref=<?= e($c['reference']) ?>"><strong><?= e($c['reference']) ?></strong></a></td>
                <td><?= formatDate($c['created_at'], true) ?></td>
                <td><?= e($c['nom_livraison']) ?><br><small><?= e($c['telephone_livraison']) ?></small></td>
                <td><?= e($c['commune']) ?></td>
                <td><?= formatPrix((int) $c['total']) ?></td>
                <td><?= e(libelleMethodePaiement($c['methode'])) ?><br><span class="statut statut-<?= e($c['paiement_statut']) ?>"><?= e(libelleStatutPaiement($c['paiement_statut'])) ?></span></td>
                <td><span class="statut statut-<?= e($c['statut']) ?>"><?= e(libelleStatutCommande($c['statut'])) ?></span></td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php if (!$commandes): ?><p class="vide">Aucune commande dans cette catégorie.</p><?php endif; ?>
</section>
<?php require __DIR__ . '/_fin.php';
