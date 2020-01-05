import socket
import threading
import time
import helpers


PORT = 3117
TIMEOUT_RUN = 10
IP_BROADCAST = "255.255.255.255"
IP_ADDRESS = "0.0.0.0"
TEAM_NAME = "this is a string with 32 chars!!"
DISCOVER = 1
OFFER = 2
REQUEST = 3
ACKNOWLEDGE = 4
NEGATIVE_ACKNOWLEDGE = 5

class Server:

    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((IP_ADDRESS, PORT))

    # i will have a tread that is doing this function
    def offer(self):
        while True:
            data, client_address = self.udp_socket.recvfrom(4096)
            if helpers.find_message_type(data) == DISCOVER:
                self.udp_socket.sendto(f'{TEAM_NAME}{OFFER}'.encode(), client_address)

    def wait_for_request(self):
        while True:
            data, client_address = self.udp_socket.recvfrom(4096)
            helpers.handle_requests(data, client_address)

    # i want to have multiple treads that are doing this function, i want a thread per user
    def handle_requests(self, data, client_address):
            if helpers.find_message_type(data) == REQUEST:
                usr_hash, length, start_from, finish_at = helpers.get_request_data(data)
                user_word, ack = helpers.scan_and_compare(start_from, finish_at, usr_hash)
                self.udp_socket.sendto(f'{TEAM_NAME}{ack}{usr_hash}{length}{user_word}'.encode(), client_address)
