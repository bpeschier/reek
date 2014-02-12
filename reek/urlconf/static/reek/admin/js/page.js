(function () {

  var Page = function (el) {
    this.el = el;
    this.children = this.getChildren();
  };

  Page.prototype = {
    getChildRoot: function () {
      return Array.prototype.slice.call(this.el.children).filter(function (el) {
        return el.tagName == "OL";
      })[0];
    },
    getChildren: function () {
      var root = this.getChildRoot();
      if (root != null) {
        return Array.prototype.slice.call(this.getChildRoot().children).filter(function (el) {
          return el.classList.contains('reek-child');
        }).map(function (el) {
          return new Page(el);
        });
      } else {
        return [];
      }
    }

  };

  window.addEventListener('load', function () {

    var trees = Array.prototype.slice.call(document.querySelectorAll('.reek-root')).map(function (el) {
      return new Page(el);
    });


  });

})();
