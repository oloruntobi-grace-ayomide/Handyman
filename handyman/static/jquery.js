$(function() {
    $(window).on('scroll', function() {
        var scroller = $(window).scrollTop();
        
        if (scroller > 60) {
            $('.nav-grand-parent, .offcanvas-nav-grand-parent').addClass('style-changer-style');
        } else if (scroller <= 600) {
            $('.nav-grand-parent, .offcanvas-nav-grand-parent').removeClass('style-changer-style');
        }
    });
});


  
 

   

