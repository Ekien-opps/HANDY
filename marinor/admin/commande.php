<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();
$reference = (string) ($_GET['ref'] ?? '');
$stmt = $pdo->prepare(
    'SELECT o.*, pay.id AS paiement_id, pay.methode, pay.montant, pay.numero_payeur, pay.reference_transaction,
            pay.statut AS paiement_statut, pay.validated_at, u.email AS client_email
     FROM orders o JOIN payments pay ON pay.order_id = o.id LEFT JOIN users u ON u.id = o.user_id
     WHERE o.reference = ?'
);
$stmt->execute([$reference]);
$commande = $stmt->fetch();
if (!$commande) {
    flash('erreur', 'Commande introuvable.');
    redirect(BASE_URL . 'admin/commandes.php');
}

$statuts = ['en_attente', 'payee', 'en_preparation', 'expediee', 'livree', 'annulee'];

/** Remet en stock les produits d'une commande annulée. */
function remettreEnStock(PDO $pdo, int $orderId): void
{
    $pdo->prepare('UPDATE products p JOIN order_items i ON i.product_id = p.id SET p.stock = p.stock + i.quantite WHERE i.order_id = ?')
        ->execute([$orderId]);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $action = $_POST['action'] ?? '';
    $pdo->beginTransaction();

    if ($action === 'valider_paiement' && $commande['paiement_statut'] !== 'valide') {
        $pdo->prepare("UPDATE payments SET statut = 'valide', validated_at = NOW() WHERE id = ?")->execute([$commande['paiement_id']]);
        if ($commande['statut'] === 'en_attente') {
            $pdo->prepare("UPDATE orders SET statut = 'payee' WHERE id = ?")->execute([$commande['id']]);
        }
        flash('succes', 'Paiement validé : la commande peut être préparée.');
    } elseif ($action === 'refuser_paiement' && $commande['paiement_statut'] !== 'valide') {
        $pdo->prepare("UPDATE payments SET statut = 'refuse' WHERE id = ?")->execute([$commande['paiement_id']]);
        flash('succes', 'Paiement refusé. Pensez à prévenir le client.');
    } elseif ($action === 'statut') {
        $nouveau = $_POST['statut'] ?? '';
        if (in_array($nouveau, $statuts, true) && $nouveau !== $commande['statut']) {
            if ($nouveau === 'annulee') {
                remettreEnStock($pdo, (int) $commande['id']);
            } elseif ($commande['statut'] === 'annulee') {
                flash('erreur', 'Une commande annulée ne peut pas être réactivée : demandez au client de commander à nouveau.');
                $pdo->rollBack();
                redirect(BASE_URL . 'admin/commande.php?ref=' . $commande['reference']);
            }
            $pdo->prepare('UPDATE orders SET statut = ? WHERE id = ?')->execute([$nouveau, $commande['id']]);
            flash('succes', 'Statut mis à jour : ' . libelleStatutCommande($nouveau) . '.');
        }
    }

    $pdo->commit();
    redirect(BASE_URL . 'admin/commande.php?ref=' . $commande['reference']);
}

$lignes = $pdo->prepare('SELECT * FROM order_items WHERE order_id = ?');
$lignes->execute([$commande['id']]);
$lignes = $lignes->fetchAll();

$adminTitre = 'Commande ' . $commande['reference'];
$adminActif = 'commandes.php';
require __DIR__ . '/_debut.php';
?>
<a href="commandes.php" class="lien-retour">Toutes les commandes</a>

<div class="grille-admin">
    <section class="panneau">
        <h2>Articles</h2>
        <table class="tableau">
            <thead><tr><th>Produit</th><th>Prix unitaire</th><th>Quantité</th><th>Total</th></tr></thead>
            <tbody>
            <?php foreach ($lignes as $l): ?>
                <tr><td><?= e($l['nom_produit']) ?></td><td><?= formatPrix((int) $l['prix_unitaire']) ?></td><td><?= (int) $l['quantite'] ?></td><td><?= formatPrix((int) $l['total_ligne']) ?></td></tr>
            <?php endforeach; ?>
            </tbody>
            <tfoot>
                <tr><td colspan="3">Livraison</td><td><?= formatPrix((int) $commande['frais_livraison']) ?></td></tr>
                <tr><td colspan="3"><strong>Total</strong></td><td><strong><?= formatPrix((int) $commande['total']) ?></strong></td></tr>
            </tfoot>
        </table>

        <h2>Livraison</h2>
        <dl class="details">
            <dt>Destinataire</dt><dd><?= e($commande['nom_livraison']) ?></dd>
            <dt>Téléphone</dt><dd><a href="tel:<?= e(preg_replace('/\s/', '', $commande['telephone_livraison'])) ?>"><?= e($commande['telephone_livraison']) ?></a></dd>
            <dt>Adresse</dt><dd><?= e($commande['adresse_livraison']) ?>, <?= e($commande['commune']) ?>, <?= e($commande['ville']) ?></dd>
            <?php if ($commande['instructions']): ?><dt>Instructions</dt><dd><?= e($commande['instructions']) ?></dd><?php endif; ?>
            <dt>Compte client</dt><dd><?= $commande['client_email'] ? e($commande['client_email']) : 'Compte supprimé' ?></dd>
            <dt>Passée le</dt><dd><?= formatDate($commande['created_at'], true) ?></dd>
        </dl>
    </section>

    <div class="pile">
        <section class="panneau">
            <h2>Paiement</h2>
            <dl class="details">
                <dt>Moyen</dt><dd><?= e(libelleMethodePaiement($commande['methode'])) ?></dd>
                <dt>Montant attendu</dt><dd><?= formatPrix((int) $commande['montant']) ?></dd>
                <dt>Numéro payeur</dt><dd><?= e($commande['numero_payeur'] ?: 'Non renseigné') ?></dd>
                <dt>Référence</dt><dd><?= e($commande['reference_transaction'] ?: 'Non renseignée') ?></dd>
                <dt>Statut</dt><dd><span class="statut statut-<?= e($commande['paiement_statut']) ?>"><?= e(libelleStatutPaiement($commande['paiement_statut'])) ?></span></dd>
            </dl>
            <?php if ($commande['paiement_statut'] !== 'valide'): ?>
                <p class="aide">Vérifiez la réception de <?= formatPrix((int) $commande['montant']) ?> sur votre compte <?= e(libelleMethodePaiement($commande['methode'])) ?> avant de valider.</p>
                <div class="groupe-boutons">
                    <form method="post"><?= champCSRF() ?><input type="hidden" name="action" value="valider_paiement"><button class="bouton">Valider le paiement</button></form>
                    <form method="post" data-confirmation="Refuser ce paiement ?"><?= champCSRF() ?><input type="hidden" name="action" value="refuser_paiement"><button class="bouton bouton-secondaire">Refuser</button></form>
                </div>
            <?php endif; ?>
        </section>

        <section class="panneau">
            <h2>Statut de la commande</h2>
            <form method="post" class="formulaire-ligne">
                <?= champCSRF() ?>
                <input type="hidden" name="action" value="statut">
                <label class="visuellement-cache" for="statut">Statut</label>
                <select id="statut" name="statut">
                    <?php foreach ($statuts as $s): ?>
                        <option value="<?= $s ?>"<?= $commande['statut'] === $s ? ' selected' : '' ?>><?= e(libelleStatutCommande($s)) ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="bouton">Mettre à jour</button>
            </form>
            <p class="aide">Passer une commande en « Annulée » remet automatiquement ses produits en stock.</p>
        </section>
    </div>
</div>
<?php require __DIR__ . '/_fin.php';
