
const start_date = new Date("Mar 8, 2025 20:00:00");
const end_date = new Date("Mar 9, 2025 20:00:00");

const sheet_id = '113mEjNx_utTE4_E01zL7NriTWGJvfpibPHpMRrbw3_8';


function adj_case(str) {
    return str.replace(
        /\w\S*/g,
        text => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase()
    );
}

function get_tichu(tichu) {
    if (tichu == undefined) return "";
    if (tichu == "T") return '(<span class="orange">T</span>)';
    if (tichu == "GT") return '(<span class="orange">GT</span>)';
    if (tichu == "T+") return '(<span class="green">T</span>)';
    if (tichu == "T-") return '(<span class="red">T</span>)';
    if (tichu == "GT+") return '(<span class="green">GT</span>)';
    if (tichu == "GT-") return '(<span class="red">GT</span>)';
}

function get_ko(ko) {
    if (ko == "KO") return '(<span class="black">KO</span>)';
    return '';
}

function parse_games_db(games_db)
{
    var prev_rounds = [];
    var cur_round = {};
	var stat = {
		tg_N: 0,
		tb_N: 0,
		tg_S: 0,
		tb_S: 0,
		gtg_N: 0,
		gtb_N: 0,
		gtg_S: 0,
		gtb_S: 0,
		ko_N: 0,
		ko_S: 0
	};

    games_db.forEach((round, idx) => {
        if (round["Mano_N"] != undefined && idx < games_db.length - 1) {
            prev_rounds.push(round);

			if (round.Tichu_N == "T+") stat.tg_N++;
			if (round.Tichu_N == "T-") stat.tb_N++;
			if (round.Tichu_S == "T+") stat.tg_S++;
			if (round.Tichu_S == "T-") stat.tb_S++;
			if (round.Tichu_N == "GT+") stat.gtg_N++;
			if (round.Tichu_N == "GT-") stat.gtb_N++;
			if (round.Tichu_S == "GT+") stat.gtg_S++;
			if (round.Tichu_S == "GT-") stat.gtb_S++;
			if (round.Punti_N == "KO") stat.ko_N++;
			if (round.Punti_S == "KO") stat.ko_S++;
			
            return;
        }
        cur_round = round;
    });

	var score_N = 0, score_S = 0;

    if (prev_rounds.length > 0) {
        score_N = prev_rounds[prev_rounds.length - 1]["Totale_N"];
        score_S = prev_rounds[prev_rounds.length - 1]["Totale_S"];
    }
	$("#cur_tot_N").html(score_N);
    $("#cur_tot_S").html(score_S);
    
    $("#cur_g1_N").html(adj_case(cur_round["NORD_G1"]));
    $("#cur_g2_N").html(adj_case(cur_round["NORD_G2"]));
    $("#cur_g1_S").html(adj_case(cur_round["SUD_G1"]));
    $("#cur_g2_S").html(adj_case(cur_round["SUD_G2"]));

    $("#cur-tichu-N").html(get_tichu(cur_round.Tichu_N));
    $("#cur-tichu-S").html(get_tichu(cur_round.Tichu_S));

    $("#games-cont").html("");

    for (var i = prev_rounds.length - 1; i >= 0; i--)
    {
        var round = prev_rounds[i];

        $("#games-cont").append(
            `<tr><td>${adj_case(round.NORD_G1)}, ${adj_case(round.NORD_G2)}</td>` +
            `<td>${round.Mano_N} ${get_tichu(round.Tichu_N)} ${get_ko(round.Punti_N)}</td>` +
            `<td>${round.Totale_N}</td><td>${round.Totale_S}</td>` +
            `<td>${round.Mano_S} ${get_tichu(round.Tichu_S)} ${get_ko(round.Punti_S)}</td>` +
            `<td>${adj_case(round.SUD_G1)}, ${adj_case(round.SUD_G2)}</td></tr>`
        );
    }

	$("#stat-t-N").html(
		`${stat.tg_N + stat.tb_N} (successo: ${(stat.tg_N /(stat.tg_N + stat.tb_N) * 100).toFixed(1)}%)`
	);
	$("#stat-t-S").html(
		`${stat.tg_S + stat.tb_S} (successo: ${(stat.tg_S /(stat.tg_S + stat.tb_S) * 100).toFixed(1)}%)`
	);
	$("#stat-gt-N").html(
		`${stat.gtg_N + stat.gtb_N} (successo: ${(stat.gtg_N /(stat.gtg_N + stat.gtb_N) * 100).toFixed(1)}%)`
	);
	$("#stat-gt-S").html(
		`${stat.gtg_S + stat.gtb_S} (successo: ${(stat.gtg_S /(stat.gtg_S + stat.gtb_S) * 100).toFixed(1)}%)`
	);
	$("#stat-ko-N").html(`${stat.ko_N}`);
	$("#stat-ko-S").html(`${stat.ko_S}`);

	const now = new Date();
	const delta_time_h = (end_date.getTime() - now.getTime()) / (1000 * 60 * 60);

	$("#stat-rimonta").html(
		`Indice di rimonta (punti in piÃ¹ all'ora che deve fare il `+
		`${(score_N > score_S) ? "SUD" : "NORD"} per recuperare il ${(score_N > score_S) ? "NORD" : "SUD"}): ` +
		`${(delta_time_h < 0.001) ? "&#8734;" : (Math.abs(score_N - score_S)/delta_time_h).toFixed(2)}`
	);
}

function parse_parts_db(parts_db) {
    $("#parts-cont").html("");

    for (var i = 0; i < parts_db.length; i++)
    {
        var part = parts_db[i];

        $("#parts-cont").append(
            `<tr><td>${((part.NORD == undefined) ? "" : (adj_case(part.NORD) + " (" + part.Lat_N + " N)"))}</td>` +
            `<td>${((part.SUD == undefined) ? "" : (adj_case(part.SUD) + " (" + part.Lat_S + " N)"))}</td></tr>`
        );
    }
}

function load_map () {
    const parts_sheet = new PublicGoogleSheetsParser(sheet_id, {sheetName: 'Partecipanti1'});
    parts_sheet.parse().then((res) => {
        if (window.screen.width < 800)
            render_map("map-wrapper", 500, 5, res, 43.7714);
        else
            render_map("map-wrapper", 650, 6, res, 43.7714);
    });
}

function parse_turns(turns_db) {
    $("#turns-cont").html("");

    for (var i = 0; i < turns_db.length; i++)
    {
        var round = turns_db[i];
        if (round.Passato == "Si") continue;

        $("#turns-cont").append(
            `<tr><td>${adj_case(round.NORD_G1)}, ${adj_case(round.NORD_G2)}</td>` +
            `<td>${round.Orario_inizio} - ${round.Orario_fine}</td><td>` +
            `${adj_case(round.SUD_G1)}, ${adj_case(round.SUD_G2)}</td></tr>`
        );
    }
}

function reload() {
    const games_sheet = new PublicGoogleSheetsParser(sheet_id, {sheetName: 'Partite'});
    games_sheet.parse().then((res) => {
        parse_games_db(res);
    });

    const turns_sheet = new PublicGoogleSheetsParser(sheet_id, {sheetName: 'Turni'});
    turns_sheet.parse().then((res) => {
        parse_turns(res);
    });

    const parts_sheet = new PublicGoogleSheetsParser(sheet_id, {sheetName: 'Partecipanti'});
    parts_sheet.parse().then((res) => {
        parse_parts_db(res);
    });
}

function switch_games() {
    $("#games-tab").show();
    $("#turns-tab").hide();
    $("#parts-tab").hide();
    $("#map-wrapper").html("");
}

function switch_turns() {
    $("#games-tab").hide();
    $("#turns-tab").show();
    $("#parts-tab").hide();
    $("#map-wrapper").html("");
}

function switch_parts() {
    $("#games-tab").hide();
    $("#turns-tab").hide();
    $("#parts-tab").show();
    load_map();
}

function update_countdown() {
    const now = new Date();

    if (start_date < now) window.location.reload();

    const distance = start_date.getTime() - now.getTime();

    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if (hours < 10) hours = "0" + hours;
    if (minutes < 10) minutes = "0" + minutes;
    if (seconds < 10) seconds = "0" + seconds;

    $("#countdown").html(`${days}:${hours}:${minutes}:${seconds}`);
}

function update_timer() {
    const now = new Date();

    if (start_date > now) window.location.reload();

    const distance = now.getTime() - start_date.getTime();

    var hours = Math.floor((distance) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if (hours < 10) hours = "0" + hours;
    if (minutes < 10) minutes = "0" + minutes;
    if (seconds < 10) seconds = "0" + seconds;

    $("#timer-cont").html(`${hours}:${minutes}:${seconds}`);
}

window.onload = () => {
    load_page();
    reload();
    setInterval(reload, 10000);

    if (start_date > new Date()) {
        switch_turns();
        $("#main-stats").hide();
        update_countdown();
        setInterval(update_countdown, 1000);
        return;
    }

    $("#countdown").hide();
    switch_games();
    update_timer();
    setInterval(update_timer, 1000);
}