let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".sidebarBtn");
let footer = document.querySelector(".sidebar-footer");
let logoName = document.querySelector(".logo_name");
let addBtn = document.querySelector(".addBtn");

let spinner = document.querySelector("#loading-spinner");

if (spinner != null) {
    spinner.style.display = "none";
}

if (addBtn != null) {
    addBtn.onclick = function() {
        spinner.style.display = "block";
    }
}

sidebarBtn.onclick = function() {
    sidebar.classList.toggle("active");
    if (sidebar.classList.contains("active")) {
        sidebarBtn.classList.replace("bx-menu", "bx-menu-alt-right");
        footer.classList.toggle("show");
        logoName.classList.toggle("show");
    } else {
        sidebarBtn.classList.replace("bx-menu-alt-right", "bx-menu");
        footer.classList.toggle("hide");
        logoName.classList.toggle("hide");
    }
};

let select = document.getElementById("site_name");
if (select != null) {
    select.removeAttribute("size");
}


function toggleSpinClass(element) {
    console.log("EVENT TRIGGERED")
    var iconElement = element.querySelector('i');

    if (iconElement.classList.contains('bx-spin')) {
        iconElement.classList.remove('bx-spin');
    } else {
        iconElement.classList.add('bx-spin');
    }
}