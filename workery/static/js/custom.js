$(document).ready(function () {

	$("#sidebar").mCustomScrollbar({
	     theme: "minimal"
	});

	$('#sidebarCollapse').on('click', function () {
	    // open or close navbar
	    $('#sidebar,#main,#sidebarCollapse,#return-to-top,body').toggleClass('active');

	});

        // ===== Scroll to Top ====
	$(window).scroll(function() {
	    if ($(this).scrollTop() >= 100) {        // If page is scrolled more than 50px
	        $('#return-to-top').fadeIn(200);    // Fade in the arrow
	    } else {
	        $('#return-to-top').fadeOut(200);   // Else fade out the arrow
	    }
	});
	$('#return-to-top').click(function() {      // When arrow is clicked
	    $('body,html').animate({
	        scrollTop : 0                       // Scroll to top of body
	    }, 500);
	});

	// ===== Advance search form ====
	$('#advance_search_btn').on('click', function () {
	    $('#adv-search').show();
	    $('#advance_search_btn_x').show();
	    $('#advance_search_btn').hide();
	});
	$('#advance_search_btn_x').on('click', function () {
	    $('#adv-search').hide();
	    $('#advance_search_btn_x').hide();
	    $('#advance_search_btn').show();
	});

	// ===== Residential and Commercial forms toggle ====
	$('#residential').on('click', function () {
	    $('#commercial-form').hide();
	    $('#residential-form').show();
	    $('#residential').addClass('active');
	    $('#commercial').removeClass('active');
	    $('#residential-form').addClass('active show');
	});
	$('#commercial').on('click', function () {
	    $('#commercial-form').show();
	    $('#residential-form').hide();
	    $('#commercial').addClass('active');
	    $('#commercial-form').addClass('active show');
	    $('#residential').removeClass('active');
	});

});

$(function () {
  $('[data-toggle="popover"]').popover()
})
