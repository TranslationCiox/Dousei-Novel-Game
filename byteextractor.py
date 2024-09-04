import codecs
import os
import re


##### Notes:
# \x01 seems to be a new line.
# \x02 wipes the textbox
# \x03 maybe, if the next character is 5c "\" and after that 72 "r" it might be one of the random wakeup dialogues.
# \x04 Seems to be related to flags and moving to other segments.
# \x05 is a clickwait, but will continue on the same line.
# \x10 male name.
# \x11 female name.
# \x12 male surname.
# \x13 female surname.
# \x15 empty nametag for the dialogue box
# \x16 end a choice.
# \x17 gives a choice.
# \x18 go to a different file (used in INIT to go to MAIN).
# \x19 go to a different file (seems to be more commonly used).
# \x20 (also written as a space " " character) loads music.
# \x28 (also written as the "(" character) load graphical things like backgrounds.
# \x1a Seems to indicate an end of a segment in the script.
# \x1d female nametag.
# \x1e male nametag.
# \x2e (also written as a period ".") seems to be used before GIF sequences. After this you can use
# 01 for pachinko, 02 for the cafe, 03 for the store, 04 for manual labor, 05 is the book store,
# 06 is the video store, 07 is the idol show, 08 for the amusement park, 09 bakery.
# \xff end a file.
patterns = [
    {
        "pattern": ["b'\\x01'"],
        #
        "action": "[01]NEWLINE\n"
    },
    {
        "pattern": ["b'\\x02'"],
        #
        "action": "[02]CLEAR_TEXTBOX\n"
    },
    {
        "pattern": ["b'\\x04'"],
        #
        "action": "[04]MOVE_TO_OTHER_SEGMENT\n"
    },
    {
        "pattern": ["b'\\x05'"],
        #
        "action": "[05]CLICKWAIT\n"
    },
    {
        "pattern": ["b'\\x10'"],
        #
        "action": "[10]MALE_NAME\n"
    },
    {
        "pattern": ["b'\\x11'"],
        #
        "action": "[11]FEMALE_NAME\n"
    },
    {
        "pattern": ["b'\\x12'"],
        #
        "action": "[12]MALE_SURNAME\n"
    },
    {
        "pattern": ["b'\\x13'"],
        #
        "action": "[13]FEMALE_SURNAME\n"
    },
    {
        "pattern": ["b'\\x15'"],
        #
        "action": "[15]NO_NAMETAG\n"
    },
    {
        "pattern": ["b'\\x16'"],
        #
        "action": "[16]END_CHOICE\n"
    },
    {
        "pattern": ["b'\\x17'"],
        #
        "action": "[17]CHOICE\n"
    },
    {
        "pattern": ["b'\\x19'"],
        #
        "action": "[19]GOTO_FILE\n"
    },
    {
        "pattern": ["b' '"],
        #
        "action": "[20]LOAD_MUSIC\n"
    },
    {
        "pattern": ["b'('"],
        #
        "action": "[28]LOAD_GRAPHICS\n"
    },
    {
        "pattern": ["b'\\x1a'"],
        #
        "action": "[1a]END_OF_SEGMENT\n"
    },
    {
        "pattern": ["b'\\x1d'"],
        #
        "action": "[1d]FEMALE_NAMETAG\n"
    },
    {
        "pattern": ["b'\\x1e'"],
        #
        "action": "[1e]MALE_NAMETAG\n"
    },
    {
        "pattern": ["b'\\xff'"],
        #
        "action": "[ff]END_FILE"
    },
]

def contains_japanese(text):
    # Regular expression pattern for Japanese characters
    pattern = re.compile(
        '['
        '\u3040-\u309F'  # Hiragana
        '\u30A0-\u30FF'  # Katakana
        '\u4E00-\u9FFF'  # Kanji
        '\uFF00-\uFF64'  # Full-width characters (excluding half-width katakana range)
        '\uFF65-\uFF9F'  # Half-width katakana
        '\uFF00-\uFFEF'  # Full-width characters, including punctuation
        '\u3000-\u303F'  # CJK Symbols and Punctuation
        ']+'
    )
    return bool(pattern.search(text))

def decode_shift_jis_with_binary(data):
    def is_shift_jis_byte(byte):
        # Shift JIS: 0x81-0x9F, 0xE0-0xEF are first byte ranges of multi-byte characters
        return (0x81 <= byte <= 0x9F) or (0xE0 <= byte <= 0xEF)

    decoded_parts = []
    i = 0
    while i < len(data):
        byte = data[i]
        try:
            # If it's likely a Shift JIS byte, attempt to decode it
            if is_shift_jis_byte(byte):
                # Attempt to decode as Shift JIS
                # Find the length of the sequence (1 or 2 bytes)
                if (i + 1 < len(data)) and (
                        (0xA1 <= data[i + 1] <= 0xDF) or (0x40 <= data[i + 1] <= 0x7E) or (0x80 <= data[i + 1] <= 0xFC)):
                    segment = data[i:i + 2]
                    i += 2
                else:
                    segment = bytes([byte])
                    i += 1

                decoded_text = segment.decode("shift_jis")
                decoded_parts.append(decoded_text.encode("shift_jis"))
            else:
                # Otherwise, treat it as binary data
                decoded_parts.append(data[i:i + 1])
                i += 1
        except (UnicodeDecodeError, IndexError):
            # Handle errors gracefully, treat as binary
            decoded_parts.append(data[i:i + 1])
            i += 1

    # After processing, merge back into a single bytes object
    return decoded_parts

def parse_bytecode(data):
    list_bytecodes = []

    byte_list = [data[i:i+1] for i in range(len(data))]
    byte_counter = 0
    for byte in byte_list:
        current_byte = str(byte[-1])
        if len(current_byte) == 7:
            list_bytecodes.append(current_byte)
            byte_counter += 1
        else:
            previous_byte = str(byte_list[byte_counter - 1][-1])
            next_byte = str(byte_list[byte_counter + 1][-1])

            if len(previous_byte) != 7 or len(next_byte) != 7:
                if len(previous_byte) != 7:
                    list_bytecodes[-1] = list_bytecodes[-1] + byte[-1].decode('shift_jis')
                    byte_counter += 1
                else:
                    list_bytecodes.append(byte[-1].decode('shift_jis'))
                    byte_counter += 1
            else:
                if byte[-1] != b'\n':
                    list_bytecodes.append(byte[-1].decode('shift_jis'))
                else:
                    list_bytecodes.append("\\x0a")
                byte_counter += 1

    return list_bytecodes

def match_pattern(line_segment, pattern):
    """Matches a line segment with a pattern, allowing wildcards."""
    if len(line_segment) != len(pattern):
        return False

    for i in range(len(pattern)):
        if pattern[i] is not None and line_segment[i] != pattern[i]:
            return False

    return True

# Function to process and save extracted text
def save_text(lines, output_path):
    with open(output_path, "w") as f:
        line_counter = 0
        while line_counter < len(lines):
            line = lines[line_counter]
            if contains_japanese(line):
                f.write(line + "\n")
            else:
                matched = False
                for pattern in patterns:
                    pattern_length = len(pattern["pattern"])
                    if match_pattern(lines[line_counter:line_counter + pattern_length], pattern["pattern"]):
                        f.write(pattern["action"])
                        line_counter += pattern_length - 1  # Skip the matched pattern length minus one since we'll increment after the match
                        matched = True
                        break

                if not matched:
                    if str(line)[0] == "b":
                        f.write(str(line)[2:-1] + "\n")
                    else:
                        f.write(str(line) + "\n")

            line_counter += 1


# Main processing loop
def process_files(input_dir="scripts"):

    counter = 0
    for fs in os.listdir(input_dir):
        if not fs.endswith(".SNX"):
            continue

        with open(os.path.join(input_dir, fs), "rb") as f:
            data = f.read()

        pure_bytes = [data[i:i + 1] for i in range(len(data))]
        data = decode_shift_jis_with_binary(data)
        list_bytes = parse_bytecode(data)
        if list_bytes:
            output_dir = input_dir + "_decoded"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, fs.replace(".SNX", "_decoded.txt"))
            save_text(list_bytes, output_path)

            output_dir = input_dir + "_bytes"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, fs.replace(".SNX", "_bytes.txt"))
            with open(output_path, "w") as f:
                for i in pure_bytes:
                    f.write(str(i)[2:-1] + "\n")

        counter += 1


# Run the processing function
process_files(input_dir="script")

