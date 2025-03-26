
function load_players(data) {
    fetch('data/players/players.json')
        .then(res => {
            return res.json();
        })
        .then(pl_index => {
            document.getElementById('cont-team_mates').innerHTML = '';
            document.getElementById('cont-opponents').innerHTML = '';
            
            data.team_mates.forEach((m_id) => {
                document.getElementById('cont-team_mates').innerHTML +=
                    `<tr><td><a href="player.html?p=${m_id}">${pl_index[m_id].name}</a></td></tr>`;
            });
            data.opponents.forEach((o_id) => {
                document.getElementById('cont-opponents').innerHTML +=
                    `<tr><td><a href="player.html?p=${o_id}">${pl_index[o_id].name}</a></td></tr>`;
            });
        });
}

function load_stats() {
    document.activeElement.blur();
    
    const url_params = new URLSearchParams(window.location.search);
    const pl_id = url_params.get('p');

    fetch(`data/players/${pl_id}.json`)
        .then(res => {
            return res.json();
        })
        .then(pl_data => {
            document.getElementById('main-name').innerHTML = pl_data.name;
            document.getElementById('main-editions').innerHTML = pl_data.editions;
            document.getElementById('main-coordinates').innerHTML =
                `(${pl_data.lat}°N, ${pl_data.long}°E)`;
            
            var ed_id = document.getElementById('ed-select').value;
            var data = pl_data.stats;

            document.getElementById('ed-select').innerHTML =
                '<option value="gen">Generali</option>';

            pl_data.stats_per_edition.forEach((ed_stats) => {
                if (ed_stats.edition_id == ed_id) data = ed_stats;
                document.getElementById('ed-select').innerHTML +=
                    `<option value="${ed_stats.edition_id}">Edizione ${ed_stats.edition_id}</option>`;
            });
            document.getElementById('ed-select').value = ed_id;

            const team = (data.teams[0] == 'N') ? 'NORD' : 'SUD';
            if (data.teams.length > 1) team = 'NORD, SUD';
            document.getElementById('main-team').innerHTML = team;
            document.getElementById('cont-team').innerHTML = team;

            const h_played = Math.floor(data.time_played / 60);
            const min_played = data.time_played % 60;
            
            document.getElementById('cont-time_played').innerHTML = 
                `${(h_played == 0) ? '' : h_played + 'h '}${min_played}min`;

            [
                'games_played',
                'self_score',
                'opp_score',
                'ko_got',
                'ko_opp'
            ].forEach((index) => {
                document.getElementById(`cont-${index}`).innerHTML = data[index];
            });
            [
                'delta',
                'delta_per_game',
                'delta_per_hour',
                'delta_per_minute'
            ].forEach((index) => {
                document.getElementById(`cont-${index}`).innerHTML =
                    (data[index] >= 0) ? `+${data[index]}` : data[index];
            });

            document.getElementById('cont-tichu').innerHTML =
                `${data.tichu_succ + data.tichu_fail} (<span class="green">` +
                `${data.tichu_succ}</span> + <span class="red">${data.tichu_fail}</span>)`;
            document.getElementById('cont-gtichu').innerHTML =
                `${data.gtichu_succ + data.gtichu_fail} (<span class="green">` +
                `${data.gtichu_succ}</span> + <span class="red">${data.gtichu_fail}</span>)`;
            
            load_players(data);

            if (document.getElementById('map-wrapper').innerHTML == '') {
                render_map('map-wrapper', 460, 7.5, [{
                    name: pl_data.name,
                    lat: pl_data.lat,
                    long: pl_data.long,
                    team: pl_data.stats.teams[0]
                }], -100);
            }
        })
        .catch(() => {
            document.getElementById('main-name').innerHTML = 'Giocatore non trovato';
            document.getElementById('tabs-wrapper').style.display = 'None';
        });
}

window.onload = () => {
    load_page();
    load_stats();
}