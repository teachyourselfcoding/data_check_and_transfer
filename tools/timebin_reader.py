import struct


class TimeReader:

    def __init__(self, filename):
        self.header_bytes = 0
        self.frm_bytes = 0
        self.filename = filename
        self.f_handle = open(filename, 'rb')
        self.read_file_header()

    def read_file_header(self):
        buf = self.f_handle.read(1)
        buf = buf + b'\x00\x00\x00'
        self.header_bytes = struct.unpack("i", buf)
        buf = self.f_handle.read(1)
        buf = self.f_handle.read(2)
        buf = buf + b'\x00\x00'
        self.frm_bytes = struct.unpack("i", buf)

    def read_frm_header(self):
        buf = self.f_handle.read(1)
        header_bytes = struct.unpack("B", buf)
        buf = self.f_handle.read(7)
        buf = self.f_handle.read(8)
        timestamp, = struct.unpack('Q', buf)
        buf = self.f_handle.read(8)
        payload_bytes, = struct.unpack('Q', buf)
        return timestamp, payload_bytes

    def read_frm(self):
        timestamp, payload_bytes = self.read_frm_header()
        payload = self.f_handle.read(payload_bytes)
        return timestamp, payload

    def get_time_list(self):
        time_list = []
        while True:
            try:
                t, _ = self.read_frm()
                time_list.append(t)
            except:
                break
        return time_list


if __name__ == "__main__":
    file = "/home/SENSETIME/meijie/Work/adas/test_record/data_2/origin/NOR_stream0_20201210194727_10_298.mp4.time.bin"
    reader = TimeReader(file)
    print(reader.get_time_list())
