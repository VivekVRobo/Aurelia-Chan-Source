/* Active Aurelia frontend bootstrap.
 *
 * The legacy UI remains available for visual/canon tooling, but safety-sensitive
 * interaction handlers are replaced by frontend/integrity_patch.js before the
 * user can interact with the page.
 */
(function bootstrapAureliaFrontend() {
  if (document.readyState === 'loading') {
    document.write('<script src="frontend/cognitive_contract.js?v=1"><\/script>');
    document.write('<script src="app_legacy.js?v=6"><\/script>');
    document.write('<script src="frontend/integrity_patch.js?v=1"><\/script>');
    return;
  }

  throw new Error('Aurelia frontend bootstrap must execute during document parsing');
})();
