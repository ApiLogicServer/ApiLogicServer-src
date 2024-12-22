(function (window) {
    var last = +new Date();
    var delay = 100; // default delay

    // Manage event queue
    var stack = [];

    function callback() {
        var now = +new Date();
        if (now - last > delay) {
            for (var i = 0; i < stack.length; i++) {
                stack[i]();
            }
            last = now;
        }
    }

    // Public interface
    var onDomChange = function (fn, newdelay) {
        if (newdelay) delay = newdelay;
        stack.push(fn);
    };

    // Naive approach for compatibility
    function naive() {

        var last = document.getElementsByTagName('*');
        var lastlen = last.length;
        setTimeout(function check() {

            // get current state of the document
            var current = document.getElementsByTagName('*');
            var len = current.length;

            // if the length is different
            // it's fairly obvious
            if (len != lastlen) {
                // just make sure the loop finishes early
                last = [];
            }

            // go check every element in order
            for (var i = 0; i < len; i++) {
                if (current[i] !== last[i]) {
                    callback();
                    last = current;
                    lastlen = len;
                    break;
                }
            }

            // over, and over, and over again
            setTimeout(check, delay);

        }, delay);
    }

    //
    //  Check for mutation events support
    //

    var support = {};

    var el = document.documentElement;
    var remain = 3;

    // callback for the tests
    function decide() {
        if (support.DOMNodeInserted) {
            window.addEventListener("DOMContentLoaded", function () {
                if (support.DOMSubtreeModified) { // for FF 3+, Chrome
                    el.addEventListener('DOMSubtreeModified', callback, false);
                } else { // for FF 2, Safari, Opera 9.6+
                    el.addEventListener('DOMNodeInserted', callback, false);
                    el.addEventListener('DOMNodeRemoved', callback, false);
                }
            }, false);
        } else if (document.onpropertychange) { // for IE 5.5+
            document.onpropertychange = callback;
        } else { // fallback
            naive();
        }
    }

    // checks a particular event
    function test(event) {
        el.addEventListener(event, function fn() {
            support[event] = true;
            el.removeEventListener(event, fn, false);
            if (--remain === 0) decide();
        }, false);
    }

    // attach test events
    if (window.addEventListener) {
        test('DOMSubtreeModified');
        test('DOMNodeInserted');
        test('DOMNodeRemoved');
    } else {
        decide();
    }

    // do the dummy test
    var dummy = document.createElement("div");
    el.appendChild(dummy);
    el.removeChild(dummy);

    // expose
    window.onDomChange = onDomChange;
})(window);