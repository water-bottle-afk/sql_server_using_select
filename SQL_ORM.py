import json
import sqlite3

__author__ = 'Nadav'

DEBUG = True

# the injection can be at option 4 [html_sql_client.py] -> explorer: yossi'--, galaxy = x
# the result will show all the planets where discovered by yossi in all the galaxies.

# all the other queries are injection safe
planets_by_explorer_and_galaxy_injection_safe = False


class Planet(object):
    def __init__(self, name_of_planet, has_water, radius, distance_from_earth, popularity):
        self.name_of_planet = name_of_planet
        self.radius = radius
        self.distance_from_earth = distance_from_earth
        self.has_water = has_water
        self.popularity = popularity

    def __repr__(self):
        return (f"Planet: [Name:{self.name_of_planet}, Has Water:{'True' if self.has_water == 1 else 'False'}, "
                f"Radius:{self.radius}, Distance:{self.distance_from_earth}, Popularity:{self.popularity}]")


class Archive(object):
    def __init__(self, doc_id, date_of_publish, galaxy, explorer_name, planet_name):
        self.doc_id = doc_id
        self.date_of_publish = date_of_publish
        self.galaxy = galaxy
        self.explorer_name = explorer_name
        self.planet_name = planet_name

    def __repr__(self):
        return (f"Archive: [Document ID: {self.doc_id}, Date of Publish: {self.date_of_publish}, "
                f"Galaxy: {self.galaxy}, Explorer: {self.explorer_name}, Planet Name: {self.planet_name}]")


def print_all_rows(rows):
    for row in rows:
        print(row)


class Nadav_ORM:
    def __init__(self, db_name, debug):
        self.current = None
        self.conn = None  # will store the DB connection
        self.cursor = None  # will store the DB connection cursor
        self.db_name = db_name
        self.debug = debug
        self.planet_kwargs = ["name_of_planet", "has_water", "radius", "distance_from_earth", "popularity"]
        self.archive_kwargs = ["doc_id", "date_of_publish", "galaxy", "explorer_name", "planet_name"]

    def debug_print(self, data, always=False):
        if self.debug or always:
            print(data)

    def open_DB(self):
        """
        will open DB file and put value in:
        self.conn (need DB file name)
        and self.cursor
        """
        self.conn = sqlite3.connect(self.db_name)
        self.current = self.conn.cursor()

    def close_DB(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def perform_query(self, sql, injection_safe_parameters=(), enforce_foreign_key_behavior=False):
        try:
            self.open_DB()

            if enforce_foreign_key_behavior:
                enable_foreign_key_sql = "PRAGMA foreign_keys = ON"
                self.current.execute(enable_foreign_key_sql)

            res = self.current.execute(sql, injection_safe_parameters)
            self.commit()  # not needed for select but anyway

            self.debug_print(f"Query: {sql}")

            items = []
            if 'select' == sql.split()[0].lower():  # if select
                items = res.fetchall()
                rows = len(items)
                print_all_rows(items)
                self.debug_print(f"Amount of rows: {rows}")
            else:  # rows
                rows = res.rowcount
                self.debug_print(f"Amount of rows: {rows}")

            self.close_DB()
            return "", rows, items

        except Exception as e:
            return f"Error {e}", 0, []

    def get_all_planets(self):
        sql = "Select * from planets"
        error, rows, items = self.perform_query(sql)

        dict_of_values = {}
        lst_of_repr = []

        for item in items:
            for arg, val in zip(self.planet_kwargs, item):
                dict_of_values[arg] = val
            plt = Planet(**dict_of_values)
            lst_of_repr.append(plt.__repr__())

        msg = json.dumps({"Subject": "GET ALL planets", "info": lst_of_repr,
                          "Rows-affected": rows})
        if error != "":
            msg = json.dumps({"Subject": "ERROR", "info": f"error. {error}",
                              "Rows-affected": rows})
        return msg

    def get_all_archive(self):
        sql = "Select * from archive"
        error, rows, items = self.perform_query(sql)

        dict_of_values = {}
        lst_of_repr = []

        for item in items:
            for arg, val in zip(self.archive_kwargs, item):
                dict_of_values[arg] = val
            plt = Archive(**dict_of_values)
            lst_of_repr.append(plt.__repr__())

        msg = json.dumps({"Subject": "GET ALL archive objects", "info": lst_of_repr,
                          "Rows-affected": rows})
        if error != "":
            msg = json.dumps({"Subject": "ERROR", "info": f"error. {error}",
                              "Rows-affected": rows})
        return msg

    def get_3_biggest_planets_with_water(self):
        sql = "select * from planets WHERE has_water = 1 order by radius DESC limit 3"
        error, rows, items = self.perform_query(sql)

        dict_of_values = {}
        lst_of_repr = []

        for item in items:
            for arg, val in zip(self.planet_kwargs, item):
                dict_of_values[arg] = val
            plt = Planet(**dict_of_values)
            lst_of_repr.append(plt.__repr__())

        msg = json.dumps({"Subject": "Biggest Three Planets that has water", "info": lst_of_repr,
                          "Rows-affected": rows})
        if error != "":
            msg = json.dumps({"Subject": "ERROR", "info": f"error. {error}",
                              "Rows-affected": rows})
        return msg

    def get_planets_with_e_and_a(self):
        sql = "select * from planets Where name_of_planet LIKE '%E%' AND name_of_planet LIKE '%A%'"
        error, rows, items = self.perform_query(sql)

        dict_of_values = {}
        lst_of_repr = []

        for item in items:
            for arg, val in zip(self.planet_kwargs, item):
                dict_of_values[arg] = val
            plt = Planet(**dict_of_values)
            lst_of_repr.append(plt.__repr__())

        msg = json.dumps({"Subject": "All the Planets that has 'E' and 'A' in its name", "info": lst_of_repr,
                          "Rows-affected": rows})
        if error != "":
            msg = json.dumps({"Subject": "ERROR", "info": f"{error}",
                              "Rows-affected": rows})
        return msg

    def get_planets_by_explorer_and_galaxy(self, explorer, galaxy):
        if planets_by_explorer_and_galaxy_injection_safe:
            sql = ("SELECT planets.* FROM planets JOIN archive ON "
                   f"planets.name_of_planet = archive.planet_name "
                   f"WHERE archive.explorer_name=? AND archive.galaxy=?")
            error, rows, items = self.perform_query(sql, (explorer, galaxy))
        else:
            sql = ("SELECT planets.* FROM planets JOIN archive ON "
                   f"planets.name_of_planet = archive.planet_name "
                   f"WHERE archive.explorer_name ='{explorer}' AND archive.galaxy='{galaxy}'")
            error, rows, items = self.perform_query(sql)

        dict_of_values = {}
        lst_of_repr = []

        for item in items:
            for arg, val in zip(self.planet_kwargs, item):
                dict_of_values[arg] = val
            plt = Planet(**dict_of_values)
            lst_of_repr.append(plt.__repr__())

        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"{error}",
                               "Rows-affected": rows})

        if not lst_of_repr:
            return json.dumps({"Subject": "NO RESULTS!",
                               "info": "no results from the query!", "Rows-affected": rows})

        return json.dumps({"Subject": "All the planets that where discovered by the explorer in the galaxy",
                           "info": lst_of_repr, "Rows-affected": rows})

    #  _____________________________________________________________________________________________________________
    #  ______end of read start write _______________________________________________________________________________
    #  _____________________________________________________________________________________________________________

    def insert_new_planet(self, planet_name, has_water, radius, distance_from_earth, popularity, **kwargs):
        # **kwargs used of the unneeded value at the key "Query" of the dict_msg.
        # more convenient for me to pop the vars using **dict_msg in the server side

        sql = ("INSERT INTO planets (name_of_planet, has_water, radius, distance_from_earth, popularity) "
               "VALUES (?, ?, ?, ?, ?)")
        error, rows, items = (self.perform_query
                              (sql, (planet_name, has_water, radius, distance_from_earth, popularity)))

        if rows == 1 and error == "":
            msg = json.dumps({"Subject": "Updated", "info": "The server updated the database.",
                              "Rows-affected": rows})
        else:
            msg = json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                          f" The server didn't updated the database. {error}",
                              "Rows-affected": rows})
        return msg

    def insert_new_archive_obj(self, planets_name, date, galaxy, explorer):
        sql = ("INSERT INTO archive (date_of_publish, galaxy, explorer_name, planet_name) "
               "VALUES (?, ?, ?, ?)")
        error, rows, items = (self.perform_query
                              (sql, (date, galaxy, explorer, planets_name), True))

        if rows == 1 and error == "":
            msg = json.dumps({"Subject": "Updated", "info": "The server updated the database.",
                              "Rows-affected": rows})
        else:
            msg = json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                          f" The server didn't updated the database. {error}",
                              "Rows-affected": rows})
        return msg

    def update_planet_popularity(self, planet_name, new_popularity):
        sql = f"UPDATE planets SET popularity = ? WHERE name_of_planet = ?"
        error, rows, items = self.perform_query(sql, (new_popularity, planet_name))

        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"{error}",
                               "Rows-affected": rows})
        if rows == 0:
            return json.dumps({"Subject": "NO RESULTS!", "info": f"Unsuccessful try."
                                                                 f" The server didn't updated the database.",
                               "Rows-affected": rows})
        return json.dumps({"Subject": "Updated", "info": "The server updated the database.",
                           "Rows-affected": rows})

    def update_archive_obj(self, explorer_to_check, galaxy_to_check, explorer, date, galaxy, planets_name, **kwargs):
        # **kwargs used of the unneeded value at the key "Query" of the dict_msg.
        # more convenient for me to pop the vars using **dict_msg in the server side

        sql = ("Update archive SET date_of_publish=?, galaxy=?, explorer_name=?, planet_name=? "
               "WHERE explorer_name=? AND galaxy=?")
        error, rows, items = (self.perform_query(sql, (date, galaxy, explorer, planets_name,
                                                       explorer_to_check, galaxy_to_check), True))

        if rows >= 1 and error == "":
            return json.dumps({"Subject": "Updated", "info": "The server updated the database.",
                               "Rows-affected": rows})
        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                           f" The server didn't updated the database. {error}",
                               "Rows-affected": rows})
        return json.dumps({"Subject": "NO RESULTS!", "info": f"Unsuccessful try."
                                                             f" The server didn't updated the database.",
                           "Rows-affected": rows})

    def delete_archive_by_explorer_and_galaxy(self, explorer, galaxy):
        sql = "DELETE from archive where explorer_name = ? AND galaxy = ?"
        error, rows, items = self.perform_query(sql, (explorer, galaxy))

        if rows > 0 and error == "":
            return json.dumps({"Subject": "Deleted", "info": "The server deleted from the database.",
                               "Rows-affected": rows})
        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                           f" The server didn't delete from the database. {error}",
                               "Rows-affected": rows})

        return json.dumps({"Subject": "NO RESULTS!", "info": f"Unsuccessful try."
                                                             f" The server didn't delete from the database.",
                           "Rows-affected": rows})

    def delete_planet(self, planet_name):
        # deleting from the archive too.
        sql = "DELETE from archive where planet_name = ?"
        error, rows, items = self.perform_query(sql, (planet_name,))
        print(rows)
        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                           f" The server didn't update the database. {error}",
                               "Rows-affected": rows})

        sql = "DELETE from planets where name_of_planet = ?"
        error, rows, items = self.perform_query(sql, (planet_name,))

        if rows == 1 and error == "":
            return json.dumps({"Subject": "Deleted", "info": "The server deleted from the database.",
                               "Rows-affected": rows})
        if error != "":
            return json.dumps({"Subject": "ERROR", "info": f"Unsuccessful try."
                                                           f" The server didn't delete from the database.",
                               "Rows-affected": rows})

        return json.dumps({"Subject": "NO RESULTS!", "info": f"Unsuccessful try."
                                                             f" The server didn't delete from the database.",
                           "Rows-affected": rows})


def main_test():
    db = Nadav_ORM("Database", DEBUG)
    x = db.insert_new_archive_obj("Earth", 3, 4, 5)
    print(x)


if __name__ == "__main__":
    main_test()
