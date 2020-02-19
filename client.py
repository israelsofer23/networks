import socket
import threading
import time
import select
import helpers

SERVER_PORT = 3117
TIMEOUT_WAIT = 15
IP_BROADCAST = "255.255.255.255"
WAITING_TIME = 1
LOCALHOST = "127.0.0.1"
TEAM_NAME = "This is a string with 32 chars!!"
DISCOVER = 1
OFFER = 2
REQUEST = 3
ACKNOWLEDGE = 4
NEGATIVE_ACKNOWLEDGE = 5


class Client:

    def __init__(self, hash_to_crack, secret_length):
        self.user_hash = hash_to_crack
        self.user_hash_length = secret_length
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setblocking(False)

    def start_activity(self):
        self.udp_socket.sendto(f'{TEAM_NAME}{DISCOVER}'.encode(), (IP_BROADCAST, SERVER_PORT))
        self.wait_for_servers()

    def wait_for_servers(self):
        time_to_end = time.time() + WAITING_TIME
        servers_addresses = []
        while time.time() <= time_to_end:
            is_socket_ready = select.select([self.udp_socket], [], [], WAITING_TIME)[0]  # Returned lists are ready FDs for read, write and error (if I'm not mistaken)
            if is_socket_ready:
                data, server = self.udp_socket.recvfrom(4096)
                if helpers.find_message_type(data) == OFFER:
                    servers_addresses.append(server)
        if (len(servers_addresses) > 0):
            ranges = helpers.split_fairly(self.user_hash_length, len(servers_addresses))
            threads = []
            for index in range(len(servers_addresses)):
                threads.append(threading.Thread(target=self.talk_with_servers, args=(servers_addresses[index], ranges[index],)))
            for thread in threads:
                thread.start()
        else:
            print("No servers answered, exiting.")
            exit(1337)

    def talk_with_servers(self, server, search_range):
        self.udp_socket.sendto(f'{TEAM_NAME}{REQUEST}{self.user_hash}{self.user_hash_length}{search_range[0]}{search_range[1]}'.encode(), server)


if __name__ == "__main__":
    user_hash = "b44ed609de1619890c9397da58c224c24e0a7d3c"#input("Welcome to <your-team-name-here>. Please enter the hash: ")
    user_hash_length = 5#int(input("Please enter the input string length: "))
    client = Client(user_hash, user_hash_length)
    client.start_activity()
