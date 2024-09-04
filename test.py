import os
input_dir = "script\main.snx"



# Function to determine if a byte is likely part of Shift JIS text
def is_shift_jis_byte(byte):
    # Shift JIS: 0x81-0x9F, 0xE0-0xEF are first byte ranges of multi-byte characters
    return (0x81 <= byte <= 0x9F) or (0xE0 <= byte <= 0xEF)


# Read the file as raw bytes
with open(input_dir, "rb") as f:
    data = f.read()

decoded_parts = []
i = 0
while i < len(data):
    byte = data[i]
    try:
        # If it's likely a Shift JIS byte, attempt to decode it
        if is_shift_jis_byte(byte):
            # Attempt to decode as Shift JIS
            # Find the length of the sequence (1 or 2 bytes)
            if (0xA1 <= data[i + 1] <= 0xDF) or (0x40 <= data[i + 1] <= 0x7E) or (0x80 <= data[i + 1] <= 0xFC):
                segment = data[i:i + 2]
                i += 2
            else:
                segment = bytes([byte])
                i += 1

            decoded_text = segment.decode("shift_jis")
            decoded_parts.append(decoded_text)
            print(decoded_text)
        else:
            # Otherwise, treat it as binary data
            decoded_parts.append(data[i:i + 1])
            i += 1
    except (UnicodeDecodeError, IndexError):
        # Handle errors gracefully, treat as binary
        decoded_parts.append(data[i:i + 1])
        i += 1
print(decoded_parts)
