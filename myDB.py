import sys


class DBHelper:

    def __init__(self):
        self.stack = []
        self.original = []
        self.data = {}
        self.value_count = {}

    def set(self, key, value, in_transaction):
        if key in self.data:
            self.value_count[self.data[key]] -= 1 # Reduce count to 0 allowed.
        self.data[key] = value
        self.value_count[value] = self.value_count.get(value, 0) + 1
        # TO-DO: implement adding to stack when in transaction
        line = ["SET", key, value]
        if in_transaction == 1:
            self.stack[-1].append(line)
        elif in_transaction == 0:
            self.original.append(line)

    def get(self, key):
        if key in self.data:
            return self.data[key]
        return None

    def unset(self, key, in_transaction):
        if key in self.data:
            self.value_count[self.data[key]] -= 1
            del self.data[key]
            line = ["UNSET", key]
            if in_transaction == 1:
                self.stack[-1].append(line)
            elif in_transaction == 0:
                self.original.append(line)
            return 1
        return 0

    def get_num(self, val):
        if val in self.value_count:
            return self.value_count[val]
        return 0

    def begin(self):
        self.stack.append([])

    def roll_back(self):
        if len(self.stack) == 0:
            return True, True  # Not in block.
        del self.stack[-1]
        self.data = {}
        self.value_count = {}
        for line in self.original:
            self.execute(line)
        if len(self.stack) != 0:
            for block in self.stack:
                for comm in block:
                    self.execute(comm)
            return False, False
        return True, False

    def execute(self, line):
        if len(line) == 3:
            self.set(line[1], line[2], -1)
        else:
            self.unset(line[1], -1)

    def commit(self):
        no_transaction = True
        if len(self.stack) != 0:
            no_transaction = False
        self.stack = []
        return no_transaction

commands = "SET", "GET", "UNSET", "NUMEQUALTO", "END", "BEGIN", "ROLLBACK", "COMMIT"
helper = DBHelper()
in_transaction = False

for raw in sys.stdin:
    keys = raw.strip().split(" ")

    if keys[0] not in commands:
        print ("Command Not Found. Please Enter a Valid Command.")
        continue

    idx = commands.index(keys[0])
    size = len(keys)

    if idx == 0 and size == 3:
        flag = 0
        if in_transaction:
            flag = 1
        helper.set(keys[1], keys[2], flag)
        continue

    if idx == 1 and size == 2:
        value = helper.get(keys[1])
        if value is None:
            print ("NULL")
        else:
            print (value)
        continue

    if idx == 2 and size == 2:
        flag = 0
        if in_transaction:
            flag = 1
        exist = helper.unset(keys[1], flag)
        if exist == 0:
            print ("Variable Does Not Exist in Database.")
        continue

    if idx == 3 and size == 2:
        value = helper.get_num(keys[1])
        print (value)
        continue

    if idx == 4 and size == 1:
        break

    if idx == 5 and size == 1:
        in_transaction = True
        helper.begin()
        continue

    if idx == 6 and size == 1:
        end_all, flag = helper.roll_back()
        in_transaction = not end_all
        if flag:
            print ("NO TRANSACTION")
        continue

    if idx == 7 and size == 1:
        flag = helper.commit()
        in_transaction = False
        if flag:
            print ("NO TRANSACTION")
        continue

    print ("Invalid Command. Please Reenter.")
