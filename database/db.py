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
exp_ed_sp.add_argument("-t", help="The directory the files will be exported to", required=True)


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
	
	def export_player_edition(self, pl_id, edition_str, ed_id = '*'):

		is_playing_n = f"(g_player_n1 = {pl_id} OR g_player_n2 = {pl_id})"
		is_playing_s = f"(g_player_s1 = {pl_id} OR g_player_s2 = {pl_id})"
		is_playing = f"({is_playing_n} OR {is_playing_s})"

		def get_tichu_str(cont):
			return f"""SELECT COUNT(*) FROM games WHERE
					((g_player_n1 = {pl_id} AND g_tichu_n1 = '{cont}') OR
					(g_player_n2 = {pl_id} AND g_tichu_n2 = '{cont}') OR
					(g_player_s1 = {pl_id} AND g_tichu_s1 = '{cont}') OR
					(g_player_s2 = {pl_id} AND g_tichu_s2 = '{cont}'))
					AND {edition_str};
				"""
		def get_closed_str(i):
			return f"""SELECT COUNT(*) FROM games WHERE
					((g_player_n1 = {pl_id} AND g_win_n1 = {i}) OR
					(g_player_n2 = {pl_id} AND g_win_n2 = {i}) OR
					(g_player_s1 = {pl_id} AND g_win_s1 = {i}) OR
					(g_player_s2 = {pl_id} AND g_win_s2 = {i}))
					AND {edition_str};
				"""
		
		res = {
			"edition_id": ed_id,
			"games_played": self.query_db(f"SELECT COUNT(*) FROM games WHERE {is_playing} AND {edition_str};"),
			"time_played": 0,
			"tichu_succ": self.query_db(get_tichu_str('T+')),
			"tichu_fail": self.query_db(get_tichu_str('T-')),
			"gtichu_succ": self.query_db(get_tichu_str('GT+')),
			"gtichu_fail": self.query_db(get_tichu_str('GT-')),
			"self_score": self.query_db(f"""SELECT
				(SELECT COALESCE(SUM(g_tot_score_n), 0) FROM games WHERE {is_playing_n} AND {edition_str}) +
				(SELECT COALESCE(SUM(g_tot_score_s), 0) FROM games WHERE {is_playing_s} AND {edition_str});
			"""),
			"opp_score": self.query_db(f"""SELECT
				(SELECT COALESCE(SUM(g_tot_score_s), 0) FROM games WHERE {is_playing_n} AND {edition_str}) +
				(SELECT COALESCE(SUM(g_tot_score_n), 0) FROM games WHERE {is_playing_s} AND {edition_str});
			"""),
			"ko_got": self.query_db(f"""SELECT
				(SELECT COUNT(*) FROM games WHERE {is_playing_n} AND g_ko_n = TRUE AND {edition_str}) +
				(SELECT COUNT(*) FROM games WHERE {is_playing_s} AND g_ko_s = TRUE AND {edition_str})
			"""),
			"ko_opp": self.query_db(f"""SELECT
				(SELECT COUNT(*) FROM games WHERE {is_playing_n} AND g_ko_s = TRUE AND {edition_str}) +
				(SELECT COUNT(*) FROM games WHERE {is_playing_s} AND g_ko_n = TRUE AND {edition_str})
			"""),
			"closed_1": self.query_db(get_closed_str(1)),
			"closed_2": self.query_db(get_closed_str(2)),
			"closed_3": self.query_db(get_closed_str(3)),
			"closed_4": self.query_db(get_closed_str(4))
		}

		res["teams"] = []
		if self.query_db(f"SELECT COUNT(*) FROM games WHERE {is_playing_n} AND {edition_str}") > 0:
			res["teams"].append("N")
		if self.query_db(f"SELECT COUNT(*) FROM games WHERE {is_playing_s} AND {edition_str}") > 0:
			res["teams"].append("S")

		self.cursor.execute(f"SELECT g_start_time, g_end_time FROM games WHERE {is_playing} AND {edition_str};")
		times = self.cursor.fetchall()

		for interval in times:
			t_start = datetime.strptime(interval[0], "%Y-%m-%d %H:%M:%S")
			t_end = datetime.strptime(interval[1], "%Y-%m-%d %H:%M:%S")
			dist = t_end - t_start
			res["time_played"] += set_precision((dist.total_seconds() / 60), 2)

			
		res["time_played"] = set_precision(res["time_played"], 0)
		res["delta"] = res["self_score"] - res["opp_score"]
		res["delta_per_game"] = set_precision( res["delta"] / res["games_played"], 2)
		res["delta_per_hour"] = set_precision(res["delta"] / (res["time_played"] / 60), 2)
		res["delta_per_minute"] = set_precision(res["delta"] / res["time_played"], 2)

		self.cursor.execute(f"""
			SELECT DISTINCT g_player_n2 FROM games WHERE g_player_n1 = {pl_id} UNION
			SELECT DISTINCT g_player_n1 FROM games WHERE g_player_n2 = {pl_id} UNION
			SELECT DISTINCT g_player_s1 FROM games WHERE g_player_s2 = {pl_id} UNION
			SELECT DISTINCT g_player_s2 FROM games WHERE g_player_s1 = {pl_id};
		""")
		res["team_mates"] = [pl[0] for pl in self.cursor.fetchall()]

		self.cursor.execute(f"""
			SELECT DISTINCT g_player_n2 FROM games WHERE {is_playing_s} UNION
			SELECT DISTINCT g_player_n1 FROM games WHERE {is_playing_s} UNION
			SELECT DISTINCT g_player_s1 FROM games WHERE {is_playing_n} UNION
			SELECT DISTINCT g_player_s2 FROM games WHERE {is_playing_n};
		""")
		res["opponents"] = [pl[0] for pl in self.cursor.fetchall()]

		return res


	def export_players(self, dir):

		if not os.path.exists(dir):
			os.makedirs(dir)
		
		players_ids = {}
		players_data = {}
		
		self.cursor.execute("SELECT * FROM players;")
		res = self.cursor.fetchall()

		for player in res:
			is_playing_n = f"(g_player_n1 = {player[0]} OR g_player_n2 = {player[0]})"
			is_playing_s = f"(g_player_s1 = {player[0]} OR g_player_s2 = {player[0]})"
			is_playing = f"({is_playing_n} OR {is_playing_s})"

			players_ids[player[1]] = player[0]
			players_data[player[0]] = {
				"name": player[1],
				"lat": player[2],
				"long": player[3]
			}

			pl_stats = {
				"name": player[1],
				"lat": player[2],
				"long": player[3],
				"editions": self.query_db(f"SELECT COUNT(DISTINCT g_edition) FROM games WHERE {is_playing};"),
				"stats": self.export_player_edition(player[0], 'TRUE')
			}

			self.cursor.execute(f"SELECT DISTINCT g_edition FROM games WHERE {is_playing};")
			editions = self.cursor.fetchall()

			pl_stats["editions"] = len(editions)
			pl_stats["stats_per_edition"] = []

			for ed_id in editions:
				pl_stats["stats_per_edition"].append(
					self.export_player_edition(player[0], f"g_edition = {ed_id[0]}", ed_id[0])
				)

			self.json_to_file(pl_stats, f"{dir}/{player[0]}.json")

		self.json_to_file(players_ids, f"{dir}/players_ids.json")
		self.json_to_file(players_data, f"{dir}/players.json")

	def export_game_data(self, g_id):

		def get_player(role):
			return self.query_db(f"SELECT g_player_{role} FROM games WHERE g_id = {g_id};")
		
		def get_tichu(role):
			return self.query_db(f"SELECT g_tichu_{role} FROM games WHERE g_id = {g_id};")

		return {
			"player_n1": get_player("n1"),
			"player_n2": get_player("n2"),
			"player_s1": get_player("s1"),
			"player_s2": get_player("s2"),
			"tichu_n1": get_tichu("n1"),
			"tichu_n2": get_tichu("n2"),
			"tichu_s1": get_tichu("s1"),
			"tichu_s2": get_tichu("s2"),
			"ko_n": self.query_db(f"SELECT g_ko_n FROM games WHERE g_id = {g_id}"),
			"ko_s": self.query_db(f"SELECT g_ko_s FROM games WHERE g_id = {g_id}"),
			"score_n": self.query_db(f"SELECT g_score_n FROM games WHERE g_id = {g_id}"),
			"score_s": self.query_db(f"SELECT g_score_s FROM games WHERE g_id = {g_id}"),
			"tot_score_n": self.query_db(f"SELECT g_tot_score_n FROM games WHERE g_id = {g_id}"),
			"tot_score_s": self.query_db(f"SELECT g_tot_score_s FROM games WHERE g_id = {g_id}")
		}

	def export_edition_short(self, ed_id):

		def get_edition_detil(col):
			return self.query_db(f"SELECT {col} FROM editions WHERE ed_id = {ed_id};")

		return {
			"id": ed_id,
			"start_t": get_edition_detil('ed_start_time'),
			"end_t": get_edition_detil('ed_end_time'),
			"cap_n": get_edition_detil('ed_cap_n'),
			"cap_s": get_edition_detil('ed_cap_s'),
			"vcap_n": get_edition_detil('ed_vcap_n'),
			"vcap_s": get_edition_detil('ed_vcap_s'),
			"winner": get_edition_detil('ed_winner'),
			"games_played": self.query_db(f"SELECT COUNT(*) FROM games WHERE g_edition = {ed_id}"),
			"score_n": self.query_db(f"SELECT SUM(g_tot_score_n) FROM games WHERE g_edition = {ed_id}"),
			"score_s": self.query_db(f"SELECT SUM(g_tot_score_s) FROM games WHERE g_edition = {ed_id}")
		}

	def export_edition_data(self, ed_id):

		res = self.export_edition_short(ed_id)

		self.cursor.execute(f"""
			SELECT DISTINCT g_player_n1 FROM games WHERE g_edition = {ed_id} UNION
			SELECT DISTINCT g_player_n2 FROM games WHERE g_edition = {ed_id}
		""")
		res["players_n"] = [pl[0] for pl in self.cursor.fetchall()]

		self.cursor.execute(f"""
			SELECT DISTINCT g_player_s1 FROM games WHERE g_edition = {ed_id} UNION
			SELECT DISTINCT g_player_s2 FROM games WHERE g_edition = {ed_id}
		""")
		res["players_s"] = [pl[0] for pl in self.cursor.fetchall()]

		self.cursor.execute(f"SELECT g_id FROM games WHERE g_edition = {ed_id};")
		res["games"] = [self.export_game_data(game[0]) for game in self.cursor.fetchall()]

		return res

	def export_editions(self, dir):

		if not os.path.exists(dir):
			os.makedirs(dir)

		self.cursor.execute("SELECT ed_id FROM editions;")
		editions = []

		for ed in self.cursor.fetchall():
			ed_data = self.export_edition_data(ed[0])
			self.json_to_file(ed_data, f"{dir}/{ed[0]}.json")

			editions.append(self.export_edition_short(ed[0]))

		self.json_to_file(editions, f"{dir}/editions_index.json")


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
	