<?php
/**
 * auth.php — Sessions des clients et des administrateurs (strictement séparées).
 */

// ---------------- Clients ----------------

function connecterClient(array $user): void
{
    session_regenerate_id(true);
    $_SESSION['client_id'] = (int) $user['id'];
    $_SESSION['client_prenom'] = $user['prenom'];
}

function deconnecterClient(): void
{
    unset($_SESSION['client_id'], $_SESSION['client_prenom']);
    session_regenerate_id(true);
}

function clientConnecte(): bool
{
    return !empty($_SESSION['client_id']);
}

function clientActuel(): ?array
{
    if (!clientConnecte()) {
        return null;
    }
    $stmt = getDB()->prepare('SELECT * FROM users WHERE id = ?');
    $stmt->execute([$_SESSION['client_id']]);
    $user = $stmt->fetch();
    if (!$user) {
        deconnecterClient();
        return null;
    }
    return $user;
}

/** Redirige vers la connexion, puis revient sur la page demandée. */
function exigerClient(): array
{
    $user = clientActuel();
    if (!$user) {
        $_SESSION['retour_apres_connexion'] = $_SERVER['REQUEST_URI'] ?? BASE_URL;
        flash('erreur', 'Connectez-vous pour continuer.');
        redirect(BASE_URL . 'connexion.php');
    }
    return $user;
}

// ---------------- Administrateurs ----------------

function connecterAdmin(array $admin): void
{
    session_regenerate_id(true);
    $_SESSION['admin_id'] = (int) $admin['id'];
    $_SESSION['admin_nom'] = $admin['nom'];
}

function deconnecterAdmin(): void
{
    unset($_SESSION['admin_id'], $_SESSION['admin_nom']);
    session_regenerate_id(true);
}

function exigerAdmin(): void
{
    if (empty($_SESSION['admin_id'])) {
        redirect(BASE_URL . 'admin/login.php');
    }
}
