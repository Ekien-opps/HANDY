<?php
require_once __DIR__ . '/includes/functions.php';

$client = exigerClient();
$pdo = getDB();

$stmt = $pdo->prepare(
    'SELECT o.*, pay.id AS paiement_id, pay.methode, pay.statut AS paiement_statut, pay.reference_transaction
     FROM orders o JOIN payments pay ON pay.order_id = o.id
     WHERE o.reference = ? AND o.user_id = ?'
);
$stmt->execute([(string) ($_GET['ref'] ?? ''), $client['id']]);
$commande = $stmt->fetch();

if (!$commande) {
    flash('erreur', 'Commande introuvable.');
    redirect(BASE_URL . 'compte.php');
}

$erreurs = [];
$numeroPayeur = '';
$referenceTransaction = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $commande['paiement_statut'] === 'en_attente') {
    exigerCSRF();
    $numeroPayeur = trim((string) ($_POST['numero_payeur'] ?? ''));
    $referenceTransaction = trim((string) ($_POST['reference_transaction'] ?? ''));

    if (!telephoneValide($numeroPayeur)) {
        $erreurs['numero_payeur'] = 'Indiquez le numéro qui a effectué le paiement (10 chiffres).';
    }
    if (!preg_match('/^[A-Za-z0-9.\-]{4,60}$/', $referenceTransaction)) {
        $erreurs['reference_transaction'] = 'Recopiez la référence figurant dans le SMS de confirmation.';
    }
    if (!$erreurs) {
        $pdo->prepare("UPDATE payments SET numero_payeur = ?, reference_transaction = ?, statut = 'en_verification' WHERE id = ? AND statut = 'en_attente'")
            ->execute([$numeroPayeur, $referenceTransaction, $commande['paiement_id']]);
        flash('succes', 'Merci ! Votre paiement est en cours de vérification. Vous serez contacté pour la livraison.');
        redirect(BASE_URL . 'paiement.php?ref=' . $commande['reference']);
    }
}

$lignes = $pdo->prepare('SELECT * FROM order_items WHERE order_id = ?');
$lignes->execute([$commande['id']]);
$lignes = $lignes->fetchAll();

$pageTitle = 'Paiement de la commande ' . $commande['reference'];
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur conteneur-etroit">
        <ol class="tunnel" aria-label="Étapes de la commande">
            <li class="fait">Panier</li>
            <li class="fait">Livraison et paiement</li>
            <li class="en-cours" aria-current="step">Confirmation</li>
        </ol>

        <h1 class="titre-affiche">Commande <?= e($commande['reference']) ?></h1>

        <?php if ($commande['paiement_statut'] === 'en_attente'): ?>
            <div class="encart-paiement">
                <h2>Finalisez votre paiement par <?= e(libelleMethodePaiement($commande['methode'])) ?></h2>
                <ol class="etapes-paiement">
                    <li>Ouvrez votre application <?= e(libelleMethodePaiement($commande['methode'])) ?>.</li>
                    <li>Envoyez exactement <strong><?= formatPrix((int) $commande['total']) ?></strong> au numéro <strong><?= e(numeroPaiement($commande['methode'])) ?></strong>.</li>
                    <li>Indiquez en motif la référence <strong><?= e($commande['reference']) ?></strong>.</li>
                    <li>Recopiez ci-dessous la référence reçue par SMS.</li>
                </ol>

                <form method="post" class="formulaire" novalidate>
                    <?= champCSRF() ?>
                    <div class="champ">
                        <label for="numero_payeur">Numéro qui a payé</label>
                        <input id="numero_payeur" name="numero_payeur" type="tel" value="<?= e($numeroPayeur) ?>" required placeholder="07 00 00 00 00">
                        <?php if (isset($erreurs['numero_payeur'])): ?><p class="erreur-champ"><?= e($erreurs['numero_payeur']) ?></p><?php endif; ?>
                    </div>
                    <div class="champ">
                        <label for="reference_transaction">Référence de la transaction</label>
                        <input id="reference_transaction" name="reference_transaction" value="<?= e($referenceTransaction) ?>" required>
                        <?php if (isset($erreurs['reference_transaction'])): ?><p class="erreur-champ"><?= e($erreurs['reference_transaction']) ?></p><?php endif; ?>
                    </div>
                    <button type="submit" class="bouton bouton-bordeaux bouton-large">Confirmer mon paiement</button>
                </form>
            </div>
        <?php else: ?>
            <div class="encart-confirmation">
                <h2><?= $commande['paiement_statut'] === 'valide' ? 'Paiement validé' : ($commande['paiement_statut'] === 'refuse' ? 'Paiement refusé' : 'Paiement en cours de vérification') ?></h2>
                <p>
                    <?php if ($commande['paiement_statut'] === 'refuse'): ?>
                        Nous n’avons pas pu confirmer votre paiement. Contactez-nous en indiquant la référence <?= e($commande['reference']) ?>.
                    <?php else: ?>
                        Statut de la commande : <strong><?= e(libelleStatutCommande($commande['statut'])) ?></strong>. Nous vous appellerons au <?= e($commande['telephone_livraison']) ?> pour la livraison.
                    <?php endif; ?>
                </p>
                <a href="<?= BASE_URL ?>compte.php" class="bouton bouton-bordeaux">Suivre mes commandes</a>
            </div>
        <?php endif; ?>

        <div class="recap recap-plein">
            <h2>Récapitulatif</h2>
            <ul class="recap-lignes">
                <?php foreach ($lignes as $l): ?>
                    <li><span><?= (int) $l['quantite'] ?> × <?= e($l['nom_produit']) ?></span><span><?= formatPrix((int) $l['total_ligne']) ?></span></li>
                <?php endforeach; ?>
            </ul>
            <dl>
                <dt>Livraison</dt><dd><?= (int) $commande['frais_livraison'] === 0 ? 'Offerte' : formatPrix((int) $commande['frais_livraison']) ?></dd>
                <dt class="recap-total">Total</dt><dd class="recap-total"><?= formatPrix((int) $commande['total']) ?></dd>
            </dl>
            <p class="aide">Livraison à : <?= e($commande['nom_livraison']) ?>, <?= e($commande['adresse_livraison']) ?>, <?= e($commande['commune']) ?></p>
        </div>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
