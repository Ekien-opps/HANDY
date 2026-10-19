<?php
require_once __DIR__ . '/includes/functions.php';

$ajax = ($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') === 'fetch';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
        if ($ajax) {
            http_response_code(419);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['ok' => false, 'message' => 'Votre session a expiré. Rechargez la page.']);
            exit;
        }
        flash('erreur', 'Votre session a expiré. Veuillez réessayer.');
        redirect(BASE_URL . 'panier.php');
    }

    $action = $_POST['action'] ?? '';
    $produitId = (int) ($_POST['produit_id'] ?? 0);
    $quantite = (int) ($_POST['quantite'] ?? 1);
    $message = '';
    $ok = true;

    switch ($action) {
        case 'ajouter':
            $avant = panierBrut()[$produitId] ?? 0;
            $apres = panierAjouter($produitId, max(1, $quantite));
            if ($apres === 0) {
                $ok = false;
                $message = "Ce produit n'est plus disponible.";
            } elseif ($apres === $avant) {
                $message = 'Quantité maximale atteinte pour ce produit.';
            } else {
                $message = 'Produit ajouté au panier.';
            }
            break;
        case 'modifier':
            panierModifier($produitId, $quantite);
            $message = 'Panier mis à jour.';
            break;
        case 'retirer':
            panierRetirer($produitId);
            $message = 'Produit retiré du panier.';
            break;
        case 'vider':
            panierVider();
            $message = 'Votre panier est vide.';
            break;
        default:
            $ok = false;
            $message = 'Action inconnue.';
    }

    if ($ajax) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $message, 'nombre' => panierNombreArticles()]);
        exit;
    }
    flash($ok ? 'succes' : 'erreur', $message);
    $retour = (string) ($_SERVER['HTTP_REFERER'] ?? '');
    redirect($action === 'ajouter' && str_starts_with($retour, BASE_URL) ? $retour : BASE_URL . 'panier.php');
}

$panier = panierDetails();
$seuil = (int) getParam('livraison_offerte_des', '0');
$pageTitle = 'Mon panier';
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur">
        <h1 class="titre-affiche">Mon panier</h1>

        <?php if (!$panier['lignes']): ?>
            <div class="etat-vide">
                <p>Votre panier est vide pour le moment.</p>
                <a href="<?= BASE_URL ?>boutique.php" class="bouton bouton-bordeaux">Découvrir nos produits</a>
            </div>
        <?php else: ?>
        <div class="panier">
            <div class="panier-lignes">
                <?php foreach ($panier['lignes'] as $l): $p = $l['produit']; ?>
                <div class="panier-ligne">
                    <img src="<?= e(imageProduit($p)) ?>" alt="" width="88" height="88">
                    <div class="panier-ligne-infos">
                        <a href="<?= BASE_URL ?>product.php?slug=<?= e($p['slug']) ?>" class="panier-ligne-nom"><?= e($p['nom']) ?></a>
                        <span class="panier-ligne-prix"><?= formatPrix((int) $p['prix']) ?> l’unité</span>
                    </div>
                    <form method="post" class="panier-ligne-quantite">
                        <?= champCSRF() ?>
                        <input type="hidden" name="action" value="modifier">
                        <input type="hidden" name="produit_id" value="<?= (int) $p['id'] ?>">
                        <label class="visuellement-cache" for="qte-<?= (int) $p['id'] ?>">Quantité de <?= e($p['nom']) ?></label>
                        <input type="number" id="qte-<?= (int) $p['id'] ?>" name="quantite" value="<?= $l['quantite'] ?>" min="0" max="<?= min((int) $p['stock'], QUANTITE_MAX_PAR_PRODUIT) ?>" data-soumission-auto>
                        <noscript><button type="submit" class="bouton bouton-petit bouton-contour">Mettre à jour</button></noscript>
                    </form>
                    <strong class="panier-ligne-total"><?= formatPrix($l['total']) ?></strong>
                    <form method="post">
                        <?= champCSRF() ?>
                        <input type="hidden" name="action" value="retirer">
                        <input type="hidden" name="produit_id" value="<?= (int) $p['id'] ?>">
                        <button type="submit" class="bouton-texte">Retirer</button>
                    </form>
                </div>
                <?php endforeach; ?>

                <div class="panier-pied">
                    <a href="<?= BASE_URL ?>boutique.php" class="lien-fort">Continuer mes achats</a>
                    <form method="post">
                        <?= champCSRF() ?>
                        <input type="hidden" name="action" value="vider">
                        <button type="submit" class="bouton-texte">Vider le panier</button>
                    </form>
                </div>
            </div>

            <aside class="recap">
                <h2>Récapitulatif</h2>
                <dl>
                    <dt>Sous-total</dt><dd><?= formatPrix($panier['sous_total']) ?></dd>
                    <dt>Livraison</dt><dd><?= $panier['frais'] === 0 ? 'Offerte' : formatPrix($panier['frais']) ?></dd>
                    <dt class="recap-total">Total</dt><dd class="recap-total"><?= formatPrix($panier['total']) ?></dd>
                </dl>
                <?php if ($seuil > 0 && $panier['frais'] > 0): ?>
                    <p class="recap-astuce">Plus que <?= formatPrix($seuil - $panier['sous_total']) ?> d’achat pour profiter de la livraison offerte.</p>
                <?php endif; ?>
                <a href="<?= BASE_URL ?>commande.php" class="bouton bouton-bordeaux bouton-large">Passer la commande</a>
                <p class="recap-paiements">Paiement par Wave, Orange Money, Moov Money ou Djamo</p>
            </aside>
        </div>
        <?php endif; ?>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
