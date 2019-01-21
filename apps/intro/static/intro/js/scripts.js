

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
    $('#15171308283766309').append('<script type="text/JavaScript" src="https://www.aparat.com/embed/N2Ae4?data[rnddiv]=15171308283766309&data[responsive]=yes"></script>');
    $('iframe#google_maps_iframe').attr('src', 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3239.9627430847677!2d51.34888151486223!3d35.702534430189345!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3f8e00a61f30034b%3A0xe59caa3900cd3c54!2sTehran+Province%2C+Tehran%2C+Azadi+St%2C+Dept.+of+Computer+Eng.%2C+Iran!5e0!3m2!1sen!2s!4v1516927405125');

});



function getTimeRemaining(endtime) {
  var t = Date.parse(endtime) - Date.parse(new Date());
  if (t < 0) t = 0;
  var seconds = Math.floor((t / 1000) % 60);
  var minutes = Math.floor((t / 1000 / 60) % 60);
  var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
  var days = Math.floor(t / (1000 * 60 * 60 * 24));
  return {
    'total': t,
    'days': days,
    'hours': hours,
    'minutes': minutes,
    'seconds': seconds
  };
}

function englishToPersian(value) {
    var nValue = "";
    for (var i = 0; i < value.length; i++) {
        var ch = value.charCodeAt(i);
        if (ch >= 48 && ch <= 57) { // For Persian digits.
            var nChar = ch + 1728;
            nValue = nValue + String.fromCharCode(nChar);
        } else if (ch >= 1632 && ch <= 1641) { // For Arabic & Unix digits.
            var newChar = ch + 144;
            nValue = nValue + String.fromCharCode(newChar);
        } else {
            nValue = nValue + String.fromCharCode(ch);
        }
    }
    return nValue;
}

function initializeClock(id, endtime) {
  var clock = document.getElementById(id);
  var daysSpan = clock.querySelector('.days');
  var hoursSpan = clock.querySelector('.hours');
  var minutesSpan = clock.querySelector('.minutes');
  var secondsSpan = clock.querySelector('.seconds');

  function updateClock() {
    var t = getTimeRemaining(endtime);

    daysSpan.innerHTML = englishToPersian(t.days.toString());
    hoursSpan.innerHTML = englishToPersian(('0' + t.hours).slice(-2));
    minutesSpan.innerHTML = englishToPersian(('0' + t.minutes).slice(-2));
    secondsSpan.innerHTML = englishToPersian(('0' + t.seconds).slice(-2));

    if (t.total <= 0) {
      clearInterval(timeinterval);
    }
  }

  updateClock();
  var timeinterval = setInterval(updateClock, 1000);
}

// start date of SAIC18
var deadline = new Date(Date.parse(new Date(2019, 1, 5, 8, 0, 0, 0)));
initializeClock('clockdiv', deadline);

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

document.getElementsByClassName("close")[0].onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
            modal.style.display = "none";
    }
}




