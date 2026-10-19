/* Marin'Or Ivoire — interactions de l'administration */
(function () {
  'use strict';

  document.querySelectorAll('form[data-confirmation]').forEach(function (form) {
    form.addEventListener('submit', function (evenement) {
      if (!window.confirm(form.getAttribute('data-confirmation'))) { evenement.preventDefault(); }
    });
  });

  var champFichier = document.querySelector('[data-fichier-apercu]');
  var apercu = document.querySelector('[data-apercu]');
  if (champFichier && apercu) {
    champFichier.addEventListener('change', function () {
      var fichier = champFichier.files && champFichier.files[0];
      if (fichier && fichier.type.indexOf('image/') === 0) {
        apercu.src = URL.createObjectURL(fichier);
      }
    });
  }
})();
