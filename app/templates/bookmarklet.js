javascript:(function(){
    _omnigeist_script=document.createElement('script');
    _omnigeist_script.type='text/javascript';
    _omnigeist_script.src='{{ host }}/static/js/omnigeist_client.js?x='+(Math.random());
    document.documentElement.appendChild(_omnigeist_script);
    _omnigeist_css=document.createElement('link');
    _omnigeist_css.rel='stylesheet';
    _omnigeist_css.href='{{ host }}/static/css/omnigeist_client.css';
    _omnigeist_css.type='text/css';
    _omnigeist_css.media='all';
    document.documentElement.appendChild(_omnigeist_css);})();
