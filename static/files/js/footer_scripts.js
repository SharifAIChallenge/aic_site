$('.ui.dropdown').dropdown();

$('#navbar').sticky({context: '#main'});

$('.ui.accordion').accordion();

$(document)
    .ready(function () {
        var navbar = $('#navbar');
        var height = -1 * navbar.height();
        navbar.css('margin-bottom', height);
        navbar.css('z-index', '999');
    })
    .scroll(function(){
        var navbar = $('#navbar');
        var height = -1 * navbar.height();
        navbar.css('margin-bottom', height);
        navbar.css('z-index', '999');

        var scrollY = window.pageYOffset;
        var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

        if (scrollY >= h) {
            navbar.addClass('reverse-navbar-color');
            navbar.removeClass('navbar-color');
        }
        else {
            navbar.addClass('navbar-color');
            navbar.removeClass('reverse-navbar-color');
        }

});


