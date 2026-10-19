<?php
/**
 * functions.php — Fonctions réutilisables sur tout le site (public et administration).
 */
require_once __DIR__ . '/db.php';
require_once __DIR__ . '/cart.php';
require_once __DIR__ . '/auth.php';

// ---------------------------------------------------------------
// Affichage et navigation
// ---------------------------------------------------------------

/** Échappe une valeur pour l'affichage HTML (protection XSS). */
function e($valeur): string
{
    return htmlspecialchars((string) ($valeur ?? ''), ENT_QUOTES, 'UTF-8');
}

function redirect(string $url): void
{
    header('Location: ' . $url);
    exit;
}

/** Message affiché une seule fois après une redirection. */
function flash(string $type, string $message): void
{
    $_SESSION['flash'][] = ['type' => $type, 'message' => $message];
}

function afficherFlash(): string
{
    $html = '';
    foreach ($_SESSION['flash'] ?? [] as $f) {
        $classe = $f['type'] === 'succes' ? 'alerte alerte-succes' : 'alerte alerte-erreur';
        $html .= '<div class="' . $classe . '" role="status">' . e($f['message']) . '</div>';
    }
    unset($_SESSION['flash']);
    return $html;
}

function formatPrix(int $montant): string
{
    return number_format($montant, 0, ',', ' ') . ' FCFA';
}

function formatDate(?string $date, bool $avecHeure = false): string
{
    if (!$date) {
        return '';
    }
    $mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août',
             'septembre', 'octobre', 'novembre', 'décembre'];
    $t = strtotime($date);
    $texte = date('j', $t) . ' ' . $mois[(int) date('n', $t) - 1] . ' ' . date('Y', $t);
    return $avecHeure ? $texte . ' à ' . date('H\hi', $t) : $texte;
}

function truncate(string $texte, int $longueur = 120): string
{
    $texte = trim(strip_tags($texte));
    return mb_strlen($texte) > $longueur ? rtrim(mb_substr($texte, 0, $longueur)) . '…' : $texte;
}

/**
 * Valeur texte d'un paramètre de requête ($_GET ou $_POST).
 * Retourne '' si le paramètre est absent ou malformé (ex. boutique.php?tri[]=x),
 * au lieu de provoquer une erreur PHP.
 */
function valeurTexte(array $source, string $cle): string
{
    $valeur = $source[$cle] ?? '';
    return is_scalar($valeur) ? (string) $valeur : '';
}

function slugify(string $texte): string
{
    $texte = mb_strtolower(trim($texte), 'UTF-8');
    $texte = strtr($texte, [
        'à' => 'a', 'â' => 'a', 'ä' => 'a', 'é' => 'e', 'è' => 'e', 'ê' => 'e', 'ë' => 'e',
        'î' => 'i', 'ï' => 'i', 'ô' => 'o', 'ö' => 'o', 'ù' => 'u', 'û' => 'u', 'ü' => 'u',
        'ç' => 'c', '’' => '-', "'" => '-',
    ]);
    $texte = preg_replace('/[^a-z0-9]+/', '-', $texte);
    return trim($texte, '-');
}

// ---------------------------------------------------------------
// Paramètres du site (table settings, clé/valeur)
// ---------------------------------------------------------------

function getParam(string $cle, string $defaut = ''): string
{
    static $cache = null;
    if ($cache === null) {
        $cache = [];
        foreach (getDB()->query('SELECT cle, valeur FROM settings') as $ligne) {
            $cache[$ligne['cle']] = $ligne['valeur'];
        }
    }
    return ($cache[$cle] ?? '') !== '' ? $cache[$cle] : $defaut;
}

// ---------------------------------------------------------------
// Images
// ---------------------------------------------------------------

/**
 * Cherche une image déposée à la main dans assets/images/ (jpg, jpeg, png ou webp).
 * $chemin s'écrit sans extension, par exemple 'produits/marinade-poulet'.
 * Retourne son URL (avec un numéro de version pour forcer le rafraîchissement) ou null.
 */
function imageLocale(string $chemin): ?string
{
    foreach (['webp', 'png', 'jpg', 'jpeg'] as $extension) {
        $fichier = ROOT_PATH . 'assets/images/' . $chemin . '.' . $extension;
        if (is_file($fichier)) {
            return BASE_URL . 'assets/images/' . $chemin . '.' . $extension . '?v=' . filemtime($fichier);
        }
    }
    return null;
}

/** Image affichée quand un produit ou une gamme n'a pas encore de photo : le logo sur fond transparent. */
function imageParDefaut(): string
{
    return imageLocale('produit-defaut') ?? BASE_URL . 'assets/images/logo/logo.png';
}

/**
 * Photo d'un produit, dans cet ordre de priorité :
 * 1. photo envoyée depuis l'administration ;
 * 2. photo déposée dans assets/images/produits/ sous le nom du produit (ex. marinade-poulet.webp) ;
 * 3. image par défaut (logo).
 */
function imageProduit(array $produit): string
{
    if (!empty($produit['image']) && is_file(UPLOAD_PATH . 'produits/' . $produit['image'])) {
        return UPLOAD_URL . 'produits/' . $produit['image'];
    }
    if (!empty($produit['slug']) && ($locale = imageLocale('produits/' . $produit['slug']))) {
        return $locale;
    }
    return imageParDefaut();
}

/**
 * Vrai si la photo du produit est un JPG : elle remplit alors toute la vignette.
 * Une photo détourée en PNG ou WEBP transparent garde le fond coloré de la charte.
 */
function produitAPhoto(array $produit): bool
{
    return (bool) preg_match('/\.(jpe?g)$/i', strtok(imageProduit($produit), '?'));
}

/** Image d'une gamme : envoi depuis l'administration, puis assets/images/gammes/<slug>, puis image par défaut. */
function imageCategorie(array $categorie): string
{
    if (!empty($categorie['image']) && is_file(UPLOAD_PATH . 'categories/' . $categorie['image'])) {
        return UPLOAD_URL . 'categories/' . $categorie['image'];
    }
    return imageLocale('gammes/' . $categorie['slug']) ?? imageParDefaut();
}

/**
 * Déclaration de la police Cream Heavy, uniquement si son fichier est présent dans assets/fonts/.
 * Sans fichier, rien n'est déclaré : le navigateur ne tente plus 4 téléchargements en erreur à chaque page.
 */
function stylePoliceTitre(): string
{
    $formats = ['woff2' => 'woff2', 'woff' => 'woff', 'ttf' => 'truetype', 'otf' => 'opentype'];
    foreach ($formats as $extension => $format) {
        $fichier = ROOT_PATH . 'assets/fonts/cream-heavy.' . $extension;
        if (is_file($fichier)) {
            $url = BASE_URL . 'assets/fonts/cream-heavy.' . $extension . '?v=' . filemtime($fichier);
            return '<style>@font-face { font-family: "Cream Heavy"; src: url("' . e($url) . '") format("' . $format . '");'
                . ' font-weight: 100 900; font-style: normal; font-display: swap; }</style>';
        }
    }
    return '';
}

/**
 * Logo de la marque.
 * $surFondSombre = true pour le pied de page bordeaux : on utilise alors logo-clair s'il existe.
 * Ordre : logo envoyé depuis Paramètres, puis assets/images/logo/logo(.png/.jpg/.webp), puis le nom en texte.
 */
function getLogo(bool $surFondSombre = false): string
{
    $alt = e(SITE_NAME);
    if ($surFondSombre && ($clair = imageLocale('logo/logo-clair'))) {
        return '<img src="' . e($clair) . '" alt="' . $alt . '" class="logo-img">';
    }
    $logo = getParam('logo');
    $url = ($logo !== '' && is_file(UPLOAD_PATH . 'logo/' . $logo)) ? UPLOAD_URL . 'logo/' . $logo : imageLocale('logo/logo');
    if ($url) {
        $classe = $surFondSombre ? 'logo-img logo-sur-pastille' : 'logo-img';
        return '<img src="' . e($url) . '" alt="' . $alt . '" class="' . $classe . '">';
    }
    return '<span class="logo-texte">Marin’Or <small>Ivoire</small></span>';
}

/**
 * Enregistre une image envoyée par formulaire après vérification du type réel
 * (finfo) et de la taille. Retourne le nom du fichier créé, ou lève une exception.
 */
function uploadImage(array $fichier, string $dossier): string
{
    if (($fichier['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
        throw new RuntimeException("L'envoi de l'image a échoué. Veuillez réessayer.");
    }
    if ($fichier['size'] > UPLOAD_MAX_SIZE) {
        throw new RuntimeException("L'image dépasse la taille maximale de 5 Mo.");
    }
    $mime = (new finfo(FILEINFO_MIME_TYPE))->file($fichier['tmp_name']);
    if (!isset(UPLOAD_MIME_AUTORISES[$mime])) {
        throw new RuntimeException('Format non accepté. Utilisez une image JPG, PNG ou WEBP.');
    }
    $nom = bin2hex(random_bytes(12)) . '.' . UPLOAD_MIME_AUTORISES[$mime];
    $destination = UPLOAD_PATH . $dossier . '/' . $nom;
    if (!move_uploaded_file($fichier['tmp_name'], $destination)) {
        throw new RuntimeException("Impossible d'enregistrer l'image sur le serveur.");
    }
    return $nom;
}

function supprimerImage(?string $nom, string $dossier): void
{
    if ($nom && preg_match('/^[a-f0-9]{24}\.(jpg|png|webp)$/', $nom)) {
        $chemin = UPLOAD_PATH . $dossier . '/' . $nom;
        if (is_file($chemin)) {
            unlink($chemin);
        }
    }
}

// ---------------------------------------------------------------
// Sécurité : CSRF, limitation de débit, validations
// ---------------------------------------------------------------

function genererTokenCSRF(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function champCSRF(): string
{
    return '<input type="hidden" name="csrf_token" value="' . e(genererTokenCSRF()) . '">';
}

function verifierTokenCSRF(?string $token): bool
{
    return is_string($token) && !empty($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

/** Vérifie le jeton CSRF d'une requête POST ou interrompt le traitement. */
function exigerCSRF(): void
{
    if (!verifierTokenCSRF($_POST['csrf_token'] ?? null)) {
        flash('erreur', 'Votre session a expiré. Veuillez réessayer.');
        redirect($_SERVER['REQUEST_URI'] ?? BASE_URL);
    }
}

/** Retourne true si l'action $cle a été effectuée $max fois ou plus pendant $duree secondes. */
function rateLimitDepasse(string $cle, int $max, int $duree): bool
{
    $maintenant = time();
    $_SESSION['rate'][$cle] = array_values(array_filter(
        $_SESSION['rate'][$cle] ?? [],
        fn ($t) => $t > $maintenant - $duree
    ));
    return count($_SESSION['rate'][$cle]) >= $max;
}

function rateLimitEnregistrer(string $cle): void
{
    $_SESSION['rate'][$cle][] = time();
}

/** Numéro ivoirien : +225 facultatif puis 10 chiffres (espaces autorisés). */
function telephoneValide(string $telephone): bool
{
    $chiffres = preg_replace('/[\s.\-]/', '', $telephone);
    return (bool) preg_match('/^(\+225|00225)?\d{10}$/', $chiffres);
}

function motDePasseValide(string $mdp): bool
{
    return mb_strlen($mdp) >= 8 && preg_match('/[A-Z]/', $mdp) && preg_match('/[a-z]/', $mdp) && preg_match('/\d/', $mdp);
}

// ---------------------------------------------------------------
// Libellés
// ---------------------------------------------------------------

function libelleStatutCommande(string $statut): string
{
    return [
        'en_attente'     => 'En attente de paiement',
        'payee'          => 'Payée',
        'en_preparation' => 'En préparation',
        'expediee'       => 'En cours de livraison',
        'livree'         => 'Livrée',
        'annulee'        => 'Annulée',
    ][$statut] ?? $statut;
}

function libelleMethodePaiement(string $methode): string
{
    return [
        'wave'         => 'Wave',
        'orange_money' => 'Orange Money',
        'moov_money'   => 'Moov Money',
        'djamo'        => 'Djamo',
    ][$methode] ?? $methode;
}

function libelleStatutPaiement(string $statut): string
{
    return [
        'en_attente'     => 'En attente',
        'en_verification' => 'À vérifier',
        'valide'         => 'Validé',
        'refuse'         => 'Refusé',
    ][$statut] ?? $statut;
}

/** Numéro marchand à afficher pour chaque moyen de paiement (paramètres du site). */
function numeroPaiement(string $methode): string
{
    return getParam($methode . '_numero', 'Numéro à définir dans les paramètres');
}

function genererReferenceCommande(): string
{
    return 'MO-' . date('ymd') . '-' . strtoupper(bin2hex(random_bytes(3)));
}

// ---------------------------------------------------------------
// Composants d'affichage réutilisables
// ---------------------------------------------------------------

/** Carte produit utilisée dans le catalogue, l'accueil et les suggestions. */
function carteProduit(array $p): string
{
    $url = BASE_URL . 'product.php?slug=' . rawurlencode($p['slug']);
    $enStock = (int) $p['stock'] > 0;
    ob_start(); ?>
    <article class="carte-produit carte-<?= e($p['conditionnement']) ?><?= produitAPhoto($p) ? ' avec-photo' : '' ?>">
        <a href="<?= e($url) ?>" class="carte-produit-visuel">
            <img src="<?= e(imageProduit($p)) ?>" alt="<?= e($p['nom']) ?>" loading="lazy" width="320" height="320">
        </a>
        <div class="carte-produit-corps">
            <h3><a href="<?= e($url) ?>"><?= e($p['nom']) ?></a></h3>
            <?php if (!empty($p['contenance'])): ?><p class="carte-produit-contenance"><?= e($p['contenance']) ?></p><?php endif; ?>
            <p class="carte-produit-texte"><?= e($p['description_courte']) ?></p>
            <div class="carte-produit-pied">
                <span class="prix"><?= formatPrix((int) $p['prix']) ?></span>
                <?php if ($enStock): ?>
                    <form action="<?= BASE_URL ?>panier.php" method="post" data-ajout-panier>
                        <?= champCSRF() ?>
                        <input type="hidden" name="action" value="ajouter">
                        <input type="hidden" name="produit_id" value="<?= (int) $p['id'] ?>">
                        <input type="hidden" name="quantite" value="1">
                        <button type="submit" class="bouton bouton-bordeaux bouton-petit">Ajouter au panier</button>
                    </form>
                <?php else: ?>
                    <span class="rupture">Bientôt de retour</span>
                <?php endif; ?>
            </div>
        </div>
    </article>
    <?php
    return ob_get_clean();
}
