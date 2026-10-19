<?php
require_once __DIR__ . '/includes/functions.php';

// Déconnexion uniquement par formulaire POST protégé (évite la déconnexion forcée par un lien piégé)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
    deconnecterClient();
    flash('succes', 'Vous êtes déconnecté. À bientôt !');
}
redirect(BASE_URL);
