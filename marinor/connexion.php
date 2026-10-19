<?php
require_once __DIR__ . '/includes/functions.php';

if (clientConnecte()) {
    redirect(BASE_URL . 'compte.php');
}

$email = '';
$erreur = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $email = trim(valeurTexte($_POST, 'email'));
    $mdp = valeurTexte($_POST, 'mot_de_passe');

    if (rateLimitDepasse('connexion_client', 5, 900)) {
        $erreur = 'Trop de tentatives. Réessayez dans 15 minutes.';
    } else {
        $stmt = getDB()->prepare('SELECT * FROM users WHERE email = ?');
        $stmt->execute([$email]);
        $user = $stmt->fetch();

        if ($user && password_verify($mdp, $user['mot_de_passe'])) {
            unset($_SESSION['rate']['connexion_client']);
            connecterClient($user);
            $retour = $_SESSION['retour_apres_connexion'] ?? BASE_URL . 'compte.php';
            unset($_SESSION['retour_apres_connexion']);
            redirect($retour);
        }
        rateLimitEnregistrer('connexion_client');
        sleep(1);
        $erreur = 'Adresse e-mail ou mot de passe incorrect.';
    }
}

$pageTitle = 'Se connecter';
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur conteneur-etroit">
        <div class="carte-formulaire">
            <h1 class="titre-affiche">Se connecter</h1>
            <?php if ($erreur): ?><div class="alerte alerte-erreur"><?= e($erreur) ?></div><?php endif; ?>
            <form method="post" class="formulaire">
                <?= champCSRF() ?>
                <div class="champ">
                    <label for="email">Adresse e-mail</label>
                    <input id="email" name="email" type="email" value="<?= e($email) ?>" required autocomplete="email">
                </div>
                <div class="champ">
                    <label for="mot_de_passe">Mot de passe</label>
                    <input id="mot_de_passe" name="mot_de_passe" type="password" required autocomplete="current-password">
                </div>
                <button type="submit" class="bouton bouton-bordeaux bouton-large">Se connecter</button>
            </form>
            <p class="lien-bas">Nouveau client ? <a href="<?= BASE_URL ?>inscription.php">Créer un compte</a></p>
        </div>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
