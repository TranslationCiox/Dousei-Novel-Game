import codecs
import os
import re


##### Notes:
# \x01 seems to be a new line.
# \x02 wipes the textbox
# \x04 Seems to be related to flags and moving to other segments.
# \x05 is a clickwait, but will continue on the same line.
# \x10 male name.
# \x11 female name.
# \x12 male surname.
# \x13 female surname.
# \x15 ???
# \x16 end a choice.
# \x17 gives a choice.
# \x18 go to a different file (used in INIT to go to MAIN).
# \x19 go to a different file (seems to be more commonly used).
# \x20 (also written as a space " " character) loads music.
# \x28 (also written as the "(" character) load graphical things like backgrounds.
# \x1a Seems to indicate an end of a segment in the script.
# \x1d female nametag.
# \x1e male nametag.
# \x2e (also written as a period ".") seems to be used before GIF sequences.
# \xff end a file.
patterns = [
    {
        "pattern": [b'\x01'],
        #
        "action": "[01]NEWLINE\n"
    },
    {
        "pattern": [b'\x02'],
        #
        "action": "[02]CLEAR_TEXTBOX\n"
    },
    {
        "pattern": [b'\x04'],
        #
        "action": "[04]MOVE_TO_OTHER_SEGMENT\n"
    },
    {
        "pattern": [b'\x05'],
        #
        "action": "[05]CLICKWAIT\n"
    },
    {
        "pattern": [b'\x10'],
        #
        "action": "[10]MALE_NAME\n"
    },
    {
        "pattern": [b'\x11'],
        #
        "action": "[11]FEMALE_NAME\n"
    },
    {
        "pattern": [b'\x12'],
        #
        "action": "[12]MALE_SURNAME\n"
    },
    {
        "pattern": [b'\x13'],
        #
        "action": "[13]FEMALE_SURNAME\n"
    },
    {
        "pattern": [b'\x15'],
        #
        "action": "[15]NO_NAMETAG\n"
    },
    {
        "pattern": [b'\x16'],
        #
        "action": "[16]END_CHOICE\n"
    },
    {
        "pattern": [b'\x17'],
        #
        "action": "[17]CHOICE\n"
    },
    {
        "pattern": [b'\x19'],
        #
        "action": "[19]GOTO_FILE\n"
    },
    {
        "pattern": [b' '],
        #
        "action": "[20]LOAD_MUSIC\n"
    },
    {
        "pattern": [b'('],
        #
        "action": "[28]LOAD_GRAPHICS\n"
    },
    {
        "pattern": [b'\x1a'],
        #
        "action": "[1a]END_OF_SEGMENT\n"
    },
    {
        "pattern": [b'\x1d'],
        #
        "action": "[1d]FEMALE_NAMETAG\n"
    },
    {
        "pattern": [b'\x1e'],
        #
        "action": "[1e]MALE_NAMETAG\n"
    },
    {
        "pattern": [b'\xff'],
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
        '\uFFA0-\uFFEF'  # Full-width characters after half-width katakana range
        ']+'
    )
    return bool(pattern.search(text))

def parse_bytecode(data):
    list_bytecodes = []
    byte_list = [data[i:i+1] for i in range(len(data))]
    split_values = {b'\x00', b'\x01', b'\x05', b'\x08', b'\x10', b'(', b'\x1a', b'\x04', b'\x11', b'\x15', b'\x19'}
    current_byte = byte_list[0]
    for byte in byte_list:
        if byte in split_values:
            if current_byte:
                list_bytecodes.append(current_byte)
            list_bytecodes.append(byte)
            current_byte = None
        else:
            if current_byte is None:
                current_byte = byte
            else:
                current_byte += byte
    if current_byte:
        list_bytecodes.append(current_byte)
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
    with codecs.open(output_path, "w", "utf-8") as f:
        line_counter = 0
        while line_counter < len(lines):
            line = lines[line_counter]

            if contains_japanese(line.decode("932", errors='ignore')):
                print(line.decode("932", errors='ignore'))
                line = line.decode("932", errors='ignore')
                line = line.replace("", "MALE NAME")   # \x10
                line = line.replace("", "FEMALE NAME") # \x11
                line = line.replace("", "CLEAR_TEXTBOX\n") # \x02 Clear textbox
                line = line.replace("", "AUTO-")           # \x04 Probably used for auto-mode.
                line = line.replace("", "MALE SURNAME")    # \x12 Male Surname

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
                    f.write(str(line)[2:-1] + "\n")

            line_counter += 1


# Main processing loop
def process_files(input_dir="scripts", output_dir="scripts_txts"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    counter = 0
    for fs in os.listdir(input_dir):
        if not fs.endswith(".SNX"):
            continue

        with open(os.path.join(input_dir, fs), "rb") as f:
            data = f.read()

        list_bytes = parse_bytecode(data)

        if list_bytes:
            output_path = os.path.join(output_dir, fs.replace(".SNX", ".txt"))
            save_text(list_bytes, output_path)
        counter += 1


# Run the processing function
process_files(input_dir="script_original", output_dir="script_decoded")

