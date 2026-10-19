<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$adminTitre = 'Tableau de bord';
$adminActif = 'index.php';
$pdo = getDB();

$chiffres = [
    'Paiements à vérifier' => (int) $pdo->query("SELECT COUNT(*) FROM payments WHERE statut = 'en_verification'")->fetchColumn(),
    'Commandes à préparer' => (int) $pdo->query("SELECT COUNT(*) FROM orders WHERE statut IN ('payee','en_preparation')")->fetchColumn(),
    'Ventes encaissées'    => formatPrix((int) $pdo->query("SELECT COALESCE(SUM(total),0) FROM orders WHERE statut IN ('payee','en_preparation','expediee','livree')")->fetchColumn()),
    'Clients inscrits'     => (int) $pdo->query('SELECT COUNT(*) FROM users')->fetchColumn(),
];
$dernieres = $pdo->query(
    'SELECT o.reference, o.nom_livraison, o.total, o.statut, o.created_at, pay.statut AS paiement_statut
     FROM orders o JOIN payments pay ON pay.order_id = o.id ORDER BY o.created_at DESC LIMIT 8'
)->fetchAll();
$stockBas = $pdo->query('SELECT id, nom, stock FROM products WHERE actif = 1 AND stock <= 5 ORDER BY stock ASC LIMIT 8')->fetchAll();
$messages = $pdo->query('SELECT id, nom, sujet, created_at FROM messages WHERE lu = 0 ORDER BY created_at DESC LIMIT 5')->fetchAll();

require __DIR__ . '/_debut.php';
?>
<section class="chiffres">
    <?php foreach ($chiffres as $libelle => $valeur): ?>
        <div class="chiffre"><strong><?= e($valeur) ?></strong><span><?= e($libelle) ?></span></div>
    <?php endforeach; ?>
</section>

<div class="grille-admin">
    <section class="panneau">
        <h2>Dernières commandes</h2>
        <?php if (!$dernieres): ?>
            <p class="vide">Aucune commande pour le moment.</p>
        <?php else: ?>
        <table class="tableau">
            <thead><tr><th>Référence</th><th>Client</th><th>Total</th><th>Paiement</th><th>Statut</th></tr></thead>
            <tbody>
            <?php foreach ($dernieres as $c): ?>
                <tr>
                    <td><a href="commande.php?ref=<?= e($c['reference']) ?>"><?= e($c['reference']) ?></a></td>
                    <td><?= e($c['nom_livraison']) ?></td>
                    <td><?= formatPrix((int) $c['total']) ?></td>
                    <td><span class="statut statut-<?= e($c['paiement_statut']) ?>"><?= e(libelleStatutPaiement($c['paiement_statut'])) ?></span></td>
                    <td><?= e(libelleStatutCommande($c['statut'])) ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php endif; ?>
    </section>

    <div class="pile">
        <section class="panneau">
            <h2>Stock faible</h2>
            <?php if (!$stockBas): ?>
                <p class="vide">Tous les produits ont plus de 5 unités en stock.</p>
            <?php else: ?>
                <ul class="liste">
                    <?php foreach ($stockBas as $p): ?>
                        <li><a href="produit-form.php?id=<?= (int) $p['id'] ?>"><?= e($p['nom']) ?></a><span class="statut statut-refuse"><?= (int) $p['stock'] ?> en stock</span></li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </section>
        <section class="panneau">
            <h2>Messages non lus</h2>
            <?php if (!$messages): ?>
                <p class="vide">Aucun nouveau message.</p>
            <?php else: ?>
                <ul class="liste">
                    <?php foreach ($messages as $m): ?>
                        <li><a href="messages.php#message-<?= (int) $m['id'] ?>"><?= e($m['nom']) ?> : <?= e($m['sujet']) ?></a><span><?= formatDate($m['created_at']) ?></span></li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </section>
    </div>
</div>
<?php require __DIR__ . '/_fin.php';
