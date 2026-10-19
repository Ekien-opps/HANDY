<?php
require_once __DIR__ . '/includes/functions.php';

$client = exigerClient();
$pdo = getDB();
$section = in_array($_GET['section'] ?? '', ['commandes', 'profil', 'securite'], true) ? $_GET['section'] : 'commandes';
$erreurs = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $action = $_POST['action'] ?? '';

    if ($action === 'profil') {
        $donnees = [];
        foreach (['prenom', 'nom', 'telephone', 'adresse', 'commune'] as $champ) {
            $donnees[$champ] = trim(valeurTexte($_POST, $champ));
        }
        if (mb_strlen($donnees['prenom']) < 2 || mb_strlen($donnees['nom']) < 2) {
            $erreurs['profil'] = 'Le prénom et le nom doivent contenir au moins 2 caractères.';
        } elseif (!telephoneValide($donnees['telephone'])) {
            $erreurs['profil'] = 'Indiquez un numéro ivoirien à 10 chiffres.';
        } else {
            $pdo->prepare('UPDATE users SET prenom = ?, nom = ?, telephone = ?, adresse = ?, commune = ? WHERE id = ?')
                ->execute([$donnees['prenom'], $donnees['nom'], $donnees['telephone'], $donnees['adresse'] ?: null, $donnees['commune'] ?: null, $client['id']]);
            $_SESSION['client_prenom'] = $donnees['prenom'];
            flash('succes', 'Vos informations ont été enregistrées.');
            redirect(BASE_URL . 'compte.php?section=profil');
        }
        $section = 'profil';
    }

    if ($action === 'mot_de_passe') {
        $actuel = valeurTexte($_POST, 'actuel');
        $nouveau = valeurTexte($_POST, 'nouveau');
        if (!password_verify($actuel, $client['mot_de_passe'])) {
            $erreurs['securite'] = 'Le mot de passe actuel est incorrect.';
        } elseif (!motDePasseValide($nouveau)) {
            $erreurs['securite'] = 'Le nouveau mot de passe doit contenir 8 caractères, une majuscule, une minuscule et un chiffre.';
        } else {
            $pdo->prepare('UPDATE users SET mot_de_passe = ? WHERE id = ?')->execute([password_hash($nouveau, PASSWORD_DEFAULT), $client['id']]);
            flash('succes', 'Votre mot de passe a été modifié.');
            redirect(BASE_URL . 'compte.php?section=securite');
        }
        $section = 'securite';
    }

    if ($action === 'supprimer') {
        if (!password_verify(valeurTexte($_POST, 'confirmation_mdp'), $client['mot_de_passe'])) {
            $erreurs['suppression'] = 'Mot de passe incorrect : votre compte n’a pas été supprimé.';
            $section = 'securite';
        } else {
            // Les commandes sont conservées pour la comptabilité, sans lien avec le compte supprimé
            $pdo->prepare('DELETE FROM users WHERE id = ?')->execute([$client['id']]);
            deconnecterClient();
            flash('succes', 'Votre compte a été supprimé.');
            redirect(BASE_URL);
        }
    }
}

$client = clientActuel();
$commandes = $pdo->prepare(
    'SELECT o.*, pay.methode, pay.statut AS paiement_statut,
            (SELECT SUM(quantite) FROM order_items WHERE order_id = o.id) AS nb_articles
     FROM orders o JOIN payments pay ON pay.order_id = o.id
     WHERE o.user_id = ? ORDER BY o.created_at DESC'
);
$commandes->execute([$client['id']]);
$commandes = $commandes->fetchAll();

$pageTitle = 'Mon compte';
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur">
        <div class="compte-entete">
            <h1 class="titre-affiche">Bonjour <?= e($client['prenom']) ?></h1>
            <form method="post" action="<?= BASE_URL ?>deconnexion.php">
                <?= champCSRF() ?>
                <button type="submit" class="bouton bouton-contour bouton-petit">Se déconnecter</button>
            </form>
        </div>

        <nav class="onglets" aria-label="Mon compte">
            <a href="?section=commandes"<?= $section === 'commandes' ? ' aria-current="page"' : '' ?>>Mes commandes</a>
            <a href="?section=profil"<?= $section === 'profil' ? ' aria-current="page"' : '' ?>>Mes informations</a>
            <a href="?section=securite"<?= $section === 'securite' ? ' aria-current="page"' : '' ?>>Mot de passe et compte</a>
        </nav>

        <?php if ($section === 'commandes'): ?>
            <?php if (!$commandes): ?>
                <div class="etat-vide">
                    <p>Vous n’avez pas encore passé de commande.</p>
                    <a href="<?= BASE_URL ?>boutique.php" class="bouton bouton-bordeaux">Découvrir nos produits</a>
                </div>
            <?php else: ?>
                <div class="tableau-defilant">
                <table class="tableau">
                    <thead><tr><th>Référence</th><th>Date</th><th>Articles</th><th>Total</th><th>Paiement</th><th>Statut</th><th></th></tr></thead>
                    <tbody>
                    <?php foreach ($commandes as $c): ?>
                        <tr>
                            <td><?= e($c['reference']) ?></td>
                            <td><?= formatDate($c['created_at']) ?></td>
                            <td><?= (int) $c['nb_articles'] ?></td>
                            <td><?= formatPrix((int) $c['total']) ?></td>
                            <td><?= e(libelleMethodePaiement($c['methode'])) ?> : <?= e(libelleStatutPaiement($c['paiement_statut'])) ?></td>
                            <td><span class="statut statut-<?= e($c['statut']) ?>"><?= e(libelleStatutCommande($c['statut'])) ?></span></td>
                            <td><a href="<?= BASE_URL ?>paiement.php?ref=<?= e($c['reference']) ?>"><?= $c['paiement_statut'] === 'en_attente' ? 'Payer' : 'Détails' ?></a></td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
                </div>
            <?php endif; ?>

        <?php elseif ($section === 'profil'): ?>
            <form method="post" class="formulaire carte-formulaire">
                <?= champCSRF() ?>
                <input type="hidden" name="action" value="profil">
                <?php if (isset($erreurs['profil'])): ?><div class="alerte alerte-erreur"><?= e($erreurs['profil']) ?></div><?php endif; ?>
                <div class="champs-duo">
                    <div class="champ"><label for="prenom">Prénom</label><input id="prenom" name="prenom" value="<?= e($client['prenom']) ?>" required></div>
                    <div class="champ"><label for="nom">Nom</label><input id="nom" name="nom" value="<?= e($client['nom']) ?>" required></div>
                </div>
                <div class="champ"><label for="email">Adresse e-mail</label><input id="email" value="<?= e($client['email']) ?>" disabled></div>
                <div class="champ"><label for="telephone">Téléphone</label><input id="telephone" name="telephone" type="tel" value="<?= e($client['telephone']) ?>" required></div>
                <div class="champ"><label for="adresse">Adresse de livraison habituelle</label><input id="adresse" name="adresse" value="<?= e($client['adresse']) ?>"></div>
                <div class="champ"><label for="commune">Commune</label><input id="commune" name="commune" value="<?= e($client['commune']) ?>"></div>
                <button type="submit" class="bouton bouton-bordeaux">Enregistrer mes informations</button>
            </form>

        <?php else: ?>
            <div class="compte-securite">
                <form method="post" class="formulaire carte-formulaire">
                    <?= champCSRF() ?>
                    <input type="hidden" name="action" value="mot_de_passe">
                    <h2>Changer de mot de passe</h2>
                    <?php if (isset($erreurs['securite'])): ?><div class="alerte alerte-erreur"><?= e($erreurs['securite']) ?></div><?php endif; ?>
                    <div class="champ"><label for="actuel">Mot de passe actuel</label><input id="actuel" name="actuel" type="password" required autocomplete="current-password"></div>
                    <div class="champ"><label for="nouveau">Nouveau mot de passe</label><input id="nouveau" name="nouveau" type="password" required autocomplete="new-password"></div>
                    <button type="submit" class="bouton bouton-bordeaux">Changer mon mot de passe</button>
                </form>

                <form method="post" class="formulaire carte-formulaire zone-danger" data-confirmation="Supprimer définitivement votre compte ?">
                    <?= champCSRF() ?>
                    <input type="hidden" name="action" value="supprimer">
                    <h2>Supprimer mon compte</h2>
                    <p>Vos données personnelles seront effacées. Les commandes déjà passées restent enregistrées pour la comptabilité de la boutique.</p>
                    <?php if (isset($erreurs['suppression'])): ?><div class="alerte alerte-erreur"><?= e($erreurs['suppression']) ?></div><?php endif; ?>
                    <div class="champ"><label for="confirmation_mdp">Votre mot de passe, pour confirmer</label><input id="confirmation_mdp" name="confirmation_mdp" type="password" required></div>
                    <button type="submit" class="bouton bouton-danger">Supprimer mon compte</button>
                </form>
            </div>
        <?php endif; ?>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
