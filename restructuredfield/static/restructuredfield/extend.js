define([], function () {
  function extendPrototype(superClass, prototypeProperties) {
    var properties = {};
    for (var prop in prototypeProperties) {
      if (prototypeProperties.hasOwnProperty(prop)) {
        properties[prop] = {
          value: prototypeProperties[prop],
          enumerable: true,
          writable: true,
          configurable: true
        }
      }
    }
    return Object.create(superClass, properties);
  }

  return extendPrototype;
})
