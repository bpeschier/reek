function RegionEditor(container) {
  this.container = document.querySelector(container);

  this.init();
}

RegionEditor.prototype = {
  init: function() {
    console.log('Container:', this.container);
  }
};