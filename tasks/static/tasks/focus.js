(function () {
  var el = document.getElementById('timer');
  if (!el) return;
  var elapsed = parseInt(el.getAttribute('data-elapsed'), 10) || 0;
  var startedAt = Date.now();

  function pad(n) { return n < 10 ? '0' + n : String(n); }

  function format(total) {
    var h = Math.floor(total / 3600);
    var m = Math.floor((total % 3600) / 60);
    var s = total % 60;
    return h > 0 ? h + ':' + pad(m) + ':' + pad(s) : pad(m) + ':' + pad(s);
  }

  function tick() {
    var total = elapsed + Math.floor((Date.now() - startedAt) / 1000);
    el.textContent = format(total);
  }

  tick();
  setInterval(tick, 1000);
})();
