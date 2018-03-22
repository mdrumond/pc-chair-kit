from fuzzywuzzy import fuzz
from util import iterate_csv
RATIO_MATCH = 90


class Person(object):
    def __init__(self, name, key="", info=""):
        self.name = name
        self.key = key
        self.info = info
        if not key:
            self.has_key = False
        else:
            self.has_key = True

    def getTheirNames(self):
        return self.name

    def set_key(self, key):
        self.has_key = True
        self.key = key

    def match(self, person):
        if isinstance(person, Person) and self.has_key and person.has_key:
            return self.key == person.key
        str_person = person if isinstance(person, str) else person.name
        if fuzz.token_sort_ratio(self.name, str_person) > RATIO_MATCH:
            return True
        return False

    def __str__(self):
        info_str = (" : %s" % str(self.info)) if self.info else ""
        key_str = (" : %s" % self.key) if self.has_key else ""
        return self.name + key_str + info_str


class Institution(object):
    def __init__(self, list_inst):
        self.list_inst = list_inst

    def match(self, inst):
        str_inst = inst if isinstance(inst, str) else inst.list_inst[0]
        for i in self.list_inst:
            if fuzz.token_sort_ratio(i, str_inst) > RATIO_MATCH:
                return True
        return False

    def __str__(self):
        return self.list_inst[0]


class Institutions(object):
    def __init__(self, csv):
        insts = {}
        for i in iterate_csv(csv):
            insts[i[0]] = i
        self.insts = insts

    def get_inst(self, inst):
        for k, l in self.insts.items():
            for i in l:
                if fuzz.token_sort_ratio(i, inst) > RATIO_MATCH:
                    return Institution(l)

        return Institution([inst])
