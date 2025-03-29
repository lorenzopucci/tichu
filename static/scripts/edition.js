
function load_edition_data(pl_index) {
    const url_params = new URLSearchParams(window.location.search);
    const ed_id = url_params.get('e');

    fetch(`data/editions/${ed_id}.json`)
        .then(res => {
            return res.json();
        })
        .then(ed_data => {
            document.getElementById('cont-id').innerHTML = ed_data.id;
            [
                'cap_n',
                'cap_s',
                'vcap_n',
                'vcap_s'
            ].forEach(key => {
                document.getElementById(`cont-${key}`).innerHTML =
                    `<a href="player.html?p=${ed_data[key]}">${pl_index[ed_data[key]].name}</a>`;
            });

            if (ed_data.winner == 'N') {
                document.getElementById('cont-result').innerHTML =
                    `<strong>${ed_data.score_n} (NORD)</strong> - ${ed_data.score_s} (SUD)`;
            }
            else {
                document.getElementById('cont-result').innerHTML =
                    `${ed_data.score_n} (NORD) - <strong>${ed_data.score_s} (SUD)</strong>`;
            }

            document.getElementById('cont-games_played').innerHTML = ed_data.games_played;

            [
                'start_t',
                'end_t'
            ].forEach(key => {
                const date = new Date(ed_data[key]);

                document.getElementById(`cont-${key}`).innerHTML =
                    `${pad_zero(date.getDate())}/${pad_zero(date.getMonth() + 1)}/${date.getFullYear()}, ` +
                    `${pad_zero(date.getHours())}:${pad_zero(date.getMinutes())}`;
            });

            load_pl_table('cont-players_n', ed_data.players_n, pl_index);
            load_pl_table('cont-players_s', ed_data.players_s, pl_index);

            map_data = [];
            ['n', 's'].forEach(team => {
                ed_data[`players_${team}`].forEach(pl_id => {
                    map_data.push({
                        name: pl_index[pl_id].name,
                        lat: pl_index[pl_id].lat,
                        long: pl_index[pl_id].long,
                        team: team.toUpperCase()
                    });
                });
            });

            if (window.innerWidth < 800) {
                render_map('map-wrapper', 450, 5, map_data, 43.7714);
            }
            else {
                render_map('map-wrapper', 600, 6, map_data, 43.7714);
            }

            ed_data.games.forEach(game => {
                document.getElementById('cont-games').innerHTML += `
                    <tr>
                    <td>
                    <span class="pl-name">${get_pl_link(game.player_n1, pl_index)}${get_tichu(game.tichu_n1)}, </span>
                    <span class="pl-name">${get_pl_link(game.player_n2, pl_index)}${get_tichu(game.tichu_n2)}</span>
                    </td>
                    <td>${game.tot_score_n}${get_ko(game.ko_n)}</td>
                    <td>${game.tot_score_s}${get_ko(game.ko_s)}</td>
                    <td>
                    <span class="pl-name">${get_pl_link(game.player_s1, pl_index)}${get_tichu(game.tichu_s1)}, </span>
                    <span class="pl-name">${get_pl_link(game.player_s2, pl_index)}${get_tichu(game.tichu_s2)}</span>
                    </td>
                    </tr>`;
            });
        })
        .catch(() => {
            document.getElementById('cont-id').innerHTML = 'non trovata';
            document.getElementById('page-cont').style.display = 'none';
        });
}

function load_data() {
    fetch('data/players/players.json')
        .then(res => {
            return res.json();
        })
        .then(pl_index => {
            load_edition_data(pl_index);
        })
        .catch(() => {
            document.getElementById('cont-id').innerHTML = 'non trovata';
            document.getElementById('page-cont').style.display = 'none';
        });
}

window.onload = () => {
    load_page();
    load_data();
}