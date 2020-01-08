import math
import string
import itertools
import hashlib


ACKNOWLEDGE = bytes([4])
NEGATIVE_ACKNOWLEDGE = bytes([5])


def cycle_string(char_arr , jump_size):
    char_arr = list(reversed(char_arr))
    base_26_to_10 = sum([ ( ord(char_arr[i]) - ord('a') )*(26**i) for i in range(len(char_arr))])
    base_26_to_10 += jump_size

    res_arr = []
    while len(res_arr) != len(char_arr):
        if base_26_to_10 == 0:
            res_arr += 'a'
            continue

        res_arr += chr( (base_26_to_10%26) + ord('a') )
        base_26_to_10 = int(math.floor(base_26_to_10/26))

    return list(reversed(res_arr))


def get_word_from_char_arr(char_arr):
    output = ""
    for c in char_arr:
        output += c

    return output


def split_fairly(input_length : int, number_of_servers : int):
    from_string, to_string = [], []
    for __ in range(input_length):
        from_string += ["a"]
        to_string += ["z"]

    space_size = 26 ** input_length
    if number_of_servers != 0:
        strings_per_server = int(math.floor(space_size / number_of_servers))
    else:
        raise ValueError("No server found, exiting!")

    ranges = []

    curr_from = from_string

    for k in range(number_of_servers):
        if k == number_of_servers-1:
            curr_to = to_string
        else:
            curr_to = cycle_string(curr_from , strings_per_server-1)

        ranges += [(get_word_from_char_arr(curr_from), get_word_from_char_arr(curr_to))]
        curr_from = cycle_string(curr_to , 1)

    return ranges


def find_message_type(message):     # TODO: change type to binary value, NOT CHAR
    try:
        return message[32]
    except:
        return 5


def scan_and_compare(start_string, finish_string, hash_word):
    try:
        print(hash_word)
        print(start_string)
        print(finish_string)
        start_string = start_string.decode()
        finish_string = finish_string.decode()
        hash_word = hash_word.decode()
        hash_word = bin(int(hash_word, base=16)).lstrip('0b')
        hash_word = int(hash_word, 2)
        for item in [''.join(x) for x in itertools.product(string.ascii_lowercase, repeat=len(start_string))]:
            if start_string <= item <= finish_string:
                item_hash = hashlib.sha1(item.encode())
                string_binary_hash = bin(int(item_hash.hexdigest(), base=16)).lstrip('0b')
                if int(string_binary_hash, 2) == hash_word:
                    return item, ACKNOWLEDGE
    except:
        return "", NEGATIVE_ACKNOWLEDGE


def get_request_data(message):  # TODO: magic numbers, start_from & finish_at might always be 256 bits,
    try:
        if len(message) == 586:
            user_hash = message[33:73]
            length = message[73]
            start_from = message[74:74 + length]
            finish_at = message[330: 330+length]
        else:
            user_hash = message[33:73]
            length = message[73]
            start_from = message[74:74+length]
            finish_at = message[74+length:]
        return user_hash, length, start_from, finish_at
    except:
        return "", 0, "", ""


def pad(amount):
    return '\0' * amount


