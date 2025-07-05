__author__ = 'Nadav'

import socket
from tcp_by_size import PROTO
import json
import webbrowser

DEBUG = False
file_path = "answer.html"


# the injection can be at option 4 -> explorer: yossi'--, galaxy = x
# the result will show all the planets where discovered by yossi in all the galaxies.

# bcz of "habits" im keeping the debug_print although i dont use it debug printing in the client side.
# which means that in this side each log/output is important and all uses param always=True.

def debug_print(data, always=False):
    if DEBUG or always:
        print(data)


def update_planets_popularity():
    planet_name = input("--- Enter the Planet's Name> ")
    new_popularity = input("--- Enter new popularity> ")
    return json.dumps({"Query": "UPDPLT", "planet_name": planet_name, "new_popularity": new_popularity})


def send_exit():
    return json.dumps({"Query": "EXIT"})


def update_archive_info():
    explorer_to_check = input("--- Enter explorer name> ")
    galaxy_to_check = input("--- Enter galaxy's name> ")
    debug_print("Write the values to update!", True)
    explorer = input("--- Enter explorer name> ")
    date_of_publish = input("--- Enter date of publish [YYYY-MM-DD]> ")
    galaxy = input("--- Enter galaxy name> ")
    planet_name = input("--- Enter planet's name> ")
    return json.dumps({
        "Query": "UDPARH",
        "explorer_to_check": explorer_to_check, "galaxy_to_check": galaxy_to_check, "explorer": explorer,
        "date": date_of_publish, "galaxy": galaxy, "planets_name": planet_name})


def get_planets_with_e_and_a():
    return json.dumps({"Query": "GETE&A"})


def get_all_planets():
    return json.dumps({"Query": "GETPLT"})


def get_all_archive():
    return json.dumps({"Query": "GETARH"})


def get_biggest_three_planets():
    return json.dumps({"Query": "GTBIG3"})


def get_water_planets_count():
    return json.dumps({"Query": "CNTWTR"})


def get_planets_by_explorer_and_galaxy():
    name = input("--- Enter explorer's name> ")
    galaxy = input("--- Enter galaxy's name> ")
    return json.dumps({"Query": "EXPDAT", "explorer": name, "galaxy": galaxy})


def insert_new_archive_info():
    date_of_publish = input("--- Enter date of publish (YYYY-MM-DD)> ")
    galaxy = input("--- Enter galaxy name> ")
    explorer_name = input("--- Enter explorer name> ")
    planet_name = input("--- Enter planet's name> ")
    return json.dumps({"Query": "NEWARH",
                       "date": date_of_publish, "galaxy": galaxy, "explorer": explorer_name,
                       "planets_name": planet_name})


def insert_new_planet():
    planet_name = input("--- Enter planet's name> ")
    radius = input("--- Enter Radius> ")
    has_water = input("--- Has water? (Y/N)> ")
    if has_water == "Y":
        has_water = 1
    elif has_water == "N":
        has_water = 0
    else:
        has_water = "Not Good Answer"

    distance_from_earth = input("--- Enter Distance from earth [*10^6 KM]> ")
    popularity = input("--- Enter search-popularity (int)> ")
    return json.dumps({"Query": "NEWPLT", "planet_name": planet_name, "radius": radius,
                       "distance_from_earth": distance_from_earth, "has_water": has_water, "popularity": popularity})


def delete_planet():
    planet_name = input("--- Enter the planet name> ")
    return json.dumps({"Query": "DELPLT", "planet_name": planet_name})


def delete_archive_obj():
    explorer = input("--- Enter explorer name> ")
    galaxy = input("--- Enter galaxy name> ")
    return json.dumps({"Query": "DELARH", "explorer": explorer, "galaxy": galaxy})


def menu():
    debug_print("-------------------- MENU --------------------", True)
    debug_print("1. Get All Planets\n" +
                "2. Get the 3 BIGGEST Planets that has water\n" +
                "3. Get the planets have 'E' and 'A' in their name\n" +
                "4. Get the planets that where found by [Explorer_Name] in [Galaxy_name]\n" +
                "5. Get All Archive\n" +
                "6. Insert new Archive Info\n" +
                "7. Insert new Planet\n" +
                "8. Update Archive Info\n" +
                "9. Update Planet's Popularity\n" +
                "10. Delete Planet\n" +  # will delete also from archive
                "11. Delete Archive info\n" +
                "12. EXIT\n", True)

    try:
        data = int(input("Enter Num> "))
        # handle error's here was more convenient for me.
        if data not in dict_of_functions.keys():
            print("Invalid Option. Please try again.")
            return menu()

        msg_to_send = dict_of_functions[data]()
        return msg_to_send
    except Exception as e:
        print(f"Invalid Option. Make sure you choose an INTEGER within the list above. {e}")
        return menu()


def create_html(data):
    global file_path
    try:
        with (open(file_path, 'w') as file):
            st = """<!DOCTYPE html>
                <html lang="en">
                    <style>
                        body {
                            background-image: url('space_bg.jpg');
                            color: white;
                            background-repeat: no-repeat;
                            background-attachment: fixed;
                            background-size: 100% 100%;
                        }
                        .container {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            flex-direction: column;
                            height: 97vh;
                            text-align: center;
                        }
                        p {
                            font-size: 20px;
                        }
                    </style>
                
                    <head>
                        <title>Server's Answer</title>
                        <meta charset="UTF-8">
                    </head>"""
            subject, info, row_affected_msg = get_subject_info_rows(data)
            st += f"""<body>
                        <div class="container">
                            <h1><u>The Server's Answer</u></h1>
                                <p id="answer">
                                    Subject: {subject} </br></br>
                                     Info: {info} </br>
                                    {row_affected_msg}
                                </p>
                            <h2><i>project was made by Nadav Cohen.</i></h2>
                        </div>
                    </body>
                </html>"""
            file.write(st)
        file_path = 'answer.html'
        webbrowser.open(file_path)

    except Exception as e:
        debug_print(f"Error. Couldn't create the answer file. {e}", True)


def get_subject_info_rows(data):
    if data is None:
        return "None", "The server didn't return a response.", ""

    subject = data["Subject"]
    if "Rows-affected" in data.keys():
        rows = data["Rows-affected"]
        info = data["info"]
        if type(info) is list:
            info = "<br>".join([item for item in info])

        if rows > 0:
            row_affected_msg = f"</br></br>{rows} row(s) have been read / affected!"
        else:
            row_affected_msg = "</br></br><b>No rows have been read / affected!</b>"

    else:  # exit msg
        info = data["info"]
        row_affected_msg = ""

    return subject, info, row_affected_msg


dict_of_functions = {
    1: get_all_planets, 2: get_biggest_three_planets, 3: get_planets_with_e_and_a,
    4: get_planets_by_explorer_and_galaxy, 5: get_all_archive,
    6: insert_new_archive_info, 7: insert_new_planet, 8: update_archive_info,
    9: update_planets_popularity, 10: delete_planet, 11: delete_archive_obj, 12: send_exit
}


def main():
    sock = socket.socket()
    try:
        sock.connect(("127.0.0.1", 33445))
        proto = PROTO(sock)

        # for future. in this side, each log/output is important and all uses param always=True.
        # choose_debug = int(input("Use Debug Mode? [0=No, 1=Yes]> "))
        # global DEBUG
        # if choose_debug == 1:
        #     DEBUG = True
        # elif choose_debug == 0:
        #     DEBUG = False
        # else:
        #     raise ValueError("Choice must be 0 or 1.")

        while True:
            data_to_send = menu()
            proto.send_with_size(data_to_send)
            received, flag = proto.recv_by_size()  # flag used only in the server's side.
            create_html(received)

            if received is None or received is not None and "EXIT OK" in received.values():
                debug_print("Exits...", True)
                break
    except Exception as e:
        debug_print(f"An error occurred! {e}", True)

    finally:
        sock.close()


if __name__ == "__main__":
    main()
