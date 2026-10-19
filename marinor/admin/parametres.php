<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();
$champs = [
    'Informations de la boutique' => [
        'slogan' => 'Slogan', 'description' => 'Présentation de la marque', 'adresse' => 'Adresse',
        'telephone' => 'Téléphone', 'whatsapp' => 'WhatsApp', 'email' => 'E-mail de contact', 'horaires' => 'Horaires',
    ],
    'Réseaux sociaux (adresses complètes)' => ['facebook' => 'Facebook', 'instagram' => 'Instagram', 'tiktok' => 'TikTok'],
    'Livraison (en FCFA)' => ['frais_livraison' => 'Frais de livraison', 'livraison_offerte_des' => 'Livraison offerte à partir de (0 = jamais)'],
    'Numéros marchands de paiement' => [
        'wave_numero' => 'Wave', 'orange_money_numero' => 'Orange Money', 'moov_money_numero' => 'Moov Money', 'djamo_numero' => 'Djamo',
    ],
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $action = $_POST['action'] ?? '';

    if ($action === 'parametres') {
        $maj = $pdo->prepare('INSERT INTO settings (cle, valeur) VALUES (?, ?) ON DUPLICATE KEY UPDATE valeur = VALUES(valeur)');
        foreach ($champs as $groupe) {
            foreach (array_keys($groupe) as $cle) {
                $valeur = trim(valeurTexte($_POST, $cle));
                if (in_array($cle, ['frais_livraison', 'livraison_offerte_des'], true)) {
                    $valeur = (string) max(0, (int) $valeur);
                }
                $maj->execute([$cle, $valeur]);
            }
        }
        if (($_FILES['logo']['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
            try {
                $nom = uploadImage($_FILES['logo'], 'logo');
                supprimerImage(getParam('logo'), 'logo');
                $maj->execute(['logo', $nom]);
            } catch (RuntimeException $ex) {
                flash('erreur', $ex->getMessage());
            }
        }
        flash('succes', 'Paramètres enregistrés.');
    } elseif ($action === 'mot_de_passe') {
        $stmt = $pdo->prepare('SELECT mot_de_passe FROM admins WHERE id = ?');
        $stmt->execute([$_SESSION['admin_id']]);
        $hash = (string) $stmt->fetchColumn();
        $nouveau = valeurTexte($_POST, 'nouveau');
        if (!password_verify(valeurTexte($_POST, 'actuel'), $hash)) {
            flash('erreur', 'Le mot de passe actuel est incorrect.');
        } elseif (!motDePasseValide($nouveau)) {
            flash('erreur', 'Le nouveau mot de passe doit contenir 8 caractères, une majuscule, une minuscule et un chiffre.');
        } else {
            $pdo->prepare('UPDATE admins SET mot_de_passe = ? WHERE id = ?')->execute([password_hash($nouveau, PASSWORD_DEFAULT), $_SESSION['admin_id']]);
            flash('succes', 'Mot de passe administrateur modifié.');
        }
    }
    redirect(BASE_URL . 'admin/parametres.php');
}

$adminTitre = 'Paramètres';
$adminActif = 'parametres.php';
require __DIR__ . '/_debut.php';
?>
<form method="post" enctype="multipart/form-data" class="formulaire-admin">
    <?= champCSRF() ?>
    <input type="hidden" name="action" value="parametres">
    <div>
        <?php foreach ($champs as $titre => $groupe): ?>
        <section class="panneau">
            <h2><?= e($titre) ?></h2>
            <?php foreach ($groupe as $cle => $libelle): ?>
                <div class="champ">
                    <label for="<?= $cle ?>"><?= e($libelle) ?></label>
                    <?php if ($cle === 'description'): ?>
                        <textarea id="<?= $cle ?>" name="<?= $cle ?>" rows="4"><?= e(getParam($cle)) ?></textarea>
                    <?php else: ?>
                        <input id="<?= $cle ?>" name="<?= $cle ?>" value="<?= e(getParam($cle)) ?>">
                    <?php endif; ?>
                </div>
            <?php endforeach; ?>
        </section>
        <?php endforeach; ?>
    </div>
    <div class="pile">
        <section class="panneau">
            <h2>Logo</h2>
            <div class="apercu-logo"><?= getLogo() ?></div>
            <div class="champ"><label for="logo">Nouveau logo (PNG transparent conseillé)</label><input id="logo" name="logo" type="file" accept="image/png,image/jpeg,image/webp"></div>
        </section>
        <button type="submit" class="bouton bouton-large">Enregistrer les paramètres</button>
    </div>
</form>

<section class="panneau panneau-etroit">
    <h2>Mot de passe administrateur</h2>
    <form method="post" class="formulaire-ligne">
        <?= champCSRF() ?>
        <input type="hidden" name="action" value="mot_de_passe">
        <div class="champ"><label for="actuel">Mot de passe actuel</label><input id="actuel" name="actuel" type="password" required autocomplete="current-password"></div>
        <div class="champ"><label for="nouveau">Nouveau mot de passe</label><input id="nouveau" name="nouveau" type="password" required autocomplete="new-password"></div>
        <button type="submit" class="bouton">Changer le mot de passe</button>
    </form>
</section>
<?php require __DIR__ . '/_fin.php';
