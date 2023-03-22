class Buffer:
    def __init__(self, input_file_name: str):
        self.content = ''
        self.buffer_size = 128
        self.buffer_pos = 0
        self.current_line = 1
        self.input_file = open(input_file_name, 'r')
        self.__fill_buffer()

    def __fill_buffer(self):
        self.content = self.input_file.read(self.buffer_size)
        self.buffer_pos = 0

    def get_next_char(self):
        if self.buffer_pos == len(self.content):
            self.__fill_buffer()
        if self.buffer_pos == len(self.content):
            return ''
        next_char = self.content[self.buffer_pos]
        self.buffer_pos += 1
        if next_char is '\n':
            self.current_line += 1
        return next_char

    def rollback(self, char):
        if char == '\n':
            return
        self.buffer_pos -= 1
