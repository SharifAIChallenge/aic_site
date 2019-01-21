$('.ui.dropdown').dropdown();

$('#navbar').sticky({context: '#main'});

$('.ui.accordion').accordion();

$('.popup-link').popup();


$(document)
    .ready(function () {
        var navbar = $('#navbar');
        navbar.css('z-index', '999');

        $('time').attr("dir", "ltr");

        var img = $('#pattern');


        images = ['pattern1.png','pattern2.png','pattern3.png','pattern4.png','pattern5.png'];
        var i = 0;
        setInterval(function(){
        //img.css('background-image', 'url(/static/images/' + images[i] +')');
        img.fadeTo(100, 0.1, function()
        {
            $(this).css('background-image', 'url(/static/images/' + images[i] +')');
        }).fadeTo(100, 1);
        if(i == (images.length - 1)){
            i = 0;
        } else {
            i++;
        }
    }, 3000);

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



