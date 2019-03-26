# -*- coding:utf-8 -*-
from pymysqlpool import ConnectionPool
from configobj import ConfigObj
import os


class db(object):
    arr_vehicle: str

    def __init__(self):
        self.count = 0
        conf_ini = os.path.dirname(os.path.dirname(__file__)) + "\\conf\\config.ini"
        config = ConfigObj(conf_ini, encoding='UTF8')
        hj = config['HJ']['hj']
        # config[hj]['db_password']
        cfig = {
            'host': config[hj]['db_host'],
            'port': 3306,
            'user': config[hj]['db_user'],
            'password': config[hj]['db_password'],
            'charset': "utf8",
            'database': config[hj]['db'],
            'autocommit': True
        }
        # config[hj]['report_db_pwd']
        cfig2 = {
            'host': config[hj]['report_db_host'],
            'port': 3306,
            'user': config[hj]['report_db_user'],
            'password': config[hj]['report_db_pwd'],
            'charset': "utf8",
            'database': config[hj]['report_db'],
            'autocommit': True
        }
        self.pool = ConnectionPool(size=2, name='pool', **cfig)
        self.pool2 = ConnectionPool(size=2, name='poo2', **cfig2)

    # 返回查询到的数据条数
    def shuliang(self, sql):
        con = self.pool.get_connection()
        with con as cur:
            cur.execute(sql)
            datas = cur.fetchall()
        count = len(datas)
        return count

    # 返回查询到的指定行、列内容
    def neirong(self, sql, row, col):
        row -= 1
        col -= 1
        con = self.pool.get_connection()
        with con as cur:
            cur.execute(sql)
            datas = cur.fetchall()
        if datas == ():
            return datas
        else:
            return datas[row][col]

    # 返回查询到的所有内容
    def return_all(self, sql):
        con = self.pool.get_connection()
        with con as cur:
            cur.execute(sql)
            datas = cur.fetchall()
        return datas

    # 查询车组下所有车辆数
    def chezu_all_cheliangshu(self, groupName, restrict):
        con = self.pool.get_connection()
        with con as cur:
            # 根据车组名查询车组id
            def get_vgid_by_vgname(vg_name):
                sql = "SELECT vg.`groupId` FROM bsj.`vehicle_group` vg WHERE vg.`groupName` = '%s';" % vg_name
                cur.execute(sql)
                datas = cur.fetchall()
                return datas[0][0]

            # 根据车组id选项车辆
            def chaxun_cl_by_vgid(vgid_id):
                sql = "SELECT v.`expireDate` FROM bsj.`vehicle_group` vg " \
                      "JOIN bsj.`vehicle` v ON(vg.`groupId`=v.`groupId`) " \
                      "WHERE vg.`groupId`='%s' %s;" % (vgid_id, restrict)
                cur.execute(sql)
                datas = cur.fetchall()
                self.count += len(datas)

            def digui_chezu(f_id):
                sql = "SELECT vg2.`groupId` FROM bsj.`vehicle_group` vg1 " \
                      "JOIN bsj.`vehicle_group` vg2 ON(vg1.`groupId`=vg2.`parentId`) " \
                      "WHERE vg1.`groupId`='%s';" % f_id
                cur.execute(sql)
                datas = cur.fetchall()
                z_id = []
                for data in datas:
                    if data[0] != "":
                        z_id.append(data[0])
                for id_ in z_id:
                    chaxun_cl_by_vgid(id_)
                    digui_chezu(id_)
            vgid = get_vgid_by_vgname(groupName)
            chaxun_cl_by_vgid(vgid)
            digui_chezu(vgid)
        return self.count

    # 查询用户下的所有用户
    def user_child_users(self, userName):
        user_arr = [userName]
        con = self.pool.get_connection()
        with con as cur:
            def digui_user(name):
                sql = "SELECT uu.`name` FROM bsj.`user` u JOIN bsj.`user` uu ON(uu.`parentId`=u.`userId`) " \
                      "WHERE u.`name`='%s'" % name
                cur.execute(sql)
                datas = cur.fetchall()
                z_id = []
                for data in datas:
                    if data[0] != "":
                        z_id.append(data[0])
                        user_arr.append(data[0])
                for name in z_id:
                    digui_user(name)
            digui_user(userName)
        return user_arr

    # 查询车组下的所有车组Id
    def chezu_child_chezu(self, cz_name):
        con = self.pool.get_connection()
        with con as cur:
            czIds = []
            sql = "SELECT vg.`groupId` FROM bsj.`vehicle_group` vg WHERE vg.`groupName`='%s';" % cz_name
            cur.execute(sql)
            datas = cur.fetchall()
            cz_id = datas[0][0]
            czIds.append(cz_id)

            # 递归查询
            def digui_vehicle_group(parentId):
                sql2 = "SELECT vg.`groupId` FROM bsj.`vehicle_group` vg WHERE vg.`parentId`='%s';" % parentId
                cur.execute(sql2)
                datas2 = cur.fetchall()
                z_id = []
                for data in datas2:
                    if data[0] != "":
                        z_id.append(data[0])
                        czIds.append(data[0])
                for pId in z_id:
                    digui_vehicle_group(pId)

            digui_vehicle_group(cz_id)
            return czIds

    # 查询车组下所有车辆车牌号或终端编号或sim卡号
    def chezu_down_cheliang(self, groupName, typ, restrict=""):
        """
        :param groupName: 车组名
        :param typ: 查询的车辆类型（比如：车牌、终端编号等）
        :param restrict: 限制条件
        """
        zd = {"车牌": "plate", "终端编号": "terminalNo", "车辆ID": "vehicleId"}
        con = self.pool.get_connection()
        with con as cur:
            arr_vehicle = []

            # 根据车组名查询车组id
            def get_vgid_by_vgname(vg_name):
                sql = "SELECT vg.`groupId` FROM bsj.`vehicle_group` vg WHERE vg.`groupName` = '%s';" % vg_name
                cur.execute(sql)
                datas = cur.fetchall()
                return datas[0][0]

            # 根据车组id选项车辆
            def chaxun_cl_by_vgid(vgid_id):
                sql = "SELECT V.`%s` FROM bsj.`vehicle` v " \
                      "WHERE v.`groupId` = '%s' %s;" % (zd[typ], vgid_id, restrict)
                cur.execute(sql)
                datas = cur.fetchall()
                for data in datas:
                    arr_vehicle.append(data[0])

            def digui_chezu(f_id):
                sql = "SELECT vg2.`groupId` FROM bsj.`vehicle_group` vg1 " \
                      "JOIN bsj.`vehicle_group` vg2 ON(vg1.`groupId`=vg2.`parentId`) " \
                      "WHERE vg1.`groupId`='%s';" % f_id
                cur.execute(sql)
                datas = cur.fetchall()
                z_id = []
                for data in datas:
                    if data[0] != "":
                        z_id.append(data[0])
                for id_ in z_id:
                    chaxun_cl_by_vgid(id_)
                    digui_chezu(id_)

            vgid = get_vgid_by_vgname(groupName)
            chaxun_cl_by_vgid(vgid)
            digui_chezu(vgid)
            return arr_vehicle

    # 返回report库中查询到的所有内容
    def return_all_report(self, sql):
        con = self.pool2.get_connection()
        with con as cur:
            cur.execute(sql)
            datas = cur.fetchall()
            return datas

    # 返回report库中查到的数据数量
    def return_quantity_report(self, sql):
        con = self.pool2.get_connection()
        with con as cur:
            cur.execute(sql)
            datas = cur.fetchall()
            return len(datas)


if __name__ == "__main__":
    DB = db()
    sql = "SELECT * FROM report.`retreatsign` si WHERE si.`vehicleId`='10000488' ORDER BY si.`signTime` DESC;"
    da = DB.return_all(sql)
    print(da[0])
    # DB.chezu_down_cheliang("报警组", "车牌", "AND v.`expireDate` IS NOT NULL")
