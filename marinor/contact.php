<?php
require_once __DIR__ . '/includes/functions.php';

$sujets = ['Question sur un produit', 'Suivi de commande', 'Devenir revendeur', 'Partenariat', 'Autre'];
$valeurs = ['nom' => '', 'email' => '', 'telephone' => '', 'sujet' => '', 'message' => ''];
$erreurs = [];

// Pré-remplissage pour un client connecté
if ($client = clientActuel()) {
    $valeurs['nom'] = $client['prenom'] . ' ' . $client['nom'];
    $valeurs['email'] = $client['email'];
    $valeurs['telephone'] = $client['telephone'];
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    if (!empty($_POST['site_web'])) {
        redirect(BASE_URL . 'contact.php'); // champ piège rempli par un robot
    }
    foreach (array_keys($valeurs) as $champ) {
        $valeurs[$champ] = trim(valeurTexte($_POST, $champ));
    }

    if (rateLimitDepasse('contact', 3, 3600)) {
        $erreurs['global'] = 'Vous avez envoyé plusieurs messages récemment. Réessayez dans une heure ou appelez-nous.';
    }
    if (mb_strlen($valeurs['nom']) < 2) {
        $erreurs['nom'] = 'Indiquez votre nom.';
    }
    if (!filter_var($valeurs['email'], FILTER_VALIDATE_EMAIL)) {
        $erreurs['email'] = 'Indiquez une adresse e-mail valide pour recevoir notre réponse.';
    }
    if ($valeurs['telephone'] !== '' && !telephoneValide($valeurs['telephone'])) {
        $erreurs['telephone'] = 'Ce numéro ne semble pas valide (10 chiffres).';
    }
    if (!in_array($valeurs['sujet'], $sujets, true)) {
        $erreurs['sujet'] = 'Choisissez le sujet de votre message.';
    }
    if (mb_strlen($valeurs['message']) < 10) {
        $erreurs['message'] = 'Votre message doit contenir au moins 10 caractères.';
    }

    if (!$erreurs) {
        getDB()->prepare('INSERT INTO messages (nom, email, telephone, sujet, message) VALUES (?, ?, ?, ?, ?)')
            ->execute([$valeurs['nom'], $valeurs['email'], $valeurs['telephone'] ?: null, $valeurs['sujet'], $valeurs['message']]);
        rateLimitEnregistrer('contact');
        flash('succes', 'Message envoyé. Nous vous répondons sous 24 heures ouvrées.');
        redirect(BASE_URL . 'contact.php');
    }
}

$pageTitle = 'Contact';
$pageDescription = 'Une question sur nos produits ou votre commande ? Contactez Marin’Or Ivoire.';
$pageActive = 'contact';
require_once __DIR__ . '/includes/header.php';
$whatsapp = preg_replace('/\D/', '', getParam('whatsapp'));
?>

<section class="bandeau-page bandeau-contact">
    <div class="conteneur">
        <nav class="fil-ariane" aria-label="Fil d’Ariane"><a href="<?= BASE_URL ?>">Accueil</a> / Contact</nav>
        <h1 class="titre-affiche">Écrivez-nous</h1>
        <p>Une question sur un produit, une commande ou un partenariat ? Nous vous répondons rapidement.</p>
    </div>
</section>

<section class="section">
    <div class="conteneur contact">
        <aside class="contact-coordonnees">
            <h2>Nos coordonnées</h2>
            <dl>
                <dt>Adresse</dt><dd><?= e(getParam('adresse')) ?></dd>
                <dt>Téléphone</dt><dd><a href="tel:<?= e(preg_replace('/\s/', '', getParam('telephone'))) ?>"><?= e(getParam('telephone')) ?></a></dd>
                <dt>E-mail</dt><dd><a href="mailto:<?= e(getParam('email')) ?>"><?= e(getParam('email')) ?></a></dd>
                <dt>Horaires</dt><dd><?= e(getParam('horaires')) ?></dd>
            </dl>
            <?php if ($whatsapp !== ''): ?>
                <a class="bouton bouton-vert" href="https://wa.me/<?= e($whatsapp) ?>" target="_blank" rel="noopener">Nous écrire sur WhatsApp</a>
            <?php endif; ?>
        </aside>

        <form method="post" class="formulaire carte-formulaire" novalidate>
            <?= champCSRF() ?>
            <?php if (isset($erreurs['global'])): ?><div class="alerte alerte-erreur"><?= e($erreurs['global']) ?></div><?php endif; ?>
            <div class="visuellement-cache" aria-hidden="true">
                <label for="site_web">Ne pas remplir</label>
                <input id="site_web" name="site_web" tabindex="-1" autocomplete="off">
            </div>
            <div class="champs-duo">
                <div class="champ">
                    <label for="nom">Nom complet</label>
                    <input id="nom" name="nom" value="<?= e($valeurs['nom']) ?>" required autocomplete="name">
                    <?php if (isset($erreurs['nom'])): ?><p class="erreur-champ"><?= e($erreurs['nom']) ?></p><?php endif; ?>
                </div>
                <div class="champ">
                    <label for="telephone">Téléphone (facultatif)</label>
                    <input id="telephone" name="telephone" type="tel" value="<?= e($valeurs['telephone']) ?>" autocomplete="tel">
                    <?php if (isset($erreurs['telephone'])): ?><p class="erreur-champ"><?= e($erreurs['telephone']) ?></p><?php endif; ?>
                </div>
            </div>
            <div class="champ">
                <label for="email">Adresse e-mail</label>
                <input id="email" name="email" type="email" value="<?= e($valeurs['email']) ?>" required autocomplete="email">
                <?php if (isset($erreurs['email'])): ?><p class="erreur-champ"><?= e($erreurs['email']) ?></p><?php endif; ?>
            </div>
            <div class="champ">
                <label for="sujet">Sujet</label>
                <select id="sujet" name="sujet" required>
                    <option value="">Choisir un sujet</option>
                    <?php foreach ($sujets as $s): ?>
                        <option<?= $valeurs['sujet'] === $s ? ' selected' : '' ?>><?= e($s) ?></option>
                    <?php endforeach; ?>
                </select>
                <?php if (isset($erreurs['sujet'])): ?><p class="erreur-champ"><?= e($erreurs['sujet']) ?></p><?php endif; ?>
            </div>
            <div class="champ">
                <label for="message">Votre message</label>
                <textarea id="message" name="message" rows="6" required data-compteur="10"><?= e($valeurs['message']) ?></textarea>
                <p class="aide" data-compteur-texte aria-live="polite"></p>
                <?php if (isset($erreurs['message'])): ?><p class="erreur-champ"><?= e($erreurs['message']) ?></p><?php endif; ?>
            </div>
            <button type="submit" class="bouton bouton-bordeaux bouton-large">Envoyer le message</button>
        </form>
    </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
