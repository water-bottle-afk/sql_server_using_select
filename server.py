__author__ = 'Nadav'

import json
import socket
import select
import SQL_ORM
from tcp_by_size import PROTO

DEBUG = True


# the injection can be at option 4 [html_sql_client.py] -> explorer: yossi'--, galaxy = x
# the result will show all the planets where discovered by yossi in all galaxies.

def debug_print(data, always=False):
    if DEBUG or always:
        print(data)


def values_type_ok(planet_name=None, has_water=None, radius=None, distance_from_earth=None,
                   popularity=None, date=None, galaxy=None, explorer=None):
    if planet_name is not None and len(planet_name) == 0:
        return False

    if has_water is not None and not (0 <= has_water <= 1):
        return False

    if (radius is not None and
            (not (type(radius) is int or type(radius) is float)  # not int or float
             or radius < 0)):
        return False

    if (distance_from_earth is not None and
            (not (type(distance_from_earth) is int or type(distance_from_earth) is float)
             or distance_from_earth < 0)):
        return False

    if popularity is not None and (not (type(popularity) is int) or popularity < 0):
        return False

    if date is not None:
        lst = date.split('-')
        if len(lst) != 3:
            return False

        num1, num2, num3 = lst[0], lst[1], lst[2]
        if len(num1) != 4 or len(num2) != 2 or len(num3) != 2:
            return False

        try:
            num1, num2, num3 = int(num1), int(num2), int(num3)
            if num1 < 1000 or (num2 < 0 or num2 > 12) or (num3 < 0 or num3 > 31):
                return False
        except Exception as e:
            debug_print(f"The client needs to check again the date_of_publish values. {e}")
            return False

    if galaxy is not None and len(galaxy) == 0:
        return False

    if explorer is not None and len(explorer) == 0:
        return False

    return True


class Server:
    def __init__(self, sock, db):
        self.idx = None
        self.dict_of_id = None
        self.messages_to_send = None
        self.write_sockets = None
        self.read_sockets = None
        self.to_continue = None
        self.db = db
        self.proto = PROTO(sock)
        self.dict_of_functions = {
            "GETPLT": self.manage_get_all_planets,
            "GETARH": self.manage_get_all_archive,
            "GTBIG3": self.manage_get_biggest_three_planets_with_water,
            "GETE&A": self.manage_get_planets_with_e_and_a,
            "EXPDAT": self.manage_get_planets_by_explorer_and_galaxy,
            "NEWARH": self.manage_insert_new_archive_info,
            "NEWPLT": self.manage_insert_new_planet,
            "UDPARH": self.manage_update_archive_info,
            "UPDPLT": self.manage_update_planets_popularity,
            "DELPLT": self.manage_delete_planet,
            "DELARH": self.manage_delete_archive_info,
            "EXIT": self.manage_exit
        }
        self.srv_sock = sock

    def manage_update_planets_popularity(self, dict_msg):
        planet_name = dict_msg["planet_name"]
        new_popularity = dict_msg["new_popularity"]

        if values_type_ok(planet_name=planet_name, popularity=new_popularity):
            msg = self.db.update_planet_popularity(planet_name, new_popularity)
        else:
            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't updated the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        return msg

    def manage_exit(self, dict_msg):
        return json.dumps({"Subject": "EXIT OK", "info": "you are disconnected."})

    def manage_get_all_planets(self, dict_msg):
        msg = self.db.get_all_planets()
        return msg

    def manage_get_planets_with_e_and_a(self, dict_msg):
        msg = self.db.get_planets_with_e_and_a()
        return msg

    def manage_get_all_archive(self, dict_msg):
        msg = self.db.get_all_archive()
        return msg

    def manage_get_biggest_three_planets_with_water(self, dict_msg):
        msg = self.db.get_3_biggest_planets_with_water()
        return msg

    def manage_get_planets_by_explorer_and_galaxy(self, dict_msg):
        msg = self.db.get_planets_by_explorer_and_galaxy(dict_msg["explorer"], dict_msg["galaxy"])
        return msg

    def manage_insert_new_planet(self, dict_msg):
        planet_name = dict_msg["planet_name"]
        has_water = dict_msg["has_water"]
        radius = dict_msg["radius"]
        distance_from_earth = dict_msg["distance_from_earth"]
        popularity = dict_msg["popularity"]

        if not values_type_ok(planet_name, has_water, radius, distance_from_earth, popularity):
            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't updated the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        else:
            msg = self.db.insert_new_planet(**dict_msg)
        return msg

    def manage_insert_new_archive_info(self, dict_msg):
        planets_name = dict_msg["planets_name"]
        date = dict_msg["date"]
        galaxy = dict_msg["galaxy"]
        explorer = dict_msg["explorer"]

        if not values_type_ok(planets_name, date=date, galaxy=galaxy, explorer=explorer):
            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't updated the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        else:
            msg = self.db.insert_new_archive_obj(planets_name, date, galaxy, explorer)
        return msg

    def manage_update_archive_info(self, dict_msg):
        explorer_to_check = dict_msg["explorer_to_check"]
        galaxy_to_check = dict_msg["galaxy"]
        planets_name = dict_msg["planets_name"]
        date = dict_msg["date"]
        galaxy = dict_msg["galaxy"]
        explorer = dict_msg["explorer"]

        if not values_type_ok(planets_name, date=date, galaxy=galaxy, explorer=explorer) \
                or not values_type_ok(explorer=explorer_to_check, galaxy=galaxy_to_check):

            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't updated the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        else:
            msg = self.db.update_archive_obj(**dict_msg)
        return msg

    def manage_delete_archive_info(self, dict_msg):
        explorer = dict_msg["explorer"]
        galaxy = dict_msg["galaxy"]

        if not values_type_ok(explorer=explorer, galaxy=galaxy):
            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't deleted the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        else:
            msg = self.db.delete_archive_by_explorer_and_galaxy(explorer, galaxy)
        return msg

    def manage_delete_planet(self, dict_msg):
        planet_name = dict_msg["planet_name"]

        if not values_type_ok(planet_name=planet_name):
            msg = json.dumps({"Subject": "ERROR", "info": f"The server didn't deleted the database"
                                                          f". A problem with the input, try again.",
                              "Rows-affected": 0})
        else:
            msg = self.db.delete_planet(planet_name)
        return msg

    def do_action(self, data, idx):
        """
        check what client ask and fill to send with the answer
        """
        try:
            debug_print(f"Got client {idx} request: {data['Query']}")
            to_send = self.dict_of_functions[data["Query"]](data)
        except Exception as e:
            to_send = json.dumps({"Subject": "ERROR!", "info": f"General Error. {e}"})
            debug_print(f"ERROR {e}")

        return to_send

    def run_srv(self):
        debug_print("after listen")
        self.read_sockets = []
        self.write_sockets = []
        self.messages_to_send = []
        self.idx = 1
        self.dict_of_id = {}  # sock : (idx, proto_obj)
        self.to_continue = True
        while self.to_continue:
            try:
                r_list, w_list, x_list = select.select([self.srv_sock] + self.read_sockets,
                                                       self.write_sockets, self.read_sockets)
                self.manage_x_list(x_list)
                self.manage_r_list(r_list)
                self.manage_w_list(w_list)
            except Exception as e:
                debug_print(f"Server Error! {e}", True)

    def manage_x_list(self, x_list):
        for sock in x_list:
            debug_print(f"Socket error, closing {sock}")
            if sock in self.read_sockets:
                self.read_sockets.remove(sock)
            if sock in self.write_sockets:
                self.write_sockets.remove(sock)
            sock.close()

    def manage_r_list(self, r_list):
        for sock in r_list:
            if sock is self.srv_sock:
                self.handle_reading_server_sock(sock)
            else:
                self.handle_reading_client_sock(sock)

    def handle_reading_server_sock(self, sock):
        connection, client_address = sock.accept()
        debug_print(f"Client {self.idx} joined! {client_address}")
        self.dict_of_id[connection] = self.idx, PROTO(connection)  # dict saves the idx and the proto
        self.idx += 1
        self.read_sockets.append(connection)

    def handle_reading_client_sock(self, sock):
        try:
            prot = self.dict_of_id[sock][1]
            data, got_unmatched_values = prot.recv_by_size()
            if data is None:
                self.handle_client_disconnected(data, prot, sock)
            else:
                if got_unmatched_values:
                    msg_to_send = json.dumps({"Subject": "ERROR", "info": f"The server didn't deleted the "
                                                                          f"database. A problem with the input, try "
                                                                          f"again.",
                                              "Rows-affected": 0})
                else:
                    msg_to_send = self.do_action(data, self.dict_of_id[sock][0])
                self.messages_to_send.append((sock, msg_to_send))
                self.write_sockets.append(sock)

        except Exception as e:
            sock.close()
            debug_print(f"Connection closed, {e}")
            self.read_sockets.remove(sock)
            self.write_sockets.remove(sock)

    def handle_client_disconnected(self, data, prot, sock):
        prot.close()
        debug_print(f"Connection closed with client num {self.dict_of_id[sock][0]}")
        del self.dict_of_id[sock]
        if sock in self.read_sockets:
            self.read_sockets.remove(sock)
        if sock in self.write_sockets:
            self.write_sockets.remove(sock)

    def manage_w_list(self, w_list):
        for msg in self.messages_to_send:
            sock, data = msg
            if sock in w_list:
                prot = self.dict_of_id[sock][1]
                prot.send_with_size(data)
                self.messages_to_send.remove(msg)
                self.write_sockets.remove(sock)
                if "EXIT OK" in data:
                    self.manage_client_exited(sock, prot)

    def manage_client_exited(self, sock, prot):
        debug_print("Closing the socket")
        self.read_sockets.remove(sock)
        del self.dict_of_id[sock]
        prot.close()


def main():
    db = SQL_ORM.Nadav_ORM("Database", True)
    server_socket = socket.socket()
    server_socket.bind(("0.0.0.0", 33445))
    server_socket.listen(4)
    srv = Server(server_socket, db)
    srv.run_srv()


if __name__ == "__main__":
    main()

