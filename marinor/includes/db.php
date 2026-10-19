<?php
/**
 * db.php — Connexion PDO unique (singleton) à la base marinor_db.
 */
require_once __DIR__ . '/config.php';

function getDB(): PDO
{
    static $pdo = null;

    if ($pdo === null) {
        try {
            $pdo = new PDO(
                'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
                DB_USER,
                DB_PASS,
                [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES   => false,
                ]
            );
        } catch (PDOException $e) {
            http_response_code(500);
            if (MODE_DEV) {
                die('Erreur de connexion à la base de données : ' . htmlspecialchars($e->getMessage())
                    . '<br>Avez-vous lancé <a href="' . BASE_URL . 'install.php">install.php</a> ?');
            }
            die('Le site est momentanément indisponible. Veuillez réessayer plus tard.');
        }
    }

    return $pdo;
}
