(function () {

  var Page = function (el, parent) {
    this.el = el;
    this.children = this.getChildren();
    this.parent = parent || null;

    this.x = 0;
    this.y = 0;
    this.width = this.el.clientWidth;
    this.height = this.el.clientHeight;
  };

  Page.prototype = {
    getChildRoot: function () {
      return Array.prototype.slice.call(this.el.children).filter(function (el) {
        return el.tagName == "OL";
      })[0];
    },
    getChildren: function () {
      var root = this.getChildRoot();
      var page = this;
      if (root != null) {
        return Array.prototype.slice.call(this.getChildRoot().children).filter(function (el) {
          return el.classList.contains('reek-child');
        }).map(function (el) {
          return new Page(el, page);
        });
      } else {
        return [];
      }
    },
    getChildWidth: function () {
      return this.children.reduce(function (val, obj) {
        return val + obj.width + 20;
      }, -20);
    },

    /**
     * Layout this page in the view hierarchy
     * Assumes parent is already laid out
     */
    layout: function (container, idx, total) {
      idx = idx || 0;
      total = total || 1;
      var y = (this.parent) ? this.parent.y + this.parent.height + 20 : 0;
      var offsetX = (idx * this.width) + ((idx > 0) ? (idx * 20) : 0);
      if (!this.parent)
        offsetX = (container.clientWidth / 2) - (this.width / 2);
      var x = (this.parent) ? this.parent.x + (this.parent.width / 2) - (this.parent.getChildWidth() / 2) + offsetX : offsetX;

      this.position(x, y);

      var count = this.children.length;
      this.children.forEach(function (page, idx) {
        page.layout(container, idx, count);
      })
    },

    position: function (x, y) {
      this.el.style.webkitTransform = 'translate3d(' + x + 'px,' + y + 'px, 0)';
    }

  };

  window.addEventListener('load', function () {

    var trees = Array.prototype.slice.call(document.querySelectorAll('.reek-root')).map(function (el) {
      return new Page(el);
    });

    trees.forEach(function (page) {
      page.layout(document.querySelector('.reek-pages > ol'));
    });


  });

})();
