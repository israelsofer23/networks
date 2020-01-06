import socket
import threading
import time
import helpers

SERVER_PORT = 3117
TIMEOUT_WAIT = 15
IP_BROADCAST = "255.255.255.255"
WAITING_TIME = 1
LOCALHOST = "127.0.0.1"
TEAM_NAME = "this is a string with 32 chars!!"
DISCOVER = 1
OFFER = 2
REQUEST = 3
ACKNOWLEDGE = 4
NEGATIVE_ACKNOWLEDGE = 5


class Client:

    def __init__(self, user_word, word_length):
        self.user_hash = user_word
        self.user_hash_length = word_length
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def start_activity(self):
        self.udp_socket.sendto(f'{TEAM_NAME}{DISCOVER}'.encode(), (IP_BROADCAST, SERVER_PORT))
        self.wait_for_servers()

    def wait_for_servers(self):
        time_to_end = time.time() + WAITING_TIME
        servers_addresses = []
        while time.time() <= time_to_end:
            data, server = self.udp_socket.recvfrom(4096)
            if helpers.find_message_type(data) == OFFER:
                servers_addresses.append(server)
        ranges = helpers.split_fairly(self.user_hash_length, len(servers_addresses))
        threads = []
        for index in range(len(servers_addresses)):
            threads.append(threading.Thread(target=self.talk_with_servers, args=(servers_addresses[index], ranges[index],)))
        for thread in threads:
            thread.start()

    def talk_with_servers(self, server, search_range):
        self.udp_socket.sendto(f'{TEAM_NAME}{REQUEST}{self.user_hash}{self.user_hash_length}{search_range(0)}{search_range(1)}'.encode(), server)


if __name__ == "__main__":
    user_hash = input("Welcome to <your-team-name-here>. Please enter the hash: ")
    user_hash_length = input("Please enter the input string length: ")
    user_hash_length = int(user_hash_length)
    client = Client(user_hash, user_hash_length)
    client.start_activity()
