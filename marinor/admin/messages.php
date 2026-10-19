<?php
require_once dirname(__DIR__) . '/includes/functions.php';
exigerAdmin();

$pdo = getDB();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    exigerCSRF();
    $id = (int) ($_POST['id'] ?? 0);
    if (($_POST['action'] ?? '') === 'lu') {
        $pdo->prepare('UPDATE messages SET lu = 1 - lu WHERE id = ?')->execute([$id]);
    } elseif (($_POST['action'] ?? '') === 'supprimer') {
        $pdo->prepare('DELETE FROM messages WHERE id = ?')->execute([$id]);
        flash('succes', 'Message supprimé.');
    }
    redirect(BASE_URL . 'admin/messages.php');
}

$messages = $pdo->query('SELECT * FROM messages ORDER BY lu ASC, created_at DESC')->fetchAll();

$adminTitre = 'Messages';
$adminActif = 'messages.php';
require __DIR__ . '/_debut.php';
?>
<?php if (!$messages): ?>
    <section class="panneau"><p class="vide">Aucun message reçu pour le moment.</p></section>
<?php endif; ?>
<?php foreach ($messages as $m): ?>
<article class="panneau message<?= $m['lu'] ? '' : ' message-nouveau' ?>" id="message-<?= (int) $m['id'] ?>">
    <header class="message-entete">
        <div>
            <strong><?= e($m['nom']) ?></strong> — <?= e($m['sujet']) ?>
            <p class="aide"><a href="mailto:<?= e($m['email']) ?>?subject=<?= rawurlencode('Re : ' . $m['sujet']) ?>"><?= e($m['email']) ?></a>
                <?= $m['telephone'] ? ' / ' . e($m['telephone']) : '' ?> / <?= formatDate($m['created_at'], true) ?></p>
        </div>
        <div class="groupe-boutons">
            <form method="post"><?= champCSRF() ?><input type="hidden" name="id" value="<?= (int) $m['id'] ?>"><input type="hidden" name="action" value="lu">
                <button type="submit" class="bouton bouton-secondaire"><?= $m['lu'] ? 'Marquer comme non lu' : 'Marquer comme lu' ?></button></form>
            <form method="post" data-confirmation="Supprimer ce message ?"><?= champCSRF() ?><input type="hidden" name="id" value="<?= (int) $m['id'] ?>"><input type="hidden" name="action" value="supprimer">
                <button type="submit" class="lien-danger">Supprimer</button></form>
        </div>
    </header>
    <p><?= nl2br(e($m['message'])) ?></p>
</article>
<?php endforeach; ?>
<?php require __DIR__ . '/_fin.php';
