
function load_page() {
    fetch("partials/header.html")
        .then(res => {
            return res.text();
        })
        .then(html => {
            document.getElementById("header").innerHTML = html;
        });
}