
document.addEventListener("DOMContentLoaded", function(){

  var scroll_hide = document.querySelector('.scroll-hide');
  var navbar = document.getElementById('navbar');

	if (scroll_hide) {
		var navbar_height = navbar.offsetHeight;
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
	};

	var navbar_collapse = document.getElementById('mobile_site_nav');

	if (navbar_collapse) {
		navbar_collapse.addEventListener('show.bs.collapse', e=>{
			navbar.classList.toggle('scrolled-top', false);
			navbar.classList.toggle('scrolled-down', false);
			navbar.classList.toggle('scrolled-up', true);
			document.body.addEventListener('click', hide_navbar_menu);
		});

		navbar_collapse.addEventListener('shown.bs.collapse', e=>{
			navbar_menu_open(true);
		});

		navbar_collapse.addEventListener('hidden.bs.collapse', e=>{
			navbar_menu_open(false);
		});
	}

});

function navbar_menu_open(toggle=false) {
	var body = document.getElementById('default');
	body.classList.toggle('navbar-expanded', toggle);
}

function hide_navbar_menu(e) {

	var navbar_collapse = document.getElementById('mobile_site_nav');
	var navbar = document.getElementById('navbar');

	if (!e.path.includes(navbar)) {
		$( navbar_collapse ).collapse('hide');
		e.target.removeEventListener('click', hide_navbar_menu);
	}
}