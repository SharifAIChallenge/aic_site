// (function($) {
//
//   $.fn.visible = function(partial) {
//
//       var $t            = $(this),
//           $w            = $(window),
//           viewTop       = $w.scrollTop(),
//           viewBottom    = viewTop + $w.height(),
//           _top          = $t.offset().top,
//           _bottom       = _top + $t.height(),
//           compareTop    = partial === true ? _bottom : _top,
//           compareBottom = partial === true ? _top : _bottom;
//
//     console.log("Top: " + _top + " Bot: " + _bottom + " View: " + viewBottom + "\n Res:" + (viewBottom >= _top+800));
//     return (viewBottom >= _top-100);
//
//   };
//
// })(jQuery);
//
// var win = $(window);
//
// var allMods = $("div#section");
//
// win.scroll(function(event) {
//
//   allMods.each(function(i) {
//     if ($(this).visible(true) && !$(this).is(':visible')) {
//         $(this).fadeIn(3000);
//     }
//   });
//
// });