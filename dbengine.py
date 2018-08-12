import sqlite3
import random as rnd


def rnd_id():
    s = "0123456789abcdefghijklmnopqrstuvwxyz"
    n = 16
    return "".join(rnd.sample(list(s), n))


# ORM
class Building:
    def __init__(self, name="", desc="", btype="", nb_rooms="", owner="", building_id=None):
        self.building_id = building_id if building_id else rnd_id()
        self.name = name
        self.desc = desc
        self.btype = btype
        self.nb_rooms = nb_rooms
        self.owner = owner


class Owner:
    def __init__(self, name="", age="", owner_id=None):
        self.owner_id = owner_id if owner_id else rnd_id()
        self.name = name
        self.age = age


## Sqlite specific definitions
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class RealEstateDbSession:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()

    def __add(self, tbl, dct):
        self.cur.execute("INSERT INTO {} ({}) VALUES ({})".format(
            tbl, ','.join(dct.keys()), ','.join(map(repr, dct.values()))))

    def __update(self, tbl, dct, unique_id):
        lst = list("{k}={v}".format(k=k, v=repr(v)) for k, v in dct.items())
        self.cur.execute("UPDATE {} SET {} WHERE {}={}".format(tbl, ','.join(lst), unique_id[0], repr(unique_id[1])))

    def __delete(self, tbl, unique_id):
        self.cur.execute("DELETE FROM {} WHERE {}={}".format(tbl, unique_id[0], repr(unique_id[1])))

    def __retrieve(self, tbl, dct, one=False):
        if not dct:
            rslt = self.cur.execute("SELECT * FROM {tbl}".format(tbl=tbl))
            one = False
        else:
            lst = list("{k}={v}".format(k=k, v=repr(v)) for k, v in dct.items())
            rslt = self.cur.execute("SELECT * FROM {} WHERE {}".format(tbl, ' AND '.join(lst)))
        if one:
            return rslt.fetchone()
        else:
            return rslt.fetchall()

    def add_building(self, b: Building):
        self.__add("buildings", b.__dict__)
        
    def update_building(self, b: Building):
        self.__update("buildings", b.__dict__, ("building_id", b.building_id))
        
    def delete_building(self, b: Building):
        self.__delete("buildings", ("building_id", b.building_id))
        
    def get_building(self, dct):
        def loop(a):
            for k, v in a.items():
                if v:
                    yield k, v
        dct = dict(loop(dct.__dict__)) if type(dct) == Building else dct
        rslt = self.__retrieve("buildings", dct, one=True)
        return Building(**rslt) if rslt else rslt

    def get_buildings(self, dct=None):
        return [Building(**x) for x in self.__retrieve("buildings", dct)]

    def add_owner(self, b: Owner):
        self.__add("owners", b.__dict__)

    def update_owner(self, b: Owner):
        self.__update("owners", b.__dict__, ("owner_id", b.owner_id))

    def delete_owner(self, b: Owner):
        self.__delete("owners", ("owner_id", b.owner_id))

    def get_owner(self, dct):
        def loop(a):
            for k, v in a.items():
                if v:
                    yield k, v
        dct = dict(loop(dct.__dict__)) if type(dct) == Owner else dct
        rslt = self.__retrieve("owners", dct, one=True)
        return Owner(**rslt) if rslt else rslt

    def get_owners(self, dct):
        return [Owner(**x) for x in self.__retrieve("owners", dct)]

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()
