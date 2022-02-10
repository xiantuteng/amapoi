# coding=utf-8

class FileContentList:
    """
    FileContentList allow you read file content as a list object.

    FileContentList('test.txt'):
            Create an object and load the contents of the file,
            it will not load everything, only the index of all lines.
    len(FileContentList('test.txt')):
            Return the numbers of lines in file.
    FileContentList('test.txt')[n]:
            Returns the content of the n'th line of the file.
    """

    def __init__(self, file_path, encoding='utf-8', buffer_size=1024 * 500):
        """
        Init FileContentList Object
        :param file_path:
        :param encoding:
        :param buffer_size:
        """
        self.file_path = file_path
        self.encoding = encoding
        self.buffer_size = buffer_size
        self.file = open(self.file_path, 'rb')
        self.index = []
        self.iter_num = -1  # current line-number
        self.loaded = False
        pass

    def __del__(self):
        self.file.close()

    def __load(self):
        """
        Load the binary offset and length(we call it the 'line index') of all lines of the file into list object.
        :return: None
        """
        # if the line index has been loaded, return immediately
        if self.loaded:
            return
        # read the line index
        buff_size = self.buffer_size
        offset, length = 0, 0
        f = self.file
        buff = f.read(buff_size)
        while len(buff) > 0:
            # find newline character '\n'
            start = 0
            pos = buff.find(0x0A, start)
            while pos >= 0:
                # founded! push the line start-position and line length to the list object
                length += (pos - start + 1)
                self.index.append([offset, length])
                offset += length
                length = 0
                start = pos + 1
                # find again
                pos = buff.find(0x0A, start)
            else:
                # there has no more newline charachter, the length must be updated
                length += (len(buff) - start)
            buff = f.read(buff_size)
        # the last line of file maybe have not newline character '\n', you need to remember them.
        if length > 0:
            self.index.append([offset, length])
        # Update flag, indicating that the row index has been loaded
        self.loaded = True
        pass

    def __len__(self):
        """
        Return the total number of lines in the file
        :return:
        """
        self.__load()
        return len(self.index)

    def __getitem__(self, item):
        self.__load()
        if isinstance(item, int):
            return self.__getitem(item)
        elif isinstance(item, slice):
            text_list = []
            start, stop, step = item.start, item.stop, item.step
            start = 0 if start is None else start
            step = 1 if step is None else step
            stop = len(self.index) if stop is None else stop
            for n in range(start, stop, step):
                text = self.__getitem(n)
                text_list.append(text)
            return text_list

    def __getitem(self, n):
        if n >= len(self.index) or n < -len(self.index):
            raise IndexError('index out of range')
        [offset, length] = self.index[n]
        self.file.seek(offset)
        b = self.file.read(length)
        text = b.decode(encoding=self.encoding, errors="strict")
        return text

    def __iter__(self):
        self.iter_num = -1
        return self

    def __next__(self):
        self.__load()
        pass
        self.iter_num += 1
        if self.iter_num >= len(self.index):
            raise StopIteration
        return self.__getitem__(self.iter_num)
