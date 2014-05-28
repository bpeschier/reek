define([], function () {

  function ContentEditor(element, plugins) {
    this.el = element;
    this.plugins = [];
    this.setupPlugins(plugins);

    if (document.getSelection) {
      this.init();
    } else {
      this.warn();
    }
  }

  ContentEditor.prototype = {
    init: function () {
      this.initEvents();
    },

    setupPlugins: function (plugins) {
      var editor = this;
      require(plugins, function () {
        for (var i = 0; i < arguments.length; i++) {
          editor.addPlugin(new (arguments[i])());
        }
      })
    },

    initEvents: function () {
      this.el.addEventListener('keyup', this);
      this.el.addEventListener('keydown', this);
      this.el.addEventListener('mouseup', this);
      this.el.addEventListener('mousedown', this);
      this.el.addEventListener('touchstart', this);
      this.el.addEventListener('touchend', this);
      this.el.addEventListener('touchcancel', this);
      this.el.addEventListener('focus', this);
    },

    addPlugin: function (plugin) {
      this.plugins.push(plugin);
    },

    warn: function () {
      this.el.innerHTML = '<span class="contenteditor-warning">Browser not supported</span>';
    },

    makeEditable: function () {
      this.el.contentEditable = true;
    },

    handleEvent: function (ev) {
      if (ev.type == "keyup" || ev.type == "mouseup" || ev.type == "touchend") {
        return this.handleUp(ev);
      } else if (ev.type == "keydown" || ev.type == "mousedown" || ev.type == "touchstart") {
        return this.handleDown(ev);
      }
    },
    handleUp: function (ev) {
      this.clean();
    },
    handleDown: function (ev) {
      if (ev.ctrlKey && ev.keyCode == 32) {
        console.log(this.plugins);
      }
    },

    clean: function () {
      for (var idx = 0; idx < this.el.childNodes.length; idx++) {
        var node = this.el.childNodes[idx];
        if (node.nodeName == "#text" && node.nodeValue.trim().length > 0) {
          // Clone into new paragraph
          var clone = node.cloneNode(true);
          var paragraph = document.createElement("P");
          node.parentNode.replaceChild(paragraph, node);
          paragraph.appendChild(clone);

          // Reset selection to cursor
          var selection = window.getSelection();
          var range = document.createRange();
          selection.removeAllRanges();
          range.setStart(clone, 1);
          selection.addRange(range);

        } else if (false && node.nodeName == "div" && node.classList.length == 0) {
          // Move it
          var p = document.createElement("P");
          node.parentNode.replaceChild(p, node);
          for (var i = 0; i < node.childNodes.length; i++) {
            p.appendChild(node.childNodes[i]);
          }
        }
      }

    }
  };

  return ContentEditor;
});
