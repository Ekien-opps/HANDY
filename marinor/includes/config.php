<?php
/**
 * config.php — Configuration générale du site Marin'Or Ivoire.
 * Seul fichier à modifier lors d'un changement d'environnement (local → production).
 */

// ---------------------------------------------------------------
// Base de données (WampServer par défaut)
// ---------------------------------------------------------------
define('DB_HOST', 'localhost');
define('DB_NAME', 'marinor_db');
define('DB_USER', 'root');
define('DB_PASS', '');

// ---------------------------------------------------------------
// URL de base : toujours terminer par un "/"
// En production : https://www.marinor-ivoire.ci/
// ---------------------------------------------------------------
define('BASE_URL', 'http://localhost/marinor/');

define('SITE_NAME', "Marin'Or Ivoire");
define('ROOT_PATH', dirname(__DIR__) . '/');
define('UPLOAD_PATH', ROOT_PATH . 'uploads/');
define('UPLOAD_URL', BASE_URL . 'uploads/');

// Uploads : 5 Mo maximum, formats image courants uniquement
define('UPLOAD_MAX_SIZE', 5 * 1024 * 1024);
define('UPLOAD_MIME_AUTORISES', ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp']);

define('PRODUITS_PAR_PAGE', 12);
define('QUANTITE_MAX_PAR_PRODUIT', 50);

// Mode développement : afficher les erreurs en local uniquement
define('MODE_DEV', true);

if (MODE_DEV) {
    ini_set('display_errors', '1');
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', '0');
    error_reporting(0);
}

date_default_timezone_set('Africa/Abidjan');

// ---------------------------------------------------------------
// Session sécurisée
// ---------------------------------------------------------------
if (session_status() === PHP_SESSION_NONE) {
    $https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
    session_set_cookie_params([
        'lifetime' => 0,
        'path'     => '/',
        'secure'   => $https,
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    session_name('MARINOR_SESSID');
    session_start();
}

// ---------------------------------------------------------------
// En-têtes HTTP de sécurité
// ---------------------------------------------------------------
if (!headers_sent()) {
    header('X-Frame-Options: SAMEORIGIN');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header("Content-Security-Policy: default-src 'self'; "
        . "img-src 'self' data: https:; "
        . "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        . "font-src 'self' https://fonts.gstatic.com; "
        . "script-src 'self'; "
        . "frame-src https://www.google.com; "
        . "form-action 'self'; base-uri 'self'");
}
