<?php
/** footer.php — Pied de page commun, bandeau cookies et scripts. */
$reseaux = array_filter([
    'Facebook'  => getParam('facebook'),
    'Instagram' => getParam('instagram'),
    'TikTok'    => getParam('tiktok'),
    'WhatsApp'  => getParam('whatsapp') !== '' ? 'https://wa.me/' . preg_replace('/\D/', '', getParam('whatsapp')) : '',
]);
?>
</main>

<section class="bande-newsletter">
    <div class="conteneur bande-newsletter-grille">
        <div>
            <h2 class="titre-affiche">Recettes et nouveautés, chaque mois</h2>
            <p>Recevez nos idées de recettes ivoiriennes et soyez les premiers informés des nouveaux produits.</p>
        </div>
        <form class="form-newsletter" action="<?= BASE_URL ?>api/newsletter.php" method="post" data-newsletter>
            <?= champCSRF() ?>
            <label for="email-newsletter" class="visuellement-cache">Votre adresse e-mail</label>
            <input type="email" id="email-newsletter" name="email" placeholder="Votre adresse e-mail" required>
            <button type="submit" class="bouton bouton-or">Je m’abonne</button>
            <p class="form-newsletter-retour" data-newsletter-retour aria-live="polite"></p>
        </form>
    </div>
</section>

<footer class="pied">
    <div class="conteneur pied-grille">
        <div>
            <div class="pied-logo"><?= getLogo(true) ?></div>
            <p><?= e(getParam('slogan', 'Le vrai goût de chez nous')) ?></p>
            <?php if ($reseaux): ?>
            <ul class="pied-reseaux">
                <?php foreach ($reseaux as $nom => $url): ?>
                    <li><a href="<?= e($url) ?>" target="_blank" rel="noopener"><?= e($nom) ?></a></li>
                <?php endforeach; ?>
            </ul>
            <?php endif; ?>
        </div>
        <div>
            <h3>Nos gammes</h3>
            <ul>
                <?php foreach ($categoriesMenu as $cat): ?>
                    <li><a href="<?= BASE_URL ?>boutique.php?categorie=<?= e($cat['slug']) ?>"><?= e($cat['nom']) ?></a></li>
                <?php endforeach; ?>
                <li><a href="<?= BASE_URL ?>boutique.php">Tous les produits</a></li>
            </ul>
        </div>
        <div>
            <h3>Informations</h3>
            <ul>
                <li><a href="<?= BASE_URL ?>about.php">Qui sommes-nous ?</a></li>
                <li><a href="<?= BASE_URL ?>contact.php">Nous contacter</a></li>
                <li><a href="<?= BASE_URL ?>confidentialite.php">Confidentialité et cookies</a></li>
            </ul>
        </div>
        <div>
            <h3>Nous joindre</h3>
            <ul>
                <li><?= e(getParam('adresse')) ?></li>
                <li><a href="tel:<?= e(preg_replace('/\s/', '', getParam('telephone'))) ?>"><?= e(getParam('telephone')) ?></a></li>
                <li><a href="mailto:<?= e(getParam('email')) ?>"><?= e(getParam('email')) ?></a></li>
            </ul>
        </div>
    </div>
    <p class="pied-copyright">© <?= date('Y') ?> <?= e(SITE_NAME) ?>. Tous droits réservés.</p>
</footer>

<div class="bandeau-cookies" data-bandeau-cookies hidden role="dialog" aria-labelledby="titre-cookies">
    <p id="titre-cookies"><strong>Cookies</strong> — Ce site utilise uniquement les cookies nécessaires à son fonctionnement (panier, connexion). Aucun cookie publicitaire.
        <a href="<?= BASE_URL ?>confidentialite.php">En savoir plus</a></p>
    <div class="bandeau-cookies-actions">
        <button type="button" class="bouton bouton-contour" data-cookies="refuse">Refuser</button>
        <button type="button" class="bouton bouton-bordeaux" data-cookies="accepte">Accepter</button>
    </div>
</div>

<div class="notification" data-notification role="status" aria-live="polite" hidden></div>

<script src="<?= BASE_URL ?>assets/js/main.js" defer></script>
</body>
</html>
