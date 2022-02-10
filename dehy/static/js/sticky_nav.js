
document.addEventListener("DOMContentLoaded", function(){

  var scroll_hide = document.querySelector('.scroll-hide');
  var navbar_height = document.querySelector('#navbar').offsetHeight;

	if(scroll_hide) {
		var last_scroll_top = 0;
		window.addEventListener('scroll', function() {
		    let scroll_top = window.scrollY;
		    if(scroll_top < last_scroll_top) {
		    	scroll_hide.classList.remove('scrolled-down');
		    	scroll_hide.classList.add('scrolled-up');
				if (scroll_top < 5) {
					scroll_hide.classList.add('scrolled-top')
				}
		    } else {
		        scroll_hide.classList.remove('scrolled-up');
				scroll_hide.classList.remove('scrolled-top');
		        scroll_hide.classList.add('scrolled-down');
		    }
		    last_scroll_top = scroll_top;
		});
		}

});

