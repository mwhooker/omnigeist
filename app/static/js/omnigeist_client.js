/*
 * TODO:
 *  namespace this file. i.e. put it in a function
 *  check if jquery is on the page already
 */
omni_height = 150;
omni_width = 700;
_jq_script=document.createElement('script');
_jq_script.type='text/javascript';
_jq_script.src='https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js';
document.documentElement.appendChild(_jq_script);

jqueryLoaded = function(callback) {
    tryReady = function(time_elapsed) {
        // Continually polls to see if jQuery is loaded.
        if (typeof $ == "undefined") { // if jQuery isn't loaded yet...
            if (time_elapsed <= 5000) {
                setTimeout("tryReady(" + (time_elapsed + 200) + ")", 200);
            } else {
                alert("Timed out while loading jQuery.")
            }
        } else {
            // jQuery loaded successfully
            callback();
        }
    }
    return tryReady(0);
}

comment_tpl = '<div class="omnigeist"><p><%=body%> &mdash; <%=author%></p></div>';

update_comments = function(idx, provider) {
    $.ajax({
        url: "http://localhost:8084/top.js",
        dataType: 'jsonp',
        data: ({idx: idx, provider: provider, url: window.location.href}),
        success: function(data){
            $('.omnigeist').replaceWith(tmpl(comment_tpl, data));
    }});
}


main = function() {
    $('<div id="omnigeist"><div class="omnigeist"></div></div>').appendTo('body');
    update_comments(1, 'reddit');
    //$('#omnigeist').addClass('omnigeist');
    //$('#omnigeist').append('<p></p>');
}

jqueryLoaded(function() {
    $.getScript('http://localhost:8084/static/js/template.js', function() {
        main();
    });
});


