<?php
/**
 * cart.php — Panier stocké en session : [id_produit => quantité].
 * Le panier persiste pendant toute la visite, sans forcer la commande.
 */

function panierBrut(): array
{
    return $_SESSION['panier'] ?? [];
}

function panierNombreArticles(): int
{
    return array_sum(panierBrut());
}

/** Ajoute une quantité d'un produit actif, en respectant le stock disponible. Retourne la quantité finale. */
function panierAjouter(int $produitId, int $quantite = 1): int
{
    $produit = produitActif($produitId);
    if (!$produit || $quantite < 1) {
        return 0;
    }
    $actuelle = $_SESSION['panier'][$produitId] ?? 0;
    $nouvelle = min($actuelle + $quantite, (int) $produit['stock'], QUANTITE_MAX_PAR_PRODUIT);
    if ($nouvelle > 0) {
        $_SESSION['panier'][$produitId] = $nouvelle;
    }
    return $nouvelle;
}

/** Fixe la quantité d'une ligne ; 0 supprime la ligne. */
function panierModifier(int $produitId, int $quantite): void
{
    if ($quantite <= 0) {
        panierRetirer($produitId);
        return;
    }
    $produit = produitActif($produitId);
    if ($produit) {
        $_SESSION['panier'][$produitId] = min($quantite, (int) $produit['stock'], QUANTITE_MAX_PAR_PRODUIT);
    }
}

function panierRetirer(int $produitId): void
{
    unset($_SESSION['panier'][$produitId]);
}

function panierVider(): void
{
    unset($_SESSION['panier']);
}

function produitActif(int $produitId): ?array
{
    $stmt = getDB()->prepare('SELECT id, stock FROM products WHERE id = ? AND actif = 1');
    $stmt->execute([$produitId]);
    return $stmt->fetch() ?: null;
}

/**
 * Détail complet du panier : lignes avec produits à jour (prix, stock),
 * sous-total, frais de livraison et total. Les produits devenus indisponibles sont retirés.
 */
function panierDetails(): array
{
    $brut = panierBrut();
    $lignes = [];
    $sousTotal = 0;

    if ($brut) {
        $ids = array_map('intval', array_keys($brut));
        $marqueurs = implode(',', array_fill(0, count($ids), '?'));
        $stmt = getDB()->prepare(
            "SELECT p.*, c.nom AS categorie_nom FROM products p
             JOIN categories c ON c.id = p.category_id
             WHERE p.id IN ($marqueurs) AND p.actif = 1"
        );
        $stmt->execute($ids);
        $produits = [];
        foreach ($stmt->fetchAll() as $p) {
            $produits[(int) $p['id']] = $p;
        }

        foreach ($brut as $id => $quantite) {
            $id = (int) $id;
            if (!isset($produits[$id]) || (int) $produits[$id]['stock'] < 1) {
                panierRetirer($id);
                continue;
            }
            $quantite = min((int) $quantite, (int) $produits[$id]['stock']);
            $_SESSION['panier'][$id] = $quantite;
            $totalLigne = $quantite * (int) $produits[$id]['prix'];
            $sousTotal += $totalLigne;
            $lignes[] = ['produit' => $produits[$id], 'quantite' => $quantite, 'total' => $totalLigne];
        }
    }

    $frais = fraisLivraison($sousTotal);
    return [
        'lignes'     => $lignes,
        'sous_total' => $sousTotal,
        'frais'      => $frais,
        'total'      => $sousTotal + $frais,
    ];
}

/** Livraison offerte au-delà du seuil défini dans les paramètres. */
function fraisLivraison(int $sousTotal): int
{
    if ($sousTotal === 0) {
        return 0;
    }
    $seuil = (int) getParam('livraison_offerte_des', '0');
    if ($seuil > 0 && $sousTotal >= $seuil) {
        return 0;
    }
    return (int) getParam('frais_livraison', '0');
}
