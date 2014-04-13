function ContentEditor(container) {
  this.container = document.querySelector(container);
  this.editors = this.container.querySelector('.contenteditor-editors');
  this.nodeEditor = this.editors.querySelector('.contenteditor-nodes');

  if (document.getSelection) {
    this.init();
  } else {
    this.warn();
  }
}

ContentEditor.prototype = {
  init: function () {
    // Set contentEditable
    this.nodeEditor.contentEditable = true;
    this.nodeEditor.addEventListener('keyup', this);
    this.nodeEditor.addEventListener('keydown', this);
    this.nodeEditor.addEventListener('focus', this);

  },

  warn: function () {
    this.nodeEditor.innerHTML = '<span class="contenteditor-warning">Editor not supported</span>';
  },

  handleEvent: function (ev) {
    if (ev.type == 'keyup') {
      return this.handleUp(ev);
    } else if (ev.type == 'keydown') {
      return this.handleDown(ev);
    }
  },
  handleUp: function (ev) {
  },
  handleDown: function (ev) {


  }

};