
    
    var fontSizeBody = 1;
    var fontSizeH1 = 1.4285;
    var fontSizeH2 = 1.1428;
    var fontSizeP = 0.9285;
    var fontSizeLabel = 0.875;
    var fontSizeDBlock= 1.36;
    
            
        function disableZoomIn(){
            var elem = document.getElementsByTagName("body")[0];
            var bodyFontSize = window.getComputedStyle(elem,null).getPropertyValue("font-size");
            if(bodyFontSize == "21.76px"){
            document.getElementById("zoomIn").setAttribute("disabled","disabled");
            }else{
                document.getElementById("zoomIn").removeAttribute("disabled");

            }

        }
        function disableZoomOut(){
            var elem = document.getElementsByTagName("body")[0];
            var bodyFontSize = window.getComputedStyle(elem,null).getPropertyValue("font-size");
            if(bodyFontSize == "16px"){
            document.getElementById("zoomOut").setAttribute("disabled","disabled");
            }else{
                document.getElementById("zoomOut").removeAttribute("disabled");

            }

        }
    

    // Funcion para aumentar la fuente

    function zoomIn() {
        fontSizeBody += 0.04;
        fontSizeH1 += 0.04;
        fontSizeH2 += 0.04;
        fontSizeP += 0.04;
        fontSizeLabel += 0.04;
        fontSizeDBlock += 0.04;
        
        for (var i=0; i<document.getElementsByTagName("body").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("body")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h1").length && fontSizeH1 >=1.4285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h1")[i].style.fontSize= fontSizeH1 + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h2").length && fontSizeH2 >=1.1428 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h2")[i].style.fontSize= fontSizeH2 + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h3").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h3")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("a").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("a")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("p").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("p")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("td").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("td")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("span").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("span")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByClassName("required").length && fontSizeLabel >=0.875 && fontSizeBody <= 1.4; i++){
            document.getElementsByClassName("required")[i].style.fontSize= fontSizeLabel + "em";
        }
        if(document.getElementById("id_password") != null){
        document.getElementById("id_password").style.fontSize = fontSizeBody + "em";
        document.getElementById("id_username").style.fontSize = fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByClassName("d-block").length && fontSizeDBlock >=1.36 && fontSizeBody <= 1.4; i++){
            document.getElementsByClassName("d-block")[i].style.fontSize= fontSizeDBlock + "em";
        }
        if(document.getElementById("password") != null){
            document.getElementById("password").style.fontSize = fontSizeBody + "em";
            document.getElementById("username").style.fontSize = fontSizeBody + "em";
            }


        disableZoomOut();
        disableZoomIn();
       



    }



    // Funcion para disminuir la fuente

    function zoomOut() {
        fontSizeBody -= 0.04;
        fontSizeH1 -= 0.04;
        fontSizeH2 -= 0.04;
        fontSizeP -= 0.04;
        fontSizeLabel -=0.04;
        fontSizeDBlock -=0.04;

        for (var i=0; i<document.getElementsByTagName("body").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("body")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h1").length && fontSizeH1 >=1.4285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h1")[i].style.fontSize= fontSizeH1 + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h2").length && fontSizeH2 >=1.1428 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h2")[i].style.fontSize= fontSizeH2 + "em";
        }
        for (var i=0; i<document.getElementsByTagName("h3").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("h3")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("a").length && fontSizeBody >=1 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("a")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("p").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("p")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("td").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("td")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByTagName("span").length && fontSizeP >=0.9285 && fontSizeBody <= 1.4; i++){
            document.getElementsByTagName("span")[i].style.fontSize= fontSizeBody + "em";
        }
        for (var i=0; i<document.getElementsByClassName("required").length && fontSizeLabel >=0.875 && fontSizeBody <= 1.4; i++){
            document.getElementsByClassName("required")[i].style.fontSize= fontSizeLabel + "em";
        }

        if(document.getElementById("id_password") != null){
            document.getElementById("id_password").style.fontSize = fontSizeBody + "em";
            document.getElementById("id_username").style.fontSize = fontSizeBody + "em";
        }

        for (var i=0; i<document.getElementsByClassName("d-block").length && fontSizeDBlock >=1.36 && fontSizeBody <= 1.4; i++){
            document.getElementsByClassName("d-block")[i].style.fontSize= fontSizeDBlock + "em";
        }
        if(document.getElementById("password") != null){
            document.getElementById("password").style.fontSize = fontSizeBody + "em";
            document.getElementById("username").style.fontSize = fontSizeBody + "em";
            }
        disableZoomIn();
        disableZoomOut();

    }
