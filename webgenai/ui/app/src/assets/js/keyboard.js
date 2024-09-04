function __triggerKeyboardEvent(el, keyCode) {
  var eventObj = document.createEventObject ?
    document.createEventObject() : document.createEvent("Events");

  if (eventObj.initEvent) {
    eventObj.initEvent("keydown", true, true);
  }

  eventObj.keyCode = keyCode;
  eventObj.which = keyCode;

  el.dispatchEvent ? el.dispatchEvent(eventObj) : el.fireEvent("onkeydown", eventObj);

}


onDomChange(function () {
  setTimeout(function () {
    __triggerKeyboardEvent(document.body, parseInt("13"));
  }, 0);
}, 0);



