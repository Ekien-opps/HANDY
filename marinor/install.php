<?php
/**
 * install.php — Installation de la base de données. À SUPPRIMER APRÈS USAGE.
 * Accès : http://localhost/marinor/install.php
 */
if (file_exists(__DIR__ . '/installed.lock')) {
    die('Le site est déjà installé. Supprimez le fichier installed.lock pour réinstaller (toutes les données seront effacées).');
}

require_once __DIR__ . '/includes/config.php';

const INSTALL_ADMIN_EMAIL = 'admin@marinor-ivoire.ci';
const INSTALL_ADMIN_PASSWORD = 'MarinOr2026!';

try {
    $pdo = new PDO('mysql:host=' . DB_HOST . ';charset=utf8mb4', DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    ]);
    $pdo->exec('CREATE DATABASE IF NOT EXISTS `' . DB_NAME . '` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
    $pdo->exec('USE `' . DB_NAME . '`');

    $sql = file_get_contents(__DIR__ . '/database.sql');
    if ($sql === false) {
        throw new RuntimeException('Le fichier database.sql est introuvable.');
    }
    $pdo->exec($sql);

    $hash = password_hash(INSTALL_ADMIN_PASSWORD, PASSWORD_DEFAULT);
    $pdo->prepare('UPDATE admins SET mot_de_passe = ? WHERE email = ?')->execute([$hash, INSTALL_ADMIN_EMAIL]);

    foreach (['uploads/produits', 'uploads/categories', 'uploads/logo'] as $dossier) {
        if (!is_dir(__DIR__ . '/' . $dossier)) {
            mkdir(__DIR__ . '/' . $dossier, 0755, true);
        }
    }

    file_put_contents(__DIR__ . '/installed.lock', date('Y-m-d H:i:s'));
    $ok = true;
} catch (Throwable $e) {
    $ok = false;
    $erreur = $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Installation — Marin'Or Ivoire</title>
<style>
    body { font-family: Arial, sans-serif; max-width: 560px; margin: 60px auto; line-height: 1.6; color: #222; padding: 0 16px; }
    h1 { color: #7B1421; }
    code { background: #F6E8EA; padding: 2px 6px; border-radius: 4px; }
    .alerte { background: #FFECD1; padding: 12px 16px; border-left: 4px solid #F9A825; margin-top: 20px; }
    a.bouton { display: inline-block; margin-top: 16px; background: #7B1421; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; }
</style>
</head>
<body>
<?php if ($ok): ?>
    <h1>Installation terminée</h1>
    <p>La base <code><?= htmlspecialchars(DB_NAME) ?></code> a été créée avec ses tables et les 15 produits de démonstration.</p>
    <p><strong>Administration :</strong> <code><?= htmlspecialchars(INSTALL_ADMIN_EMAIL) ?></code> / <code><?= htmlspecialchars(INSTALL_ADMIN_PASSWORD) ?></code></p>
    <a class="bouton" href="admin/login.php">Ouvrir l’administration</a>
    <p class="alerte">Supprimez le fichier <code>install.php</code> maintenant, puis changez le mot de passe depuis Paramètres.</p>
<?php else: ?>
    <h1>L’installation a échoué</h1>
    <pre><?= htmlspecialchars($erreur) ?></pre>
    <p>Vérifiez que WampServer est lancé (icône verte) et les identifiants dans <code>includes/config.php</code>.</p>
<?php endif; ?>
</body>
</html>
