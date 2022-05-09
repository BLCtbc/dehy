$(document).ready(function() {
	window.addEventListener("scroll", function() {
	  var elementTarget = document.querySelector(".faq-page-inner");
	  var href = '/faq/';

	  if (window.scrollY > elementTarget.offsetHeight) {
		  href = '/contact/';
	  }
	  document.querySelector(`nav a.nav-link[href='${href}']`).classList.toggle('active', true);
	  document.querySelectorAll(`nav a.nav-link.active:not([href='${href}'])`).forEach(elem=>{
		  elem.classList.toggle('active', false);
	  });
	});
});

