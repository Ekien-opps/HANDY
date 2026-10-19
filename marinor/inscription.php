<?php
require_once __DIR__ . '/includes/functions.php';

if (clientConnecte()) {
    redirect(BASE_URL . 'compte.php');
}

$valeurs = ['prenom' => '', 'nom' => '', 'email' => '', 'telephone' => ''];
$erreurs = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    foreach (array_keys($valeurs) as $champ) {
        $valeurs[$champ] = trim(valeurTexte($_POST, $champ));
    }
    $mdp = valeurTexte($_POST, 'mot_de_passe');
    $confirmation = valeurTexte($_POST, 'confirmation');

    if (mb_strlen($valeurs['prenom']) < 2) {
        $erreurs['prenom'] = 'Indiquez votre prénom.';
    }
    if (mb_strlen($valeurs['nom']) < 2) {
        $erreurs['nom'] = 'Indiquez votre nom.';
    }
    if (!filter_var($valeurs['email'], FILTER_VALIDATE_EMAIL)) {
        $erreurs['email'] = 'Indiquez une adresse e-mail valide.';
    }
    if (!telephoneValide($valeurs['telephone'])) {
        $erreurs['telephone'] = 'Indiquez un numéro ivoirien à 10 chiffres.';
    }
    if (!motDePasseValide($mdp)) {
        $erreurs['mot_de_passe'] = '8 caractères minimum, avec une majuscule, une minuscule et un chiffre.';
    } elseif ($mdp !== $confirmation) {
        $erreurs['confirmation'] = 'Les deux mots de passe ne correspondent pas.';
    }

    if (!$erreurs) {
        $pdo = getDB();
        $stmt = $pdo->prepare('SELECT id FROM users WHERE email = ?');
        $stmt->execute([$valeurs['email']]);
        if ($stmt->fetch()) {
            $erreurs['email'] = 'Un compte existe déjà avec cette adresse. Connectez-vous.';
        } else {
            $pdo->prepare('INSERT INTO users (prenom, nom, email, telephone, mot_de_passe) VALUES (?, ?, ?, ?, ?)')
                ->execute([$valeurs['prenom'], $valeurs['nom'], $valeurs['email'], $valeurs['telephone'], password_hash($mdp, PASSWORD_DEFAULT)]);
            connecterClient(['id' => $pdo->lastInsertId(), 'prenom' => $valeurs['prenom']]);
            flash('succes', 'Bienvenue ' . $valeurs['prenom'] . ', votre compte est créé.');
            $retour = $_SESSION['retour_apres_connexion'] ?? BASE_URL . 'compte.php';
            unset($_SESSION['retour_apres_connexion']);
            redirect($retour);
        }
    }
}

$pageTitle = 'Créer un compte';
require_once __DIR__ . '/includes/header.php';

function champInscription(string $nom, string $libelle, string $type, array $valeurs, array $erreurs, string $auto): void
{ ?>
    <div class="champ">
        <label for="<?= $nom ?>"><?= e($libelle) ?></label>
        <input id="<?= $nom ?>" name="<?= $nom ?>" type="<?= $type ?>" value="<?= $type === 'password' ? '' : e($valeurs[$nom] ?? '') ?>" required autocomplete="<?= $auto ?>">
        <?php if (isset($erreurs[$nom])): ?><p class="erreur-champ"><?= e($erreurs[$nom]) ?></p><?php endif; ?>
    </div>
<?php }
?>

<section class="section">
    <div class="conteneur conteneur-etroit">
        <div class="carte-formulaire">
            <h1 class="titre-affiche">Créer mon compte</h1>
            <p>Suivez vos commandes et retrouvez vos adresses de livraison.</p>
            <form method="post" class="formulaire" novalidate>
                <?= champCSRF() ?>
                <div class="champs-duo">
                    <?php champInscription('prenom', 'Prénom', 'text', $valeurs, $erreurs, 'given-name'); ?>
                    <?php champInscription('nom', 'Nom', 'text', $valeurs, $erreurs, 'family-name'); ?>
                </div>
                <?php champInscription('email', 'Adresse e-mail', 'email', $valeurs, $erreurs, 'email'); ?>
                <?php champInscription('telephone', 'Téléphone', 'tel', $valeurs, $erreurs, 'tel'); ?>
                <?php champInscription('mot_de_passe', 'Mot de passe', 'password', $valeurs, $erreurs, 'new-password'); ?>
                <?php champInscription('confirmation', 'Confirmer le mot de passe', 'password', $valeurs, $erreurs, 'new-password'); ?>
                <button type="submit" class="bouton bouton-bordeaux bouton-large">Créer mon compte</button>
            </form>
            <p class="lien-bas">Déjà client ? <a href="<?= BASE_URL ?>connexion.php">Se connecter</a></p>
        </div>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
