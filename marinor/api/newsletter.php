<?php
/** api/newsletter.php — Inscription à la lettre d'information (réponse JSON ou redirection). */
require_once dirname(__DIR__) . '/includes/functions.php';

$ajax = ($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') === 'fetch';

function reponse(bool $ok, string $message, bool $ajax): void
{
    if ($ajax) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $message]);
        exit;
    }
    flash($ok ? 'succes' : 'erreur', $message);
    redirect(BASE_URL);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
    reponse(false, 'Votre session a expiré. Rechargez la page.', $ajax);
}
if (rateLimitDepasse('newsletter', 5, 3600)) {
    reponse(false, 'Trop de tentatives. Réessayez plus tard.', $ajax);
}
rateLimitEnregistrer('newsletter');

$email = trim((string) ($_POST['email'] ?? ''));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reponse(false, 'Indiquez une adresse e-mail valide.', $ajax);
}

getDB()->prepare('INSERT IGNORE INTO subscribers (email) VALUES (?)')->execute([$email]);
reponse(true, 'Merci ! Vous recevrez nos prochaines recettes.', $ajax);
