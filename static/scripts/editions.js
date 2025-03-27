
function load_editions(pl_index) {
    fetch('data/editions/editions_index.json')
        .then(res => {
            return res.json();
        })
        .then(data => {
            data.reverse();

            data.forEach(edition => {
                const start_t = new Date(edition.start_t);
                const end_t = new Date(edition.end_t);

                var res = `<strong>${edition.score_n} (NORD)</strong> - 
                    ${edition.score_s} (SUD)`;

                if (edition.winner == "S") {
                    res = `${edition.score_n} (NORD) - 
                        <strong>${edition.score_s} (SUD)</strong>`;
                }

                document.getElementById('page-cont').innerHTML += `
                    <div class="ed-wrapper">
                        <a class="no-ul" href="edition.html?e=${edition.id}">
                        <h2>Edizione ${edition.id}</h2>
                        </a>
                        <div class="ed-stats">
                        Data: ${pad_zero(start_t.getDate())}/${pad_zero(start_t.getMonth())}/${start_t.getFullYear()} -
                        ${pad_zero(end_t.getDate())}/${pad_zero(end_t.getMonth())}/${end_t.getFullYear()}
                        <br>
                        Capitani: ${get_pl_link(edition.cap_n, pl_index)} (NORD), 
                            ${get_pl_link(edition.cap_s, pl_index)} (SUD)
                        <br>
                        Vicecapitani: ${get_pl_link(edition.vcap_n, pl_index)} (NORD), 
                            ${get_pl_link(edition.vcap_s, pl_index)} (SUD)
                        <br>
                        Risultato: ${res}
                        </div>
                    </div>
                `;
            });
        });
}


function load_data() {
    fetch('data/players/players.json')
        .then(res => {
            return res.json();
        })
        .then(pl_index => {
            load_editions(pl_index);
        });
}

window.onload = () => {
    load_page();
    load_data();
}