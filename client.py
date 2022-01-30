"""
A client that sends to port 1024. It sends starting from 0 each number up to 119 999 and expanded to 1000 bytes.
Each request expects status code 200. Otherwise, the proper body of the request is saved in a list which is
resent after all remaining data was sent.

=== Ausbreitungsverzögerung ===
35786 km / 300000 km/s = 0,12 s
0,24 s bis zum anderen Empfänger auf der Erde, da von Klient zu Satellit, von Satellit zum Empfänger.
Mit Berücksichtigung der Antworten, die geschickt werden müssen kommen, noch einmal zusätzlich 0,24 s hinzu.
In Summe 0,48 s.

=== Datarate-Delay-Produkt ===
Datenrate = 500 MB/s
Delay = 0,24 s
Datarate-Delay-Produkt = 120 MB

=== Zusammenfassung ===
Man kann 120 MB auf den Kanal legen, um den Kanal voll auszunutzen.
Nach 0,48 s sind erst alle Daten vollständig verarbeitet.
"""
import socket
import time
import typing

sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
request_body: int = 0
list_of_missing_bodies: typing.List[int] = []

# Send all data which are in sum 120 MB. Then stop for 0.48 seconds. This process is repeated 30 times.
for j in range(30):
    for k in range(120000):
        request_body_bytes: bytes = request_body.to_bytes(1000, byteorder="big")
        # s.sendto(data, ("192.168.1.12", 1024))  # todo
        sock.sendto(request_body_bytes, ("localhost", 1024))  # todo
        response, response_address = sock.recvfrom(4096)

        if response.decode("UTF-8") != "200":
            list_of_missing_bodies.append(request_body)

        request_body += 1

    # At the end of the sent 120 MB chunk, resend the missing bodies.
    for missing_body in list_of_missing_bodies:
        # sock.sendto(missing_body, ("192.168.1.12", 1024))  # todo
        sock.sendto(missing_body, ("localhost", 1024))  # todo

    time.sleep(0.48)
