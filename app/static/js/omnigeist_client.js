omni_height = 150;
omni_width = 700;
_jq_script=document.createElement('script');
_jq_script.type='text/javascript';
_jq_script.src='https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js';
document.documentElement.appendChild(_jq_script);
var domLoaded = function (callback) {
    /* Internet Explorer */
    /*@cc_on
    @if (@_win32 || @_win64)
        document.write('<script id="ieScriptLoad" defer src="//:"><\/script>');
        document.getElementById('ieScriptLoad').onreadystatechange = function() {
            if (this.readyState == 'complete') {
                callback();
            }
        };
    @end @*/
    /* Mozilla, Chrome, Opera */
    if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', callback, false);
    }
    /* Safari, iCab, Konqueror */
    if (/KHTML|WebKit|iCab/i.test(navigator.userAgent)) {
        var DOMLoadTimer = setInterval(function () {
            if (/loaded|complete/i.test(document.readyState)) {
                callback();
                clearInterval(DOMLoadTimer);
            }
        }, 10);
    }
    /* Other web browsers */
    window.onload = callback;
};

domLoaded(function() {
        $('<div id="omnigeist"></div>').appendTo('body');
        $('<div id="omnigeist-spacer"></div>').appendTo('body');
        $('#omnigeist').css('top', $(window).height() - omni_height);
        $('#omnigeist').css('left', ($(window).width() - omni_width)/2);
        //$('#omnigeist').addClass('omnigeist');
        //$('#omnigeist').append('<p></p>');
        $.ajax({
            url: "http://localhost:8084/top.js",
            dataType: 'jsonp',
            data: ({idx: '1', provider: 'digg', url: window.location.href}),
            context: $('#omnigeist'),
            success: function(data){
                $(this).text(data['body']);
                //alert(data['body']);
            }});
    });
