from pathlib import Path

from bot.database.db import Database

current_path = Path.cwd()  # / "bot"
# path_db = current_path / "db.test.sqlite3"
path_db = current_path / "production.db.sqlite3"
db = Database(path_db)  # se esta abriendo multiples conexiones TODO:
db.connect()

path_script_db = current_path / "db....sql"
try:
    with open(path_script_db, "r", encoding="utf-8") as f:
        sql = f.read()
except FileNotFoundError:
    # LOGGER.error
    print(f"Archivo no encontrado: {path_script_db}")
if sql:
    db.exe_script(sql)

tables = {
    "chats": ["id", "type", "name"],
    "posts": ["chat_id", "telegram_post_id", "discussion_message_id"],
    "post_items": ["post_id", "title_id", "thread_post_id"],
    "genres": ["id", "name"],
    "title_genres": ["title_id", "genre_id"],
    "titles": [
        "id",
        "media_type",
        "original_title",
        "title",
        "original_language",
        "tagline",
        "release_date",
        "overview",
        "runtime",
        "vote_average",
        "vote_count",
    ],
    "domains": [
        "kind",
        "host",
        "name",
    ],
    "paths": [
        "domain_id",
        "path",
    ],
    "external_ids": [
        "title_id",
        "provider",
        "external_id",
    ],
}


class Querys:
    # db.exe(
    #             "SELECT name from pragma_table_info('voucher_settlements')",
    #         )

    #         names_columns = db.fetch_all()
    #         names_columns = [n[0] for n in names_columns]
    def parse(self, table, columns=None):
        print("TABLE:", table, "COLUMNS:", columns)
        txt = f"INSERT INTO {table} ( "

        xf = "?"
        xc = ""
        size = len(tables[table]) if columns is None else len(columns)

        if size >= 1:
            xc = "?, " * (size - 1)
        else:
            print("error")
            exit()
        # elif len(dt) == 0:
        can = xc + xf
        colums = tables[table] if columns is None else columns

        xtx = ", ".join(colums)

        txt = txt + xtx

        txt = txt + " ) VALUES ( " + can + " )"
        return txt

    def save_data(self, table, /, *data, columns=None):
        sql = self.parse(table, columns=columns)
        ty = db.exe(
            sql,
            data,
        )
        print(sql, data)
        return ty

    def save_data_2(self, table, /, *data):
        sql = self.parse("post_items", data)
        print("SQL:", sql, "DATA:", data)
        ty = db.exe(
            sql,
            ["post_id"],
        )
        # print(sql, data)
        return ty

    def get_id(self, table, colunm, _id):
        sql = f"""SELECT id FROM {table} WHERE {colunm} = {_id}"""
        print(sql)
        db.exe(sql)
        return db.fetch_one()[0]
    def get_name(self, table, colunm, _name):
        sql = f"""SELECT id FROM {table} WHERE {colunm} = '{_name}'"""
        db.exe(sql)
        return db.fetch_one()[0]

    def get_title_id(self, table, colunm, _id):
        sql = f"""SELECT title_id FROM {table} WHERE {colunm} = {_id}"""
        db.exe(sql)
        return db.fetch_one()[0]

    def update_cell(self, sql):
        db.exe(sql)
        return db.fetch_one()

    def execute_query(self, sql):
        db.exe(sql)
        return db

    def test(self):
        # db.cursor.execute("PRAGMA table_info(posts)")
        # for row in db.cursor.fetchall():
        #     print(row)
        # db.cursor.execute(
        #                 """
        #                 SELECT id, channel_chat_id, channel_message_id, title_id
        #                 FROM posts
        #                 WHERE channel_chat_id = ?
        #                 AND channel_message_id = ?
        #             """,
        #                         (-1001713666556, 361),
        #             )
        # print(db.cursor.fetchall())
        db.exe_script(
            script="""INSERT INTO links ( title_id, path_id, name, parent_id ) VALUES (1034716, 56, '', 55);
            INSERT INTO links ( title_id, path_id, name, parent_id ) VALUES (1034716, 58, '', 56);
            INSERT INTO links ( title_id, path_id, name, parent_id ) VALUES (1034716, 59, '', 56);"""
        )


        # print(db.cursor.fetchall())

    # def get_registers_for_range_date(
    #     self,
    #     year,
    #     month: str,
    #     q: int = 1,
    #     skip_fee: bool = True,
    #     count: bool = False,
    #     is_report: bool = False,
    # ) -> dict:
    #     wildcard = "COUNT(*)" if count else "*"
    #     if not count:
    #         wildcard = "COUNT(id) AS registers_count, SUM(package_count) AS packages_count, SUM(total_amount) * 0.1 AS company_commission_amount, SUM(commission_amount) AS personal_fee_amount, SUM(total_amount) AS total_amount" if is_report else "*"
    #     sql = f"SELECT {wildcard} from voucher_settlements"
    #     if q == 1:
    #         range_date = f"'2026-{month}-01' and '2026-{month}-15'"
    #     elif q == 2:
    #         range_date = f"'2026-{month}-16' and '2026-{month}-31'"
    #     elif q == 3:
    #         range_date = f"'2026-{month}-01' and '2026-{month}-31'"
    #     else:
    #         return
    #     sql = f"{sql} WHERE date BETWEEN {range_date}"
    #     if skip_fee:
    #         sql = f"{sql} AND voucher_number != 1000"

    #     db.exe(sql)
    #     dt_columns = db.fetch_all()

    #     if count:
    #         return {"voucher_settlements": dt_columns[0][0]}
    #     elif is_report:
    #         names_columns = [
    #             "registers_count",
    #             "packages_count",
    #             "company_commission_amount",
    #             "personal_fee_amount",
    #             "total_amount",
    #         ]
    #     else:
    #         db.exe(
    #             "SELECT name from pragma_table_info('voucher_settlements')",
    #         )

    #         names_columns = db.fetch_all()
    #         names_columns = [n[0] for n in names_columns]

    #     # print(dt_columns)
    #     dt: list = []
    #     if not dt_columns:
    #         return dt

    #     for _dt in dt_columns:
    #         _d = {}
    #         for i, c in enumerate(names_columns):
    #             _d[c] = _dt[i]
    #         dt.append(_d)
    #     return dt
    #     return db.fetch_all()

    # def update_cell(self, id=104, date="2026-03-01", value_pc=0, value_pp=0, value_ta=0, voucher_number=1000):
    # comentar todo o este se acrtulizara a vaores por defecto
    # db.exe(  # date
    #     f"""UPDATE voucher_settlements
    #         SET date='{date}'
    #         WHERE id={id};
    #     """
    # )
    # db.exe(  # voucher_number
    #     f"""UPDATE voucher_settlements
    #         SET voucher_number={voucher_number}
    #         WHERE id={id};
    #     """
    # )
    # db.exe(  # package_count
    #     f"""UPDATE voucher_settlements
    #         SET package_count={value_pc}
    #         WHERE id={id};
    #     """
    # )
    # db.exe(

    #     # f"""UPDATE voucher_settlements
    #     #     SET commission_amount={value}
    #     #     WHERE id={id};
    #     # """

    #     f"""UPDATE voucher_settlements
    #         SET package_price={value_pp}
    #         WHERE id={id};
    #     """
    # )
    # db.exe(

    #     f"""UPDATE voucher_settlements
    #         SET total_amount={value_ta}
    #         WHERE id={id};
    #     """
    # )
