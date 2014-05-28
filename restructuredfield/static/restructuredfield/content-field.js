define(['content/content-editor'], function (ContentEditor) {
  function ContentField(container, plugins) {
    this.container = document.querySelector(container);
    this.editors = this.container.querySelector('.contenteditor-editors');
    this.nodeEditor = new ContentEditor(this.editors.querySelector('.contenteditor-nodes'), plugins);

    this.init();
  }

  ContentField.prototype = {
    init: function () {
      // Set contentEditable
      this.nodeEditor.makeEditable();
    }
  };
  return ContentField;
});