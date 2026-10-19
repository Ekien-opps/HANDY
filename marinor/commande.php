<?php
require_once __DIR__ . '/includes/functions.php';

$client = exigerClient();
$panier = panierDetails();

if (!$panier['lignes']) {
    flash('erreur', 'Votre panier est vide.');
    redirect(BASE_URL . 'panier.php');
}

$communes = ['Abobo', 'Adjamé', 'Anyama', 'Attécoubé', 'Bingerville', 'Cocody', 'Koumassi', 'Marcory',
             'Plateau', 'Port-Bouët', 'Songon', 'Treichville', 'Yopougon'];
$methodes = ['wave', 'orange_money', 'moov_money', 'djamo'];

$valeurs = [
    'nom'          => trim($client['prenom'] . ' ' . $client['nom']),
    'telephone'    => $client['telephone'],
    'adresse'      => $client['adresse'] ?? '',
    'commune'      => $client['commune'] ?? '',
    'instructions' => '',
    'methode'      => 'wave',
];
$erreurs = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    foreach (array_keys($valeurs) as $champ) {
        $valeurs[$champ] = trim(valeurTexte($_POST, $champ));
    }

    if (mb_strlen($valeurs['nom']) < 3) {
        $erreurs['nom'] = 'Indiquez le nom de la personne qui recevra la commande.';
    }
    if (!telephoneValide($valeurs['telephone'])) {
        $erreurs['telephone'] = 'Indiquez un numéro ivoirien à 10 chiffres, par exemple 07 00 00 00 00.';
    }
    if (mb_strlen($valeurs['adresse']) < 5) {
        $erreurs['adresse'] = 'Précisez l’adresse : quartier, rue, point de repère.';
    }
    if (!in_array($valeurs['commune'], $communes, true)) {
        $erreurs['commune'] = 'Choisissez votre commune de livraison.';
    }
    if (!in_array($valeurs['methode'], $methodes, true)) {
        $erreurs['methode'] = 'Choisissez un moyen de paiement.';
    }

    if (!$erreurs) {
        $pdo = getDB();
        try {
            $pdo->beginTransaction();

            // Verrouillage des produits pour éviter de vendre un stock déjà parti
            $ids = array_map(fn ($l) => (int) $l['produit']['id'], $panier['lignes']);
            $marqueurs = implode(',', array_fill(0, count($ids), '?'));
            $stmt = $pdo->prepare("SELECT id, nom, prix, stock FROM products WHERE id IN ($marqueurs) AND actif = 1 FOR UPDATE");
            $stmt->execute($ids);
            $stocks = [];
            foreach ($stmt->fetchAll() as $p) {
                $stocks[(int) $p['id']] = $p;
            }

            $sousTotal = 0;
            foreach ($panier['lignes'] as $l) {
                $id = (int) $l['produit']['id'];
                if (!isset($stocks[$id]) || (int) $stocks[$id]['stock'] < $l['quantite']) {
                    throw new RuntimeException('Le stock de « ' . $l['produit']['nom'] . ' » a changé. Vérifiez votre panier.');
                }
                $sousTotal += (int) $stocks[$id]['prix'] * $l['quantite'];
            }
            $frais = fraisLivraison($sousTotal);
            $reference = genererReferenceCommande();

            $pdo->prepare(
                'INSERT INTO orders (reference, user_id, nom_livraison, telephone_livraison, adresse_livraison, commune, ville, instructions, sous_total, frais_livraison, total)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            )->execute([$reference, $client['id'], $valeurs['nom'], $valeurs['telephone'], $valeurs['adresse'],
                        $valeurs['commune'], 'Abidjan', $valeurs['instructions'] ?: null, $sousTotal, $frais, $sousTotal + $frais]);
            $orderId = (int) $pdo->lastInsertId();

            $insertLigne = $pdo->prepare('INSERT INTO order_items (order_id, product_id, nom_produit, prix_unitaire, quantite, total_ligne) VALUES (?, ?, ?, ?, ?, ?)');
            $majStock = $pdo->prepare('UPDATE products SET stock = stock - ? WHERE id = ?');
            foreach ($panier['lignes'] as $l) {
                $p = $stocks[(int) $l['produit']['id']];
                $insertLigne->execute([$orderId, $p['id'], $p['nom'], $p['prix'], $l['quantite'], (int) $p['prix'] * $l['quantite']]);
                $majStock->execute([$l['quantite'], $p['id']]);
            }

            $pdo->prepare('INSERT INTO payments (order_id, methode, montant) VALUES (?, ?, ?)')
                ->execute([$orderId, $valeurs['methode'], $sousTotal + $frais]);

            // Mémoriser l'adresse pour les prochaines commandes
            $pdo->prepare('UPDATE users SET adresse = ?, commune = ? WHERE id = ?')
                ->execute([$valeurs['adresse'], $valeurs['commune'], $client['id']]);

            $pdo->commit();
            panierVider();
            redirect(BASE_URL . 'paiement.php?ref=' . $reference);
        } catch (Throwable $ex) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            flash('erreur', $ex instanceof PDOException
                ? 'La commande n’a pas pu être enregistrée. Veuillez réessayer.'
                : $ex->getMessage());
            redirect(BASE_URL . 'panier.php');
        }
    }
}

$pageTitle = 'Livraison et paiement';
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur">
        <ol class="tunnel" aria-label="Étapes de la commande">
            <li class="fait">Panier</li>
            <li class="en-cours" aria-current="step">Livraison et paiement</li>
            <li>Confirmation</li>
        </ol>

        <div class="panier">
            <form method="post" class="formulaire" novalidate>
                <?= champCSRF() ?>
                <fieldset>
                    <legend>Adresse de livraison</legend>
                    <div class="champ">
                        <label for="nom">Nom de la personne qui réceptionne</label>
                        <input id="nom" name="nom" value="<?= e($valeurs['nom']) ?>" required autocomplete="name">
                        <?php if (isset($erreurs['nom'])): ?><p class="erreur-champ"><?= e($erreurs['nom']) ?></p><?php endif; ?>
                    </div>
                    <div class="champ">
                        <label for="telephone">Téléphone</label>
                        <input id="telephone" name="telephone" type="tel" value="<?= e($valeurs['telephone']) ?>" required autocomplete="tel" placeholder="07 00 00 00 00">
                        <?php if (isset($erreurs['telephone'])): ?><p class="erreur-champ"><?= e($erreurs['telephone']) ?></p><?php endif; ?>
                    </div>
                    <div class="champ">
                        <label for="commune">Commune (Abidjan)</label>
                        <select id="commune" name="commune" required>
                            <option value="">Choisir votre commune</option>
                            <?php foreach ($communes as $c): ?>
                                <option<?= $valeurs['commune'] === $c ? ' selected' : '' ?>><?= e($c) ?></option>
                            <?php endforeach; ?>
                        </select>
                        <?php if (isset($erreurs['commune'])): ?><p class="erreur-champ"><?= e($erreurs['commune']) ?></p><?php endif; ?>
                    </div>
                    <div class="champ">
                        <label for="adresse">Adresse précise</label>
                        <input id="adresse" name="adresse" value="<?= e($valeurs['adresse']) ?>" required placeholder="Quartier, rue, point de repère">
                        <?php if (isset($erreurs['adresse'])): ?><p class="erreur-champ"><?= e($erreurs['adresse']) ?></p><?php endif; ?>
                    </div>
                    <div class="champ">
                        <label for="instructions">Instructions pour le livreur (facultatif)</label>
                        <input id="instructions" name="instructions" value="<?= e($valeurs['instructions']) ?>" maxlength="255" placeholder="Ex. : appeler en arrivant devant la pharmacie">
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Moyen de paiement</legend>
                    <div class="choix-paiement">
                        <?php foreach ($methodes as $m): ?>
                        <label class="option-paiement option-<?= e($m) ?>">
                            <input type="radio" name="methode" value="<?= e($m) ?>"<?= $valeurs['methode'] === $m ? ' checked' : '' ?>>
                            <span><?= e(libelleMethodePaiement($m)) ?></span>
                        </label>
                        <?php endforeach; ?>
                    </div>
                    <?php if (isset($erreurs['methode'])): ?><p class="erreur-champ"><?= e($erreurs['methode']) ?></p><?php endif; ?>
                    <p class="aide">À l’étape suivante, vous recevrez le numéro marchand et le montant exact à envoyer.</p>
                </fieldset>

                <button type="submit" class="bouton bouton-bordeaux bouton-large">Valider ma commande</button>
            </form>

            <aside class="recap">
                <h2>Votre commande</h2>
                <ul class="recap-lignes">
                    <?php foreach ($panier['lignes'] as $l): ?>
                        <li><span><?= $l['quantite'] ?> × <?= e($l['produit']['nom']) ?></span><span><?= formatPrix($l['total']) ?></span></li>
                    <?php endforeach; ?>
                </ul>
                <dl>
                    <dt>Sous-total</dt><dd><?= formatPrix($panier['sous_total']) ?></dd>
                    <dt>Livraison</dt><dd><?= $panier['frais'] === 0 ? 'Offerte' : formatPrix($panier['frais']) ?></dd>
                    <dt class="recap-total">Total</dt><dd class="recap-total"><?= formatPrix($panier['total']) ?></dd>
                </dl>
                <a href="<?= BASE_URL ?>panier.php" class="lien-fort">Modifier mon panier</a>
            </aside>
        </div>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
