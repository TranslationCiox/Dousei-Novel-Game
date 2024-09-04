import os
import re

# THIS SCRIPT IS BROKEN

patterns = [
    {"pattern": b'\x01', "action": b"[01]NEWLINE\n"},
    {"pattern": b'\x02', "action": b"[02]CLEAR_TEXTBOX\n"},
    {"pattern": b'\x04', "action": b"[04]MOVE_TO_OTHER_SEGMENT\n"},
    {"pattern": b'\x05', "action": b"[05]CLICKWAIT\n"},
    {"pattern": b'\x10', "action": b"[10]MALE_NAME\n"},
    {"pattern": b'\x11', "action": b"[11]FEMALE_NAME\n"},
    {"pattern": b'\x12', "action": b"[12]MALE_SURNAME\n"},
    {"pattern": b'\x13', "action": b"[13]FEMALE_SURNAME\n"},
    {"pattern": b'\x15', "action": b"[15]NO_NAMETAG\n"},
    {"pattern": b'\x16', "action": b"[16]END_CHOICE\n"},
    {"pattern": b'\x17', "action": b"[17]CHOICE\n"},
    {"pattern": b'\x19', "action": b"[19]GOTO_FILE\n"},
    {"pattern": b' ', "action": b"[20]LOAD_MUSIC\n"},
    {"pattern": b'(', "action": b"[28]LOAD_GRAPHICS\n"},
    {"pattern": b'\x1a', "action": b"[1a]END_OF_SEGMENT\n"},
    {"pattern": b'\x1d', "action": b"[1d]FEMALE_NAMETAG\n"},
    {"pattern": b'\x1e', "action": b"[1e]MALE_NAMETAG\n"},
    {"pattern": b'\xff', "action": b"[ff]END_FILE"}
]

def replace_tags_with_bytes(data):
    # Convert binary data to a string for pattern replacement
    data_str = data.decode('latin1')  # Use 'latin1' to keep byte values in their original form
    for pattern in patterns:
        action_tag = pattern['action'].decode('latin1')  # Decode action tag
        hex_value = pattern['pattern']  # This is already in bytes
        # Replace the action tag with the byte value
        data_str = data_str.replace(action_tag, hex_value.decode('latin1'))
    # Convert string back to bytes
    return data_str.encode('latin1')


def hex_to_bytes(data):
    # Convert binary data to a string for hex replacement
    data_str = data.decode('latin1')
    hex_pattern = re.compile(r'\\x([0-9a-fA-F]{2})')
    def replace_match(match):
        return bytes.fromhex(match.group(1)).decode('latin1')
    data_str = hex_pattern.sub(replace_match, data_str)
    # Convert string back to bytes
    return data_str.encode('latin1')


def process_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for fs in os.listdir(input_dir):
        if not fs.endswith("_decoded.txt"):
            continue

        with open(os.path.join(input_dir, fs), "rb") as f:  # Read as text with appropriate encoding
            data = f.read()

        # Replace text tags with corresponding byte values
        data = replace_tags_with_bytes(data)

        # Handle remaining hex strings like \x00
        data = hex_to_bytes(data)

        # Write the output as a binary file
        output_path = os.path.join(output_dir, fs.replace("_decoded.txt", ".SNX"))
        with open(output_path, "wb") as f:
            f.write(data)  # Encode and write as binary data


# Run the processing function
process_files("script_decoded", "script_new")
