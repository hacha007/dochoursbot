from database import cursor, conn

def get_last_shift():
    cursor.execute("SELECT * FROM shifts ORDER BY id DESC LIMIT 1")
    return cursor.fetchone()

def insert_shift(date, shift_type, clock_in):
    cursor.execute(
        "INSERT INTO shifts(date,shift_type,clock_in) VALUES(?,?,?)",
        (date, shift_type, clock_in)
    )
    conn.commit()

def update_clock_out(clock_out):
    cursor.execute("""
    UPDATE shifts
    SET clock_out=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(clock_out,))
    conn.commit()

def update_break_start(time):
    cursor.execute("""
    UPDATE shifts
    SET break_start=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(time,))
    conn.commit()

def update_break_end(time):
    cursor.execute("""
    UPDATE shifts
    SET break_end=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(time,))
    conn.commit()