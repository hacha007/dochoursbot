from datetime import datetime

def calculate_hours(clock_in, clock_out, break_start, break_end):

    start = datetime.fromisoformat(clock_in)
    end = datetime.fromisoformat(clock_out)

    total = end - start

    if break_start and break_end:
        bs = datetime.fromisoformat(break_start)
        be = datetime.fromisoformat(break_end)
        total -= (be - bs)

    return total.total_seconds() / 3600