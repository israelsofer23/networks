import socket
import threading
import time
import helpers
import NotFoundException
import sys

SERVER_PORT = 3117
TIMEOUT_WAIT = 15
IP_BROADCAST = "255.255.255.255"
WAITING_TIME = 1
LOCALHOST = "127.0.0.1"
TEAM_NAME = b'The ARP poisoners!              '
DISCOVER = bytes([1])
OFFER = bytes([2])
REQUEST = bytes([3])
ACKNOWLEDGE = bytes([4])
NEGATIVE_ACKNOWLEDGE = bytes([5])


class Client:

    def __init__(self, hash_to_crack, secret_length):
        self.user_hash = hash_to_crack
        self.user_hash_length = secret_length
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.setblocking(False)

    def start_activity(self):
        self.udp_socket.sendto(TEAM_NAME + DISCOVER + (helpers.pad(40)).encode() + bytes([0]), (IP_BROADCAST, SERVER_PORT))  # TODO: Missing fields
        self.wait_for_servers()

    def wait_for_servers(self):
        time_to_end = time.time() + WAITING_TIME
        servers_addresses = []
        self.udp_socket.settimeout(WAITING_TIME)
        while time.time() <= time_to_end:
            # is_socket_ready = select.select([self.udp_socket], [], [], WAITING_TIME)[0]  # Returned lists are ready FDs for read, write and error (if I'm not mistaken)
            # if is_socket_ready:
            try:
                data, server = self.udp_socket.recvfrom(4096)
                if bytes([helpers.find_message_type(data)]) == OFFER:
                    print("got an offer message!")
                    servers_addresses.append(server)
            except socket.timeout:
                pass
        if len(servers_addresses) > 0:
            ranges = helpers.split_fairly(self.user_hash_length, len(servers_addresses))
            threads = []
            exception_counter = 0
            for index in range(len(servers_addresses)):
                threads.append(threading.Thread(target=self.talk_with_servers, args=(servers_addresses[index], ranges[index],)))
            try:
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
            except NotFoundException:
                exception_counter += 1
            if exception_counter == len(servers_addresses):
                raise NotFoundException
        else:
            print("No servers answered, exiting.")
            exit(1337)

    def talk_with_servers(self, server, search_range):
        self.udp_socket.sendto(TEAM_NAME + REQUEST + self.user_hash.encode() + bytes([self.user_hash_length]) + search_range[0].encode() + search_range[1].encode(), server)
        print("sent a request message")
        self.udp_socket.settimeout(TIMEOUT_WAIT)
        try:
            server_response, address = self.udp_socket.recvfrom(4096)
            if server_response:
                server_response = server_response.decode()
                print(server_response[74:])
                sys.exit()
            raise NotFoundException
        except socket.timeout:
            raise NotFoundException


if __name__ == "__main__":
    user_hash = input("Welcome to The ARP poisoners!. Please enter the hash: ")
    user_hash_length = int(input("Please enter the input string length: "))
    client = Client(user_hash, user_hash_length)
    client.start_activity()
