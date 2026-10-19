<?php
require_once dirname(__DIR__) . '/includes/functions.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
    deconnecterAdmin();
}
redirect(BASE_URL . 'admin/login.php');
