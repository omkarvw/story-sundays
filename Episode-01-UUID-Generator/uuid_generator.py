import time

# --- Bit Allocations ---
TIMESTAMP_BITS = 41
DATACENTER_BITS = 5
MACHINE_BITS = 5
SEQUENCE_BITS = 12

# --- Pre-calculated Masks and Shifts ---
MAX_SEQUENCE = -1 ^ (-1 << SEQUENCE_BITS)
MACHINE_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + MACHINE_BITS
TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_BITS + DATACENTER_BITS

# Example Configuration (in a real system, this would be dynamic)
DATACENTER_ID = 3
MACHINE_ID = 7

# --- State Variables (must persist for each instance) ---
last_timestamp = -1
sequence = 0

def generate_id():
    global last_timestamp, sequence

    current_timestamp = int(time.time() * 1000)

    # 1. Handle clock rollback: Refuse to generate IDs if clock moves backward.
    if current_timestamp < last_timestamp:
        raise ValueError("Clock moved backwards! Refusing to generate ID.")

    if current_timestamp == last_timestamp:
        # 2. Increment sequence number if in the same millisecond.
        sequence = (sequence + 1) & MAX_SEQUENCE
        # 3. If sequence is maxed out (4096 IDs per ms), wait for the next millisecond.
        if sequence == 0:
            while current_timestamp <= last_timestamp:
                current_timestamp = int(time.time() * 1000)
    else:
        # 4. Reset sequence for a new millisecond.
        sequence = 0

    last_timestamp = current_timestamp

    # 5. Build the 64-bit ID by bit-shifting and combining the parts.
    new_id = (current_timestamp << TIMESTAMP_SHIFT) | \
             (DATACENTER_ID << DATACENTER_ID_SHIFT) | \
             (MACHINE_ID << MACHINE_ID_SHIFT) | \
             sequence

    return new_id

if __name__ == "__main__":
    for _ in range(5):
        print(f"Generated ID: {generate_id()}")