<?php
require_once __DIR__ . '/includes/functions.php';

$pageTitle = 'Confidentialité et cookies';
require_once __DIR__ . '/includes/header.php';
?>

<section class="section">
    <div class="conteneur conteneur-etroit texte-courant">
        <h1 class="titre-affiche">Confidentialité et cookies</h1>

        <h2>Les données que nous collectons</h2>
        <p>Lorsque vous créez un compte ou passez commande, nous enregistrons vos nom, prénom, adresse e-mail, téléphone et adresse de livraison. Ces informations servent uniquement à traiter et livrer vos commandes, et à vous répondre si vous nous écrivez.</p>

        <h2>Les cookies utilisés</h2>
        <p>Le site utilise un seul cookie, indispensable à son fonctionnement : il mémorise votre panier et votre connexion pendant votre visite. Aucun cookie publicitaire ou de mesure d’audience n’est déposé.</p>

        <h2>Vos droits</h2>
        <p>Vous pouvez à tout moment consulter et modifier vos informations depuis votre espace client, ou supprimer votre compte. Les commandes déjà passées sont conservées pour les obligations comptables de la boutique.</p>
        <p>Pour toute question, écrivez-nous à <a href="mailto:<?= e(getParam('email')) ?>"><?= e(getParam('email')) ?></a>.</p>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
