define([], function () {
  /**
   * Plugins control a specific type of content. It is responsible for
   * providing a visual interface for the content and converting it to
   * reStructuredText.
   * @constructor
   */
  function Plugin() {
    this.init();
  }

  Plugin.prototype = {
    init: function () {
    }
  };

  return Plugin;
});