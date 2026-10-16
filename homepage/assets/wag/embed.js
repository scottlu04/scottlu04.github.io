/* Size this same-origin frame to its controls, graph and metric details. */
(function () {
  var content = document.querySelector('.embed-content');
  var scheduled = false;
  function resize() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(function () {
      scheduled = false;
      if (window.frameElement) {
        var height = Math.ceil(content.getBoundingClientRect().height) + 2;
        if (window.frameElement.style.height !== height + 'px') {
          window.frameElement.style.height = height + 'px';
        }
      }
    });
  }
  new ResizeObserver(resize).observe(content);
  window.addEventListener('load', resize);
  resize();
})();
