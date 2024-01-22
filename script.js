let menuVisible = false;
//Función que oculta o muestra el menu
function mostrarOcultarMenu() {
  if (menuVisible) {
    document.getElementById("nav").classList = "";
    menuVisible = false;
  } else {
    document.getElementById("nav").classList = "responsive";
    menuVisible = true;
  }
}

function seleccionar() {
  //oculto el menu una vez que selecciono una opcion
  document.getElementById("nav").classList = "";
  menuVisible = false;
}
//Funcion que aplica las animaciones de las habilidades
function efectoHabilidades() {
  var skills = document.getElementById("skills");
  var distancia_skills =
    window.innerHeight - skills.getBoundingClientRect().top;
  if (distancia_skills >= 300) {
    let habilidades = document.getElementsByClassName("progreso");
    habilidades[0].classList.add("powerbi");
    habilidades[1].classList.add("tableau");
    habilidades[2].classList.add("alteryx");
    habilidades[3].classList.add("sqlserver");
    habilidades[4].classList.add("python");
    habilidades[5].classList.add("asure");
    habilidades[6].classList.add("communication");
    habilidades[7].classList.add("teamwork");
    habilidades[8].classList.add("creativityandinnovation");
    habilidades[9].classList.add("dedication");
    habilidades[10].classList.add("continuouslearning");
    habilidades[11].classList.add("adaptability");
  }
}

//detecto el scrolling para aplicar la animacion de la barra de habilidades
window.onscroll = function () {
  efectoHabilidades();
};
