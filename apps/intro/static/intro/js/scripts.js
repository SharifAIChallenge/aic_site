function setAnimation(selector, animation, delay=0) {
    $(selector).on('inview', function(event, isInView) {
      if (isInView) {
        // element is now visible in the viewport
        theThis = this;
        setTimeout(function(){
            //do what you need here
            $(theThis).transition(animation);
            $(theThis).unbind('inview');
        }, delay);
      } else {
        // element has gone out of viewport
      }
    });
}

$(document).ready(function () {
    $('.section.header .ai.button').css('margin-top', '-50%');
    // setAnimation('.banner.text.image', 'scale in');
    setAnimation('#head-logo, #seven-million', 'tada', 1000);
    setAnimation('#champion-cup', 'scale in');
});


$(document).on('click', 'a[href^="#"]', function (event) {
    event.preventDefault();

    $('html, body').animate({
        scrollTop: $($.attr(this, 'href')).offset().top
    }, 500);
});

$(document).ready(function(){
    $('iframe#google_maps_iframe').attr('src', 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3239.9627430847677!2d51.34888151486223!3d35.702534430189345!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3f8e00a61f30034b%3A0xe59caa3900cd3c54!2sTehran+Province%2C+Tehran%2C+Azadi+St%2C+Dept.+of+Computer+Eng.%2C+Iran!5e0!3m2!1sen!2s!4v1516927405125');
});

