"""
A server that listens to port 1024. The server knows which data is expected and in which order.
Therefore, it sends suitable acknowledgements according to the HTTP status codes so that the client knows
which data needs to be resent.
"""
import socket
import time
import statistics
import typing

sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("localhost", 1024))
print("Server running...")

# === Variables ===
# Counts the received packets.
packets_amount: int = 0

# The size of all packet in one period in bits.
packets_size: int = 0

# This is a list of the sent requests' data. Numbers are sent.
sequence: typing.List[int] = []

# Latencies between two arriving packets.
latencies: typing.List[float] = []

# Interval in which the stats are printed in seconds
stats_interval: int = 5

# The start time for statistics printing which is every 5 seconds.
start_time: float = -1.0

# The time the packet before the current one arrived.
time_last_packet: float = -1.0

# The amount of packets in the previous interval.
packets_amount_previous: int = 0

# The amount of lost packets in the previous period.
packets_lost_previous: int = 0

# === Receive incoming packets ===
while True:
    # Request
    request, address = sock.recvfrom(4096)
    received_number: int = int.from_bytes(request, byteorder="big")
    sequence.append(received_number)

    if packets_amount == 0:
        start_time = time.time()

    packets_amount += 1
    packets_size += len(request)

    # Start listing the latencies at the second packet.
    if packets_amount > 1:
        latencies.append(time.time() - time_last_packet)

    # Print the stats periodically.
    if time.time() >= (start_time + stats_interval):
        # The amount of packets in the interval.
        packets_amount_current: int = packets_amount - packets_amount_previous

        # Throughput in KiB/s
        throughput: float = round((packets_amount_current / 1024 / (time.time() - start_time)), 2)

        # Calculate the mean latency of the packets sent within the interval.
        latency: float = statistics.mean(latencies[-packets_amount_current:])

        # The amount of lost packets in this period.
        interval_lost_packets: int = received_number - packets_amount - packets_lost_previous

        # Lost packets during one period in percent.
        lost_percent: float = round(interval_lost_packets / packets_amount_current * 100, 2)

        print("Latenz zwischen den Packets: {} s\nDatenrate: {} KiB/s\nVerlorene Packets: {}% "
              .format(latency, throughput, lost_percent))

        # Set some variables.
        start_time: float = time.time()
        packets_lost_previous: int = interval_lost_packets

    # === Response ===
    sock.sendto(str("200").encode(), address)

    # TODO What if last number does not arrive?
    # Sent what is missing.
    if received_number == 119999:
        missing: typing.List[int] = []

        for j in range(120000):
            if j not in sequence:
                missing.append(j)

        sock.sendto(str(missing).encode(), address)

    # Set some variables.
    time_last_packet = time.time()
    packets_amount_previous: int = packets_amount

    # Reset some variables.
    packets_size = 0
