from datetime import datetime
import sqlite3
import argparse
import json
import math
import os

parser = argparse.ArgumentParser()
subp = parser.add_subparsers(dest="subcommand")

load_sp = subp.add_parser("add_edition", help="Insert a new 24h edition into the database")
load_sp.add_argument("-d", default="data.db", help="The target database file")
load_sp.add_argument("-g", help="The games json file", required=True)
load_sp.add_argument("-m", help="The metadata json file", required=True)

load_sp = subp.add_parser("add_players", help="Insert new players into the database")
load_sp.add_argument("-d", default="data.db", help="The target database file")
load_sp.add_argument("-i", help="The players json file", required=True)

exp_pl_sp = subp.add_parser("export_players", help="Export individual statistics")
exp_pl_sp.add_argument("-d", default="data.db", help="The database file")
exp_pl_sp.add_argument("-t", help="The directory the files will be exported to", required=True)

exp_ed_sp = subp.add_parser("export_editions", help="Export statistics for all editions")
exp_ed_sp.add_argument("-d", default="data.db", help="The database file")
exp_ed_sp.add_argument("-t", help="The target json file", required=True)


def set_precision(f, n):
	return math.floor(f * (10 ** n)) / (10 ** n)


class TichuDB:
	conn = None
	cursor = None
	
	def __init__(self, db_file):
		self.conn = sqlite3.connect(db_file)
		self.cursor = self.conn.cursor()

	def __del__(self):
		self.conn.close()

	def query_db(self, query):
		self.cursor.execute(query)
		return self.cursor.fetchall()[0][0]

	def json_to_file(self, cont, path):
		if not os.path.exists(path):
			os.mknod(path)

		with open(path, "w") as f:
			json.dump(cont, f)

	def get_player_id(self, name):
		self.cursor.execute(f'SELECT pl_id FROM players WHERE pl_name = "{name}"')
		res = self.cursor.fetchall()
		if (len(res) == 0):
			raise Exception(f'There is no player named "{name}" in the database.')
		else:
			return res[0][0]

	def add_players(self, input_file):
		i_file = open(input_file, "r")
		i_data = json.load(i_file)

		for player in i_data:
			self.cursor.execute(f"""
				INSERT INTO players (pl_name, pl_lat, pl_long)
				VALUES (
					"{player['name']}",
					{player['lat']},
					{player['long']}
				);
			""")
		self.conn.commit()

	def add_edition(self, meta_file, games_file):
		m_file = open(meta_file, "r")
		m_data = json.load(m_file)
		
		g_file = open(games_file, "r")
		g_data = json.load(g_file)

		self.cursor.execute(f"""
			INSERT INTO editions (
				ed_start_time,
				ed_end_time,
				ed_cap_n,
				ed_cap_s,
				ed_vcap_n,
				ed_vcap_s,
				ed_winner
			) VALUES (
				"{m_data['start_time']}",
				"{m_data['end_time']}",
				{self.get_player_id(m_data['cap_n'])},
				{self.get_player_id(m_data['cap_s'])},
				{self.get_player_id(m_data['vcap_n'])},
				{self.get_player_id(m_data['vcap_s'])},
				"{m_data['winner']}"
			);
		""")

		self.cursor.execute("SELECT ed_id FROM editions ORDER BY ed_id DESC LIMIT 1;")
		ed_id = self.cursor.fetchall()[0][0]

		for round in g_data:
			score_n = round["SCORE_N"] if ("SCORE_N" in round) else 0
			score_s = round["SCORE_S"] if ("SCORE_S" in round) else 0
	
			if (score_n == "KO"):
				score_n = 0
				score_s = 200
			if (score_s == "KO"):
				score_s = 0
				score_n = 200
			
			self.cursor.execute(f"""
				INSERT INTO games (
					g_edition,
					g_start_time,
					g_end_time,
					g_player_n1,
					g_player_n2,
					g_player_s1,
					g_player_s2,
					g_tichu_n1,
					g_tichu_n2,
					g_tichu_s1,
					g_tichu_s2,
					g_ko_n,
					g_ko_s,
					g_score_n,
					g_score_s,
					g_tot_score_n,
					g_tot_score_s
				)
				VALUES (
					{ed_id},
					"{round['T_START']}",
					"{round['T_END']}",
					{self.get_player_id(round['N1'])},
					{self.get_player_id(round['N2'])},
					{self.get_player_id(round['S1'])},
					{self.get_player_id(round['S2'])},
					"{round['T_N1'] if ('T_N1' in round) else ''}",
					"{round['T_N2'] if ('T_N2' in round) else ''}",
					"{round['T_S1'] if ('T_S1' in round) else ''}",
					"{round['T_S2'] if ('T_S2' in round) else ''}",
					{'TRUE' if ('SCORE_N' in round and round['SCORE_N'] == 'KO') else 'FALSE'},
					{'TRUE' if ('SCORE_S' in round and round['SCORE_S'] == 'KO') else 'FALSE'},
					{score_n},
					{score_s},
					{round['ROUND_N']},
					{round['ROUND_S']}
				);
			""")
			
		self.conn.commit()

	def export_players(self, dir):

		if not os.path.exists(dir):
			os.makedirs(dir)
		
		players_stats = {}
		players_ids = {}
		players_names = {}
		
		self.cursor.execute("SELECT * FROM players;")
		res = self.cursor.fetchall()

		for player in res:
			is_playing_n = f"g_player_n1 = {player[0]} OR g_player_n2 = {player[0]}"
			is_playing_s = f"g_player_s1 = {player[0]} OR g_player_s2 = {player[0]}"
			is_playing = f"{is_playing_n} OR {is_playing_s}"

			def get_tichu_str(cont):
				return f"""SELECT COUNT(*) FROM games WHERE
						(g_player_n1 = {player[0]} AND g_tichu_n1 = '{cont}') OR
						(g_player_n2 = {player[0]} AND g_tichu_n2 = '{cont}') OR
						(g_player_s1 = {player[0]} AND g_tichu_s1 = '{cont}') OR
						(g_player_s2 = {player[0]} AND g_tichu_s2 = '{cont}');
					"""
			def get_closed_str(i):
				return f"""SELECT COUNT(*) FROM games WHERE
						(g_player_n1 = {player[0]} AND g_win_n1 = {i}) OR
						(g_player_n2 = {player[0]} AND g_win_n2 = {i}) OR
						(g_player_s1 = {player[0]} AND g_win_s1 = {i}) OR
						(g_player_s2 = {player[0]} AND g_win_s2 = {i});
					"""
			
			players_ids[player[1]] = player[0]
			players_names[player[0]] = player[1]
			
			players_stats[player[0]] = {
				"name": player[1],
				"lat": player[2],
				"long": player[3],
				"editions": self.query_db(f"SELECT COUNT(DISTINCT g_edition) FROM games WHERE {is_playing};"),
				"games_played": self.query_db(f"SELECT COUNT(*) FROM games WHERE {is_playing};"),
				"time_played": 0,
				"tichu_succ": self.query_db(get_tichu_str('T+')),
				"tichu_fail": self.query_db(get_tichu_str('T-')),
				"gtichu_succ": self.query_db(get_tichu_str('GT+')),
				"gtichu_fail": self.query_db(get_tichu_str('GT-')),
				"self_score": self.query_db(f"""SELECT
					(SELECT COALESCE(SUM(g_tot_score_n), 0) FROM games WHERE {is_playing_n}) +
					(SELECT COALESCE(SUM(g_tot_score_s), 0) FROM games WHERE {is_playing_s});
				"""),
				"opp_score": self.query_db(f"""SELECT
					(SELECT COALESCE(SUM(g_tot_score_s), 0) FROM games WHERE {is_playing_n}) +
					(SELECT COALESCE(SUM(g_tot_score_n), 0) FROM games WHERE {is_playing_s});
				"""),
				"closed_1": self.query_db(get_closed_str(1)),
				"closed_2": self.query_db(get_closed_str(2)),
				"closed_3": self.query_db(get_closed_str(3)),
				"closed_4": self.query_db(get_closed_str(4))
			}

			self.cursor.execute(f"SELECT g_start_time, g_end_time FROM games WHERE {is_playing};")
			times = self.cursor.fetchall()

			for interval in times:
				t_start = datetime.strptime(interval[0], "%Y-%m-%d %H:%M:%S")
				t_end = datetime.strptime(interval[1], "%Y-%m-%d %H:%M:%S")
				dist = t_end - t_start
				players_stats[player[0]]["time_played"] += set_precision((dist.total_seconds() / 60), 2)

				
			players_stats[player[0]]["time_played"] = set_precision(players_stats[player[0]]["time_played"], 0)
			players_stats[player[0]]["delta"] = players_stats[player[0]]["self_score"] - players_stats[player[0]]["opp_score"]
			players_stats[player[0]]["delta_per_game"] = set_precision(
				players_stats[player[0]]["delta"] / players_stats[player[0]]["games_played"],
				2
			)
			players_stats[player[0]]["delta_per_hour"] = set_precision(
				players_stats[player[0]]["delta"] / (players_stats[player[0]]["time_played"] / 60),
				2
			)
			players_stats[player[0]]["delta_per_minute"] = set_precision(
				players_stats[player[0]]["delta"] / players_stats[player[0]]["time_played"],
				2
			)

			self.json_to_file(players_stats[player[0]], f"{dir}/{player[0]}.json")

		self.json_to_file(players_ids, f"{dir}/players_ids.json")
		self.json_to_file(players_names, f"{dir}/players_names.json")

	def export_editions(self, file):

		ed_data = []

		self.cursor.execute("SELECT * FROM editions;")
		editions = self.cursor.fetchall()

		for edition in editions:
			ed_data.append({
				"id": edition[0],
				"satrt_t": edition[1],
				"end_t": edition[2],
				"cap_n": edition[3],
				"cap_s": edition[4],
				"vcap_n": edition[5],
				"vcap_s": edition[6],
				"winner": edition[7],
				"games_played": self.query_db(f"SELECT COUNT(*) FROM games WHERE g_edition = {edition[0]}"),
				"score_n": self.query_db(f"SELECT SUM(g_tot_score_n) FROM games WHERE g_edition = {edition[0]}"),
				"score_s": self.query_db(f"SELECT SUM(g_tot_score_s) FROM games WHERE g_edition = {edition[0]}")
			})

		self.json_to_file(ed_data, file)


if __name__ == "__main__":
	args = parser.parse_args()
	db = TichuDB(args.d)

	if (args.subcommand == "add_players"):
		db.add_players(args.i)

	if (args.subcommand == "add_edition"):
		db.add_edition(args.m, args.g)

	if (args.subcommand == "export_players"):
		db.export_players(args.t)

	if (args.subcommand == "export_editions"):
		db.export_editions(args.t)
	