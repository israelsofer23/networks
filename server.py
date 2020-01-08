import socket
import threading
import helpers


PORT = 3117
TIMEOUT_RUN = 10
IP_BROADCAST = "255.255.255.255"
IP_ADDRESS = "0.0.0.0"
TEAM_NAME = b'The ARP poisoners!              '
DISCOVER = bytes([1])
OFFER = bytes([2])
REQUEST = bytes([3])
ACKNOWLEDGE = bytes([4])
NEGATIVE_ACKNOWLEDGE = bytes([5])


class Server:

    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((IP_ADDRESS, PORT))
        self.threads = []

    # TODO: ReDesign suggestion - Thread that listens for messages (both offer and request) and dispatches thread to handle each operation
    # i will have a tread that is doing this function
    def offer(self):
        while True:
            data, client_address = self.udp_socket.recvfrom(4096)
            message_type = helpers.find_message_type(data)
            if bytes([message_type]) == DISCOVER:
                print("got a discover message!")
                self.send_offer_message(client_address)
            elif bytes([message_type]) == REQUEST:
                self.send_request_message(data, client_address)

    def wait_for_request(self):
        while True:
            data, client_address = self.udp_socket.recvfrom(4096)
            message_type = helpers.find_message_type(data)
            if bytes([message_type]) == DISCOVER:
                print("got a discover message!")
                self.send_offer_message(client_address)
            elif bytes([message_type]) == REQUEST:
                self.send_request_message(data, client_address)

    # i want to have multiple treads that are doing this function, i want a thread per user
    def handle_requests(self, data, client_address):
            usr_hash, length, start_from, finish_at = helpers.get_request_data(data)
            user_word, ack = helpers.scan_and_compare(start_from, finish_at, usr_hash)
            message_len = len(TEAM_NAME.decode()) + 1 + len(usr_hash.decode()) + 1 + len(user_word)
            print(user_word + "ssssssssss")
            print(TEAM_NAME + ack + usr_hash + bytes([length]) + user_word.encode() + user_word.encode())
            if user_word:
                self.udp_socket.sendto(TEAM_NAME + ack + usr_hash + bytes([length]) + user_word.encode() + helpers.pad(length), client_address)
            else:
                self.udp_socket.sendto(TEAM_NAME + ack + usr_hash + bytes([0]), client_address)

    def send_offer_message(self, client_address):
        print(TEAM_NAME + OFFER + (helpers.pad(40)).encode() + bytes([0]))
        self.udp_socket.sendto(TEAM_NAME + OFFER + (helpers.pad(40)).encode() + bytes([0]), client_address)

    def send_request_message(self, data, client_address):
        print("got a request message")
        client = threading.Thread(target=self.handle_requests, args=(data, client_address,))
        self.threads.append(client)
        client.start()

if __name__ == '__main__':
    server = Server()
    offer_thread = threading.Thread(target=server.offer, args=())
    temp = threading.Thread(target=server.wait_for_request, args=())
    temp.start()
    offer_thread.start()
    server.wait_for_request()

