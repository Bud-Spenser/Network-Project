import socket
import time

# Set up socket
s: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IP of the receiver
ip: str = input("IP-Adresse: ")

# The counter for the packets.
counter: int = 0

# Send 120 MB then stop for 0.48 seconds. Repeat 30 times.
for j in range(30):
    for k in range(120000):
        now: float = time.time()
        data: bytes = counter.to_bytes(1000, byteorder="big")
        s.sendto(data, (ip, 50000))
        counter += 1

    time.sleep(0.48)

# === Rechnung ===
# Ausbreitungsverzögerung = 35786 km / 300000 km/s = 0,12 s
# 0,24 s bis zum anderen Empfänger auf der Erde, da von Klient zu Satellit, von Satellit zum Empfänger.
# Datenrate = 500 MB/s
# Delay = 0.24 s
# Datarate-Delay-Produkt = 120 MB

# === Zusammenfassung ===
# Ich kann 120 MB auf den Kanal legen, um den Kanal effizient zu nutzen.
# Dann kommen die ersten Pakete an. Zur Überprüfung, ob alle Pakete vollständig sind, NACKs schicken.
# Nach 0,48 s sind erst alle Daten vollständig eingetroffen.
# Danach sendet nach Möglichkeit der Empfänger einen Bloom-Filter zurück mit nicht empfangegen Frames,
# um den Kanal nicht zu belasten.
