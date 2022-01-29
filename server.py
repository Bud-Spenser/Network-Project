"""
A server that listens to port 5000.
"""
import socket
import time
import statistics
import typing

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(("", 50000))
    
    print("Server running...")

    # === Variables ===
    # Counts the received packets.
    packet_count: int = 0
    # This is a list of the sent requests' data. Numbers are sent.
    sequence_list: typing.List[int] = []
    # Time when the server ends.
    t_end: float = time.time() + 60

    # === Variables for statistics ===
    # Interval in which the stats are printed in seconds
    stats_interval: int = 5
    # Set up a latency list to calculate the mean of the latencies during an interval.
    latency_list: typing.List[float] = []
    # Variables for lost and interval packet measurement
    old_packet_count: int = 0
    old_packet_lost: int = 0

    # === Receive incoming packets ===
    while True:
        # End the server when due.
        if time.time() > t_end:
            print(len(sequence_list))
            exit(0)

        request, address = s.recvfrom(4096)

        # === STATS ===
        # Received message is the sequence number formatted as a byte string.
        counter: int = int.from_bytes(request, byteorder="big")

        # Add the sequence number to a sequence list
        sequence_list.append(counter)

        packet_count += 1

        # Start measuring time for the stats
        if packet_count == 1:
            start_time = time.time()

        # Latency can only be calculated if at least two frames are sent
        if packet_count > 1:
            latency_list.append(time.time() - time_last_frame)

        # Arrival time of the packet.
        time_last_frame: float = time.time()

        # Print the stats periodically.
        if time.time() > (start_time + stats_interval):
            # The amount of packets in the interval.
            interval_packets: int = packet_count - old_packet_count

            # The amount of packets from last period.
            old_packet_count: int = packet_count

            # Throughput in KiB/s
            throughput: float = round((1024 * 0.001 * interval_packets / (time.time() - start_time)), 2)

            # Calculate the mean of the packets sent within the interval.
            latency: float = statistics.mean(latency_list[-interval_packets:])

            # Lost frames
            # Last element sequence_list[] compared to packet_count
            interval_lost: int = sequence_list[-1] - packet_count - old_packet_lost
            old_packet_lost: int = sequence_list[-1] - packet_count
            
            # Lost packets during one period in percent
            lost_percent: float = round(interval_lost / interval_packets * 100, 2)

            # New start time for the real interval
            start_time: float = time.time()
            
            print("Latenz zwischen den Frames: {}s\nDatenrate: {} KiB/s\nVerlorene Frames: {}% "
                  .format(latency, throughput, lost_percent))

        # === Response ===
        # Sent what we got.
        s.sendto(str(sequence_list), address)
