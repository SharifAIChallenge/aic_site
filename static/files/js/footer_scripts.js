$('.ui.dropdown').dropdown();

$('#navbar').sticky({context: '#main'});

$('.ui.accordion').accordion();

$('.popup-link').popup();


$(document)
    .ready(function () {
        var navbar = $('#navbar');
        navbar.css('z-index', '999');

        $('time').attr("dir", "ltr");

    })
    .scroll(function(){
        var navbar = $('#navbar');
        navbar.css('z-index', '999');

        var scrollY = window.pageYOffset;
        var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

        if (scrollY >= 30) {
            navbar.addClass('reverse-navbar-color');
            navbar.removeClass('navbar-color');
        }
        else {
            navbar.addClass('navbar-color');
            navbar.removeClass('reverse-navbar-color');
        }

    });



