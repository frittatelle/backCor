import struct
import numpy

l_int16 = 2
l_int32 = 4
l_int64 = 8
s_int16 = "<H"
s_int32 = "<I"                  # little edian
s_int64 = "<Q"                  # little edian

l_float = 4
s_float = "<f"
l_double = 8
s_double = "<d"


class wdfReader(object):
    def __init__(self, file_name):
        try:
            self.file_obj = open(file_name, "rb")
        except IOError:
            raise IOError("File {} does noe exist!".format(file_name))
        # Initialize the properties for the wdfReader class
        self.title = ""
        self.username = ""
        self.measurement_type = ""
        self.scan_type = ""
        self.laser_wavenumber = None
        self.count = None
        self.spectral_units = ""
        self.xlist_type = None
        self.xlist_units = ""
        self.ylist_type = None
        self.ylist_units = ""
        self.point_per_spectrum = None
        self.data_origin_count = None
        self.capacity = None
        self.application_name = ""
        self.application_version = [None]*4
        self.xlist_length = None
        self.ylist_length = None
        self.accumulation_count = None
        self.block_info = {}    # each key has value (offset, size)
        # Parse the header section in the wdf file
        try:
            self.parse_header()
        except:
            print("Failed to parse the header of file")
        # Location the data, xlist, ylist and
        try:
            self.block_info["DATA"] = self.locate_block("DATA")
            self.block_info["XLST"] = self.locate_block("XLST")
            self.block_info["YLST"] = self.locate_block("YLST")
        except:
            print("Failed to get the block information")
        # set xlist and ylist unit and type
        self.xlist_type, self.xlist_units = self.get_xlist_info()
        self.ylist_type, self.ylist_units = self.get_ylist_info()
        # set the data origin, if count is not 0 (for mapping applications)
        if (self.data_origin_count != None) and (self.data_origin_count != 0):
            try:
                self.block_info["ORGN"] = self.locate_block("ORGN")
            except:
                print("Failed to get the block information")


    def _read_int16(self):
        return struct.unpack(s_int16, self.file_obj.read(l_int16))[0]
    def _read_int32(self):
        return struct.unpack(s_int32, self.file_obj.read(l_int32))[0]
    def _read_int64(self):
        return struct.unpack(s_int64, self.file_obj.read(l_int64))[0]
    def _read_float(self):
        return struct.unpack(s_float, self.file_obj.read(l_float))[0]
    def _read_double(self):
        return struct.unpack(s_double, self.file_obj.read(l_double))[0]
    def _read_utf8(self, size):
        # TODO: strip the blanks
        return self.file_obj.read(size).decode("utf8")

    # The method for reading the info in the file header
    def parse_header(self):
        self.file_obj.seek(0)   # return to the head
        block_ID = self.file_obj.read(4).decode("ascii")  # Must make the conversion under python3
        block_UID = self._read_int32()
        block_len = self._read_int64()
        if (block_ID != "WDF1") or (block_UID != 0 and block_UID != 1) \
           or (block_len != 512):
            raise ValueError("The wdf file format is incorrect!")

        # The keys from the header
        self.file_obj.seek(60)
        self.point_per_spectrum = self._read_int32()
        self.capacity = self._read_int64()
        self.count = self._read_int64()
        self.accumulation_count = self._read_int32()
        self.ylist_length = self._read_int32()
        self.xlist_length = self._read_int32()
        self.data_origin_count = self._read_int32()
        self.application_name = self._read_utf8(24)
        for i in range(4):
            self.application_version[i] = self._read_int16()
        # TODO: change the types to string
        self.scan_type = self._read_int32()
        self.measurement_type = self._read_int32()
        # For the units
        # TODO: change to string
        self.file_obj.seek(152)
        self.spectral_units = self._read_int32()
        self.laser_wavenumber = self._read_float()
        # Username and title
        self.file_obj.seek(208)
        self.username = self._read_utf8(32)
        self.title = self._read_utf8(160)

    # locate the data block offset with the corresponding block name
    def locate_block(self, block_name):
        if (block_name in self.block_info) and (self.block_info[block_name] is not None):
            return self.block_info[block_name]
        else:
            # find the block by increment in block size
            # exhaustive but no need to worry
            curr_name = None
            curr_pos = 0
            next_pos = curr_pos
            self.file_obj.seek(curr_pos)
            while (curr_name != block_name) and (curr_name != ""):
                curr_pos = next_pos
                curr_name = self.file_obj.read(4).decode("ascii")  # Always a 4-str block name
                uid = self._read_int32()
                size = self._read_int64()
                next_pos += size
                self.file_obj.seek(next_pos)
                # print(curr_name, curr_pos, uid, size)
            # found the id
            if curr_name == block_name:
                return (curr_pos, size)
            else:
                raise ValueError("The block with name {} is not found!".format(block_name))


    # get the xlist info
    def get_xlist_info(self):
        pos, size = self.locate_block("XLST")
        offset = 16
        self.file_obj.seek(pos + offset)
        #TODO: strings
        data_type = self._read_int32()
        data_unit = self._read_int32()
        return (data_type, data_unit)

    # get the ylist info
    def get_ylist_info(self):
        pos, size = self.locate_block("YLST")
        offset = 16
        self.file_obj.seek(pos + offset)
        #TODO: strings
        data_type = self._read_int32()
        data_unit = self._read_int32()
        return (data_type, data_unit)


    def get_xdata(self):
        pos = self.locate_block("XLST")[0]
        offset = 24
        self.file_obj.seek(pos + offset)
        size = self.xlist_length
        self.file_obj.seek(pos + offset)
        x_data = numpy.fromfile(self.file_obj, dtype="float32", count=size)
        return x_data



    def get_ydata(self):
        pos = self.locate_block("YLST")[0]
        offset = 24
        self.file_obj.seek(pos + offset)
        size = self.ylist_length
        self.file_obj.seek(pos + offset)
        y_data = numpy.fromfile(self.file_obj, dtype="float32", count=size)
        return y_data


    def get_spectra(self, start=0, end=-1):
        if end == -1:           # take all spectra
            end = self.count-1
        if (start not in range(self.count)) or (end not in range(self.count)):
            raise ValueError("Wrong start and end indices of spectra!")
        if start > end:
            raise ValueError("Start cannot be larger than end!")

        pos_start = self.locate_block("DATA")[0] + 16 + l_float*start*self.point_per_spectrum
        n_row = end - start + 1
        self.file_obj.seek(pos_start)
        spectra_data = numpy.fromfile(self.file_obj, dtype="float32", count=n_row*self.point_per_spectrum)
        if len(spectra_data.shape) == 1:
            # The spectra is only 1D array
            return spectra_data
        else:
            # Make 2D array
            spectra_data = spectra_data.reshape(n_row, spectra_data.size // n_row)
            return spectra_data
