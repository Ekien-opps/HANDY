/* Marin'Or Ivoire — interactions du site public (aucune dépendance) */
(function () {
  'use strict';

  var corps = document.body;

  /* ---------- Notification ---------- */
  var notification = document.querySelector('[data-notification]');
  var minuteur = null;
  function notifier(message, erreur) {
    if (!notification) { return; }
    notification.textContent = message;
    notification.classList.toggle('erreur', !!erreur);
    notification.hidden = false;
    clearTimeout(minuteur);
    minuteur = setTimeout(function () { notification.hidden = true; }, 3200);
  }

  function envoyer(form) {
    return fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'X-Requested-With': 'fetch', 'Accept': 'application/json' },
      credentials: 'same-origin'
    }).then(function (reponse) { return reponse.json(); });
  }

  /* ---------- Menu mobile ---------- */
  var boutonMenu = document.querySelector('.menu-bouton');
  var menu = document.getElementById('menu-principal');
  if (boutonMenu && menu) {
    boutonMenu.addEventListener('click', function () {
      var ouvert = menu.classList.toggle('ouvert');
      boutonMenu.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
    });
  }

  /* ---------- Ajout au panier sans rechargement ---------- */
  var compteur = document.querySelector('[data-compteur-panier]');
  document.querySelectorAll('[data-ajout-panier]').forEach(function (form) {
    form.addEventListener('submit', function (evenement) {
      evenement.preventDefault();
      var bouton = form.querySelector('[type="submit"]');
      if (bouton) { bouton.disabled = true; }
      envoyer(form).then(function (donnees) {
        notifier(donnees.message, !donnees.ok);
        if (compteur && typeof donnees.nombre === 'number') {
          compteur.textContent = donnees.nombre;
          compteur.hidden = donnees.nombre === 0;
          compteur.classList.remove('pulse');
          void compteur.offsetWidth;
          compteur.classList.add('pulse');
        }
      }).catch(function () {
        form.submit();
      }).finally(function () {
        if (bouton) { bouton.disabled = false; }
      });
    });
  });

  /* ---------- Sélecteur de quantité ---------- */
  document.querySelectorAll('[data-selecteur-quantite]').forEach(function (bloc) {
    var champ = bloc.querySelector('input');
    function ajuster(pas) {
      var max = parseInt(champ.max, 10) || 99;
      var valeur = (parseInt(champ.value, 10) || 1) + pas;
      champ.value = Math.min(Math.max(valeur, 1), max);
    }
    bloc.querySelector('[data-moins]').addEventListener('click', function () { ajuster(-1); });
    bloc.querySelector('[data-plus]').addEventListener('click', function () { ajuster(1); });
  });

  /* ---------- Soumission automatique (tri, quantités du panier) ---------- */
  document.querySelectorAll('[data-soumission-auto]').forEach(function (champ) {
    champ.addEventListener('change', function () { champ.form.submit(); });
  });

  /* ---------- Confirmation avant action sensible ---------- */
  document.querySelectorAll('form[data-confirmation]').forEach(function (form) {
    form.addEventListener('submit', function (evenement) {
      if (!window.confirm(form.getAttribute('data-confirmation'))) { evenement.preventDefault(); }
    });
  });

  /* ---------- Compteur de caractères ---------- */
  document.querySelectorAll('[data-compteur]').forEach(function (zone) {
    var minimum = parseInt(zone.getAttribute('data-compteur'), 10);
    var texte = zone.parentElement.querySelector('[data-compteur-texte]');
    function maj() {
      var n = zone.value.trim().length;
      texte.textContent = n < minimum ? n + ' / ' + minimum + ' caractères minimum' : n + ' caractères';
    }
    zone.addEventListener('input', maj);
    maj();
  });

  /* ---------- Lettre d'information ---------- */
  var formNewsletter = document.querySelector('[data-newsletter]');
  if (formNewsletter) {
    var retour = formNewsletter.querySelector('[data-newsletter-retour]');
    formNewsletter.addEventListener('submit', function (evenement) {
      evenement.preventDefault();
      envoyer(formNewsletter).then(function (donnees) {
        retour.textContent = donnees.message;
        if (donnees.ok) { formNewsletter.reset(); }
      }).catch(function () { formNewsletter.submit(); });
    });
  }

  /* ---------- Bandeau cookies ---------- */
  var bandeau = document.querySelector('[data-bandeau-cookies]');
  var choix = null;
  try { choix = window.localStorage.getItem('marinor_cookies'); } catch (e) { choix = 'indisponible'; }
  if (bandeau && !choix) {
    bandeau.hidden = false;
    bandeau.querySelectorAll('[data-cookies]').forEach(function (bouton) {
      bouton.addEventListener('click', function () {
        try { window.localStorage.setItem('marinor_cookies', bouton.getAttribute('data-cookies')); } catch (e) {}
        bandeau.hidden = true;
      });
    });
  }

  if (corps) { corps.classList.add('js'); }
})();
