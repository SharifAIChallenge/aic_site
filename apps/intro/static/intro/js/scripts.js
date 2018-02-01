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

