__author__ = 'Nadav'

import json

# from  tcp_by_size import send_with_size ,recv_by_size

SIZE_HEADER_FORMAT = "0000|"  # n digits for data size + one delimiter
size_header_size = len(SIZE_HEADER_FORMAT)


# The injection can be at option 4 [html_sql_client.py] -> explorer: yossi'--, galaxy = x
# The result will show all the planets where discovered by yossi in all the galaxies.


class PROTO:
    def __init__(self, sock, debug=True):
        self.sock = sock
        self.debug = debug

    def debug_print(self, data, always=False, end="\n"):
        if self.debug or always:
            print(data, end=end)

    def recv_by_size(self):  # return a json formatted data, & True if got un matched values type, False otherwise
        try:
            size_header = b''
            data_len = 0
            while len(size_header) < size_header_size:
                _s = self.sock.recv(size_header_size - len(size_header))
                if _s == b'':
                    size_header = b''
                    break
                size_header += _s
            data = b''
            if size_header != b'':
                data_len = int(size_header[:size_header_size - 1])
                while len(data) < data_len:
                    _d = self.sock.recv(data_len - len(data))
                    if _d == b'':
                        data = b''
                        break
                    data += _d

            if size_header != b'':
                msg = data.decode()
                self.debug_print(f"Recv({len(msg)}):", True, end="\t")
                self.debug_print(msg,True)

                dict_msg = json.loads(msg)

                for key, val in dict_msg.items():  # returning to the type before the json operation
                    try:
                        if key in ["has_water", "popularity", "new_popularity"]:
                            val = int(val)
                            dict_msg[key] = val
                        elif key in ["radius", "distance_from_earth"]:
                            val = float(val)
                            dict_msg[key] = val
                    except Exception as e:
                        self.debug_print(f"The client sent a wrong type of data. {e}")
                        return dict_msg, True

                return dict_msg, False

            if data_len != len(data):
                msg = ""  # Partial data is like no data !
                return json.loads(msg), False

            return None, False  # for disconnection

        except Exception as e:
            self.debug_print(f"Error occurred during receiving! {e}", True)
            return None, False

    def send_with_size(self, data):  # gets a json formatted data
        try:
            # bdata = json.dumps(data)
            len_data = len(data)
            header_data = str(len(data)).zfill(size_header_size - 1) + "|"

            bdata = header_data + data
            bdata = bdata.encode()
            self.sock.send(bdata)
            if len_data > 0:
                self.debug_print(f"Sent({len_data}):", True, end="\t")
                self.debug_print(data, True)
        except Exception as e:
            self.debug_print(f"Error occurred during sending! {e}", True)
            return None

    def close(self):
        self.sock.close()
