<?php
require_once dirname(__DIR__) . '/includes/functions.php';

if (!empty($_SESSION['admin_id'])) {
    redirect(BASE_URL . 'admin/index.php');
}

$erreur = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
        $erreur = 'Votre session a expiré. Veuillez réessayer.';
    } elseif (rateLimitDepasse('connexion_admin', 5, 900)) {
        $erreur = 'Trop de tentatives. Réessayez dans 15 minutes.';
    } else {
        $stmt = getDB()->prepare('SELECT * FROM admins WHERE email = ?');
        $stmt->execute([trim(valeurTexte($_POST, 'email'))]);
        $admin = $stmt->fetch();
        if ($admin && password_verify(valeurTexte($_POST, 'mot_de_passe'), $admin['mot_de_passe'])) {
            unset($_SESSION['rate']['connexion_admin']);
            connecterAdmin($admin);
            redirect(BASE_URL . 'admin/index.php');
        }
        rateLimitEnregistrer('connexion_admin');
        sleep(1);
        $erreur = 'Adresse e-mail ou mot de passe incorrect.';
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Connexion | Administration <?= e(SITE_NAME) ?></title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="<?= BASE_URL ?>assets/css/admin.css" rel="stylesheet">
</head>
<body class="page-connexion">
<main class="connexion">
    <p class="admin-logo">Marin’Or <small>Administration</small></p>
    <?php if ($erreur): ?><div class="alerte alerte-erreur"><?= e($erreur) ?></div><?php endif; ?>
    <form method="post" class="formulaire">
        <?= champCSRF() ?>
        <div class="champ">
            <label for="email">Adresse e-mail</label>
            <input id="email" name="email" type="email" required autofocus autocomplete="username">
        </div>
        <div class="champ">
            <label for="mot_de_passe">Mot de passe</label>
            <input id="mot_de_passe" name="mot_de_passe" type="password" required autocomplete="current-password">
        </div>
        <button type="submit" class="bouton">Se connecter</button>
    </form>
    <p class="connexion-retour"><a href="<?= BASE_URL ?>">Retour au site</a></p>
</main>
</body>
</html>
