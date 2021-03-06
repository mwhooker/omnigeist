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

omnigeist_tpl = '{{ client_tpl }}';
comment_tpl = '{{ comment_tpl }}';

(function() {
    var cache = null;

    this.get_comments = function get_comments(idx, provider, success, fail) {

        function _success(data) {
            var provider_data;
            if (provider in data) {
                provider_data = data[provider];
            } else if (provider == undefined) {
                for (var p in data) {
                    if (data[p].length) {
                        provider_data = data[p];
                        provider = p;
                        break;
                    } else {
                        continue;
                    }
                }
            }

            if (provider_data == undefined || !provider_data.length) {
                return fail(provider);
            }
            success(provider_data[0], provider);
        };

        if (cache) {
            _success(cache);
        } else {
            $.ajax({
                url: "http://localhost:8084/top.js",
                dataType: 'jsonp',
                data: ({idx: idx, url: window.location.href}),
                success: function(data) {
                    cache = data;
                    _success(data);
                }
            });
        }
    };
})();


main = function() {
    function set_comments(data, provider) {
        $('.provider').each(function(i) {
          if ($(this).attr('provider') == provider) { 
            $(this).addClass('active-provider');
          } else {
            $(this).removeClass('active-provider');
          }
        });
        $('.comment-container').replaceWith(tmpl(comment_tpl, data));
    };
    function fail(provider) {
      alert("failed to load provider " + provider);
    }

    $('body').append(tmpl(omnigeist_tpl));
    $('#provider-digg, #provider-reddit').click(function() {
        get_comments(1, $(this).attr('provider'), set_comments, fail);
    });
    get_comments(1, 'reddit', set_comments, fail);
}

jqueryLoaded(function() {
    $.getScript('http://localhost:8084/static/js/template.js', function() {
        main();
    });
});


