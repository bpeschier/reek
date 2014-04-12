function ContentEditor(container) {
  this.container = document.querySelector(container);

  this.init();
}

ContentEditor.prototype = {
  init: function() {
    console.log('Container:', this.container);
  }
};