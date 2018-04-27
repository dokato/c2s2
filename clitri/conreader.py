import re

class ConTag(object):

    def __init__(self, txt, ttype):
        self.txt = txt
        self.type = ttype

    def __repr__(self):
        return "CT(%s, %s)" % (self.txt, self.type)

class ConNer(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.tags = self.con_reader(file_name)

    def con_reader(self, file_name):
        tags = []
        rex_txt = re.compile("c=\".*\" ")
        rex_typ = re.compile("\|\|t=\".*\"")
        with open(file_name, 'r') as f:
            for l in f:
                txt = rex_txt.findall(l)[0][3:-2]
                ttype = rex_typ.findall(l)[0][5:-1]
                tags.append(ConTag(txt, ttype))
        return tags

    def give_specific_type(self, ttype):
        ntags = []
        for tg in self.tags:
            if tg.type == ttype:
                ntags.append(tg)
        return ntags

if __name__ == '__main__':
    cn = ConNer('condtaggeddata/101.xml.con')
    print(cn.give_specific_type("problem"))
