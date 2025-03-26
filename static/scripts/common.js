
function load_page() {
    fetch("partials/header.html")
        .then(res => {
            return res.text();
        })
        .then(html => {
            document.getElementById("header").innerHTML = html;
        });
}

function get_tichu(tichu) {
    if (tichu == undefined || tichu == '') return '';
    if (tichu == 'T') return ' (<span class="orange">T</span>)';
    if (tichu == 'GT') return ' (<span class="orange">GT</span>)';
    if (tichu == 'T+') return ' (<span class="green">T</span>)';
    if (tichu == 'T-') return ' (<span class="red">T</span>)';
    if (tichu == 'GT+') return ' (<span class="green">GT</span>)';
    if (tichu == 'GT-') return ' (<span class="red">GT</span>)';
}

function get_ko(ko) {
    if (ko == 'KO' || ko == 1) return ' (<span class="black">KO</span>)';
    return '';
}

function load_pl_table(id, players, pl_index) {
    document.getElementById(id).innerHTML = '';

    players.forEach(pl_id => {
        document.getElementById(id).innerHTML +=
            `<tr><td><a href="player.html?p=${pl_id}">${pl_index[pl_id].name}</a></td></tr>`;
    });
}

function pad_zero(n) {
    return (n < 10) ? "0" + n : n;
}