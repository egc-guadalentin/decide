	


	function popupMostrar(){
		if(document.getElementById("btn-abrir-popup")!=null){
			var btnAbrirPopup = document.getElementById("btn-abrir-popup");
			var overlay = document.getElementById("overlay");
			var popup = document.getElementById("popup");
			overlay.classList.add("active");
			popup.classList.add("active");
		}
		
	}

	function popQuitar(){
		if(document.getElementById("btn-cerrar-popup")!= null){
			var btnCerrarPopup = document.getElementById("btn-cerrar-popup");
			var overlay = document.getElementById("overlay");
			var popup = document.getElementById("popup");
			overlay.classList.remove("active");
			popup.classList.remove("active");
			
		}
	}
	

	
	

