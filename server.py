__author__ = 'Nadav'

import json
import socket
import select
import SQL_ORM
from tcp_by_size import PROTO

DEBUG = False
DB_NAME = "Database"


# the injection can be at option 4 [html_sql_client.py] -> explorer: yossi'--, galaxy = x
# the result will show all the planets where discovered by yossi in all galaxies.


def full_validate(func):
    """
    decorator to validate the parameters type/values..
    @full_validdate
    def function(...)
    sets function = full_validate(function) => wrapper
    when calling function(self, dict_msg) it does wrapper(self, dict_msg)
    """

    def wrapper(self, dict_msg):
        if not self.validate_values(**dict_msg):
            return json.dumps({
                "Subject": "ERROR - INPUT",
                "info": "A problem with the input, try again.",
                "Rows-affected": 0})
        return func(self,dict_msg)

    return wrapper

class Server:
    def __init__(self, sock, db):
        self.idx = None
        self.dict_of_id = None
        self.messages_to_send = None
        self.write_sockets = None
        self.read_sockets = None
        self.to_continue = None
        self.db = db
        global DEBUG
        self.proto = PROTO(sock, DEBUG)
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

    @staticmethod
    def debug_print(data, always=False):
        """custom printing function"""
        if DEBUG or always:
            print(data)

    def validate_values(self, **kwargs):

        dict_of_validate_functions = {
            "planet_name": self.check_str,
            "explorer_to_check": self.check_str,
            "explorer": self.check_str,
            "galaxy": self.check_str,
            "date": self.check_date,
            "popularity": self.check_int,
            "new_popularity": self.check_int,
            "distance_from_earth": self.check_distance_from_earth,
            "radius": self.check_radius,
            "has_water": self.check_has_water
        }
        for key, value in kwargs.items():
            if key == "Query":
                self.debug_print(f"validate values for query: {value}")
                continue  # in order to get to the next loop without checking the rest

            if not dict_of_validate_functions[key](value):
                return False
        return True

    @staticmethod
    def check_str(st):  # planet_name OR galaxy OR explorer
        if st is not None and len(st) == 0:
            return False
        return True

    @staticmethod
    def check_has_water(has_water):
        # water is 0 or 1
        if has_water is not None:
            try:
                has_water = int(has_water)
                return has_water == 0 or has_water == 1
            except Exception:
                return False
        return True

    @staticmethod
    def check_radius(radiues):
        # when used in distance from earth
        if radiues is not None:
            try:
                number = float(radiues)
                return number > 0
            except Exception:
                return False
        return True

    @staticmethod
    def check_distance_from_earth(distance):
        # when used in distance from earth
        if distance is not None:
            try:
                number = float(distance)
                return number >= 0
            except Exception:
                return False
        return True

    @staticmethod
    def check_int(number):
        if number is not None:
            try:
                number = int(number)
                return number >= 0
            except Exception:
                return False
        return True

    def check_date(self, date):
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
                self.debug_print(f"The client needs to check again the date_of_publish values. {e}")
                return False
        return True

    @full_validate
    def manage_update_planets_popularity(self, dict_msg):
        planet_name = dict_msg["planet_name"]
        new_popularity = dict_msg["new_popularity"]

        return self.db.update_planet_popularity(planet_name, new_popularity)

    def manage_exit(self, data):
        return json.dumps({"Subject": "EXIT OK", "info": "you are disconnected."})

    def manage_get_all_planets(self, data):
        msg = self.db.get_all_planets()
        return msg

    def manage_get_planets_with_e_and_a(self, data):
        msg = self.db.get_planets_with_e_and_a()
        return msg

    def manage_get_all_archive(self, data):
        msg = self.db.get_all_archive()
        return msg

    def manage_get_biggest_three_planets_with_water(self, data):
        msg = self.db.get_3_biggest_planets_with_water()
        return msg

    @full_validate
    def manage_get_planets_by_explorer_and_galaxy(self, dict_msg):
        explorer = dict_msg["explorer"]
        galaxy = dict_msg["galaxy"]
        msg = self.db.get_planets_by_explorer_and_galaxy(explorer,galaxy)
        return msg

    @full_validate
    def manage_insert_new_planet(self, dict_msg):
         return self.db.insert_new_planet(**dict_msg)
    @full_validate
    def manage_insert_new_archive_info(self, dict_msg):
        return self.db.insert_new_archive_obj(**dict_msg)
    @full_validate
    def manage_update_archive_info(self, dict_msg):
        return self.db.update_archive_obj(**dict_msg)

    @full_validate
    def manage_delete_archive_info(self, dict_msg):
        explorer = dict_msg["explorer"]
        galaxy = dict_msg["galaxy"]
        return self.db.delete_archive_by_explorer_and_galaxy(explorer, galaxy)

    @full_validate
    def manage_delete_planet(self, dict_msg):
        planet_name = dict_msg["planet_name"]
        return self.db.delete_planet(planet_name)

    def do_action(self, data, idx):
        """
        check what client ask and fill to send with the answer
        """
        try:
            self.debug_print(f"Got client {idx} request: {data['Query']}")
            to_send = self.dict_of_functions[data["Query"]](data)
        except Exception as e:
            to_send = json.dumps({"Subject": "ERROR!", "info": f"General Error. {e}"})
            self.debug_print(f"ERROR {e}")

        return to_send

    def run_srv(self):
        self.debug_print("after listen")
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
                self.debug_print(f"Server Error! {e}", True)

    def manage_x_list(self, x_list):
        for sock in x_list:
            self.debug_print(f"Socket error, closing client no. {self.dict_of_id[sock][0]} sock")
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
        self.debug_print(f"Client {self.idx} joined! {client_address}")
        self.dict_of_id[connection] = self.idx, PROTO(connection)  # dict saves the idx and the proto
        self.idx += 1
        self.read_sockets.append(connection)

    def handle_reading_client_sock(self, sock):
        try:
            prot = self.dict_of_id[sock][1]
            data = prot.recv_by_size()

            if data is None:
                self.handle_client_disconnected(data, prot, sock)
                return

            msg_to_send = self.do_action(data, self.dict_of_id[sock][0])
            self.messages_to_send.append((sock, msg_to_send))
            self.write_sockets.append(sock)

        except Exception as e:
            sock.close()
            self.debug_print(f"Connection closed, {e}")
            self.read_sockets.remove(sock)
            self.write_sockets.remove(sock)

    def handle_client_disconnected(self, data, prot, sock):
        prot.close()
        self.debug_print(f"Connection closed with client no. {self.dict_of_id[sock][0]}")
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
        self.debug_print(f"Closing the socket of client no. {self.dict_of_id[sock][0]}")
        self.read_sockets.remove(sock)
        del self.dict_of_id[sock]
        prot.close()


def main():
    try:
        choose_debug = int(input("Use Debug Mode? [0=No, 1=Yes]> "))
        global DEBUG
        if choose_debug == 1:
            DEBUG = True
        elif choose_debug == 0:
            DEBUG = False
        else:
            raise ValueError("Choice must be 0 or 1.")
        db = SQL_ORM.Nadav_ORM(DB_NAME, DEBUG)
        server_socket = socket.socket()
        server_socket.bind(("0.0.0.0", 33445))
        server_socket.listen(4)
        srv = Server(server_socket, db)
        srv.run_srv()
    except Exception as e:
        Server.debug_print(f"ERROR. {e}")


if __name__ == "__main__":
    main()
