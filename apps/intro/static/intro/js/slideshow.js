var slideIndex = 3;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
    slideIndex += n;
  showSlides(slideIndex);
}

// Thumbnail image controls
function currentSlide(n) {
    slideIndex = n;
  showSlides(slideIndex);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("dot-slide");
  var timeline = document.getElementsByClassName('timelineStoriesText');
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
  timeline.style.height = "700px";
}