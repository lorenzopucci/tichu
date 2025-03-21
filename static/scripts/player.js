
function load_stats() {
    const url_params = new URLSearchParams(window.location.search);
    const pl_id = url_params.get('p');

    fetch(`data/players/${pl_id}.json`)
        .then(res => {
            return res.json();
        })
        .then(data => {
            document.getElementById('cont-name').innerHTML = data.name;
            document.getElementById('main-editions').innerHTML = data.editions;
            document.getElementById('main-coordinates').innerHTML =
                `(${data.lat}°N, ${data.long}°E)`;
            
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

            render_map('map-wrapper', 460, 7.5, [{
                name: data.name,
                lat: data.lat,
                long: data.long,
                team: data.teams[0]
            }], -100);
        });
}

window.onload = () => {
    load_page();
    load_stats();
}