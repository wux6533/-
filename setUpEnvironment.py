# -*- coding:utf-8 -*-
from pages.dataManagement.vehicleManagement.vehgroupAdd import vehgroupAdd
from pages.dataManagement.bulkImport.importVehicle import importVehicle
from selenium.webdriver.common.action_chains import ActionChains
from pages.dataManagement.userManagement.userAdd import userAdd
from base.jiekou.rulesApi import RulesApi
from time import sleep
import unittest
import os


class SetUpEnvironment(userAdd, vehgroupAdd, importVehicle):
    # 根据车组名点开车组
    def diankaichezu_bind(self, groupName_arr):
        try:
            for groupName in groupName_arr:
                xp = ".//a[@title='%s']/preceding-sibling::span[contains(@id,'bind-tree-check1')][2]" % groupName
                ope = self.dr.find_element_by_xpath(xp)
                ActionChains(self.dr).move_to_element(ope).perform()
                sleep(1)
                tx = ope.get_attribute("class")
                n = tx.find("_") + 1
                xx = tx[n:]
                # 判断准备打开用户是否有下级用户
                if xx == "docu":
                    print("%s没有下级用户" % groupName)
                else:
                    # 判断用户是否已经打开
                    if xx == "open":
                        pass
                    elif xx == "close":
                        self.dr.find_element_by_xpath(xp).click()
                        sleep(1)
        except Exception as e:
            print("根据车组名点击车组失败！原因：%s" % e)
            exit(1)

    # 进入新增下级车组或用户界面
    def open_add_sub_group_page(self, parent_arr, groupName):
        """groupName_arr 是车组的上级车组数组， groupName 时新增下级车组的车组名"""
        self.diankaichezu_by_groupName(parent_arr)  # 点击新增前先打开上级车组
        self.dianji_yonghu_or_chezu_by_name(groupName)  # 根据车组名点击车组
        self.dr.find_element_by_xpath(".//span[@title='添加车组']").click()
        sleep(1)

    # 打开新增下级用户界面
    def open_add_sub_user_page(self, parent_arr, userName):
        """groupName_arr 是车组的上级车组数组， userName 时新增下级车组的车组名"""
        self.diankaichezu_by_groupName(parent_arr)  # 点击新增前先打开上级车组
        self.dianji_yonghu_or_chezu_by_name(userName)  # 根据车组名点击车组
        self.dr.find_element_by_xpath(".//span[@title='新增下级用户']").click()
        sleep(1)

    # 新增用户并绑定车组
    def add_user_bing_group(self, info_arr):
        try:
            self.dr.find_element_by_xpath(".//input[@placeholder='请输入您的账户']").send_keys(info_arr[0])
            self.dr.find_element_by_xpath(".//input[@placeholder='请输入您的密码']").send_keys(info_arr[1])
            self.dr.find_element_by_xpath(".//input[@placeholder='请输入您的客户名称']").send_keys(info_arr[2])
            self.dr.find_element_by_xpath(".//span[text()='选择绑定车组']").click()
            sleep(2)
            self.diankaichezu_bind(info_arr[3][0:-1])
            xp = ".//a[@title='%s']/preceding-sibling::span[contains(@id,'bind-tree-check1')][1]" % info_arr[3][-1]
            check = self.dr.find_element_by_xpath(xp)
            ActionChains(self.dr).move_to_element(check).perform()
            sleep(1)
            check.click()
            self.dr.find_elements_by_xpath(".//span[text()='确 定']")[1].click()  # 点击确定
            sleep(0.5)
            self.dr.find_element_by_xpath(".//input[@placeholder='请输入您的电话']").send_keys(info_arr[4])
        except Exception as e:
            print("输入用户名、密码、客户名、联系电话失败！原因：%s" % e)
            exit(1)

    # 选中上传文件
    def xuanzhongwenjian(self, file_name):
        try:
            path = os.path.dirname(os.path.dirname(__file__))
            path.replace('/', '\\')
            file_path = path + "\\excelFile\\daorucheliang\\%s.xlsx" % file_name
            print(file_path)
            self.dr.find_element_by_class_name("ivu-upload-input").send_keys(file_path)
            sleep(1)
            # 输入文件路径，打开
        except Exception as e:
            print("选中上传文件失败！原因：%s" % e)
            exit(1)

    # 选中导入车组
    def select_vehgroup(self, parent_arr, groupName):
        try:
            self.dr.find_element_by_xpath(".//*[ @class ='choice-vehicle-group']/div[1]/div/div[1]").click()
            self.diankaichezu_by_groupName(parent_arr)
            self.dianji_yonghu_or_chezu_by_name(groupName)
        except Exception as e:
            print("打开新增车组界面失败！原因：%s" % e)
            exit(1)

    # 设置报警规则，并绑定车辆
    def reset_alarm_rule_bind_veh(self):
        JK = RulesApi("tian", "123456")
        token = JK.token
        DB = self.DB

        # 重置位置管理区域并绑定车辆
        def reset_all_area():
            zd = {
                '线路偏移': '15566669039',
                '线路分段限速': '15566669040',
                '禁止驶出区域': '15566669041',
                '禁止驶入区域': '15566669042',
                '区域限速': '15566669043',
            }
            print("正在删除区域配置下的所有区域...")
            pathId_s = JK.get_all_area("区域配置", token)
            for pathId in pathId_s:
                JK.del_path_by_pathId(pathId, token)
            # 删除线路配置下的所有线路
            print("正在删除线路配置下的所有线路...")
            pathId_s = JK.get_all_area("线路配置", token)
            for pathId in pathId_s:
                JK.del_path_by_pathId(pathId, token)
            # 区域绑定车辆
            typ = ['线路偏移', '线路分段限速', '禁止驶出区域', '禁止驶入区域', '区域限速']
            for ty in typ:
                print("正在添加%s位置管理..." % ty)
                pathId = JK.add_safty_path(ty, token)
                print("正在给%s绑定车辆..." % ty)
                sql = "SELECT v.`vehicleId` FROM bsj.`vehicle` v WHERE v.`terminalNo` = '%s';" % zd[ty]
                vid = DB.neirong(sql, 1, 1)
                JK.bind_vehicle_path(pathId, "", vid, token)

        # 设置油量参数
        def reset_oil_parameter():
            zdbhs = ['15566669044', '15566669057']
            for zdbh in zdbhs:
                print("正在给%s车辆设置油量参数..." % zdbh)
                sql = "SELECT v.`vehicleId` FROM bsj.`vehicle` v WHERE v.`terminalNo` = '%s';" % zdbh
                vehicleId = DB.neirong(sql, 1, 1)
                JK.set_oil_parameter(vehicleId, token)

        # 重置报警规则并绑定车辆
        def reset_alarm_rule():
            zd = {
                '离线报警': '15566669046',
                '高低温报警': '15566669052',
                '不定位报警': '15566669047',
                '夜间禁行报警': '15566669048'
            }
            typs = ['离线报警', '高低温报警', '不定位报警', '夜间禁行报警']
            # 删除旧规则
            for ty in typs:
                print("正在删除%s报警规则..." % ty)
                ruleIds = JK.get_all_rule_info(ty, token)
                for ruleId in ruleIds:
                    JK.del_alarm_rule(ruleId, token)
            # 增加新规则并绑定车辆
            for ty in typs:
                print("正在添加%s报警规则..." % ty)
                ruleId = JK.add_alarm_rule(ty, token)
                print("正在给%s报警规则绑定车辆..." % ty)
                sql = "SELECT v.`vehicleId` FROM bsj.`vehicle` v WHERE v.`terminalNo` = '%s';" % zd[ty]
                vid = DB.neirong(sql, 1, 1)
                JK.rule_bind_vehicle(ruleId, vid, token)

        # 重置道路等级设置
        def reset_road_rule():
            zd = {
                '道路等级': '15566669049',
                '夜间道路等级': '15566669050'
            }
            ruleIds = JK.find_road_rule_info(token)
            for ruleId in ruleIds:
                print("正在删除道路等级规则...")
                JK.delete_road_rule_info(ruleId, token)
            for ty in ['道路等级', '夜间道路等级']:
                print("正在添加%s规则..." % ty)
                ruleId = JK.insert_road_rule(ty, token)
                print("正在给%s规则绑定车辆..." % ty)
                sql = "SELECT v.`vehicleId` FROM bsj.`vehicle` v WHERE v.`terminalNo` = '%s';" % zd[ty]
                vid = DB.neirong(sql, 1, 1)
                JK.binding_road_rule(ruleId, '', vid, token)

        reset_all_area()  # 重置位置管理区域并绑定车辆
        reset_oil_parameter()  # 设置油量参数
        reset_alarm_rule()  # 重置报警规则并绑定车辆
        reset_road_rule()  # 重置道路等级设置


class SetUpEnvironmentUnitTest(unittest.TestCase):
    LL = None

    @classmethod
    def setUpClass(cls):
        cls.LL = SetUpEnvironment()
        LL = cls.LL
        LL.openDriver()  # 打开浏览器
        LL.login("liuyuntian", "123456")  # 登录
        LL.openDataManagementPage()  # 进入资料管理
        # LL.mask_next(1)

    @classmethod
    def tearDownClass(cls):
        cls.LL.closeDriver()

    def setUp(self):
        pass

    def tearDown(self):
        self.LL.Refresh()

    def test_greate_vehgroup(self):
        """创建车组"""
        self.LL.openVehicleManagementPage()  # 进入车辆管理界面
        self.LL.Refresh()
        parent = ["车组管理"]
        czs = ["车辆管理组", "一般测试组", "用户管理组"]
        for cz in czs:
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.open_add_sub_group_page(parent, "自动化测试组")  # 进入新增下级车组界面
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        # 增加车辆管理组下级车组
        parent = ["车组管理", "自动化测试组"]
        czs = ["批量导入测试组", "删除车辆测试组", "删除车组测试组", "搜索车辆测试组",
               "新增车辆测试组", "新增车组测试组", "修改车辆测试组", "修改车组测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "车辆管理组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        # 增加一般测试组测试组下级车组
        czs = ["报警组", "到期组", "庞博组", "少于50辆组", "天王组", "无车组", "相同车牌组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "一般测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        # 增加用户管理组下级车组
        czs = ["1号测试组", "绑定测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "用户管理组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        # 增加批量导入测试组下级车组
        parent = ["车组管理", "自动化测试组", "车辆管理组"]
        czs = ["批量导入1"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "批量导入测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)
        # 增加新增车组测试组下级车组
        czs = ["监控界面车组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "新增车组测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)
        # 增加修改车辆测试组下级车组
        czs = ["尾款金额组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "修改车辆测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)
        # 增加修改车组测试组下级车组
        czs = ["1号修改测试组", "3号修改测试组", "4号修改测试组", "6号修改测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "修改车组测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        parent = ["车组管理", "自动化测试组", "用户管理组"]
        # 新增1号测试组下级车组
        czs = ["2号测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "1号测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)
        # 新增绑定测试组级车组
        czs = ["1号绑定组", "2号绑定组", "3号绑定组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "绑定测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

        parent = ["车组管理", "自动化测试组", "车辆管理组", "修改车组测试组"]
        # 增加1号修改测试组下级车组
        czs = ["修改测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "1号修改测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)
        # 增加3号修改测试组下级车组
        czs = ["修改上级测试组"]
        for cz in czs:
            self.LL.open_add_sub_group_page(parent, "3号修改测试组")  # 进入新增下级车组界面
            da = [cz, "15574811614", "轿车", "无敌是多么寂寞"]
            self.LL.vehgroup_Add(da[0], da[1], da[3])  # 输入车组名、联系方式、备注
            self.LL.baocun_vehgroupAdd()  # 点击保存
            sleep(2)

    def test_greate_user(self):
        """创建用户"""
        zd = {
            "zidonghua": ["自动化测试组"],
            "cheliangguanli": ["自动化测试组", "车辆管理组"],
            "tian": ["自动化测试组", "一般测试组"],
            "yonghuguanli": ["自动化测试组", "用户管理组"],
            "piliangdaoru": ["自动化测试组", "车辆管理组", "批量导入测试组"],
            "shanchucheliang": ["自动化测试组", "车辆管理组", "删除车辆测试组"],
            "shanchuchezu": ["自动化测试组", "车辆管理组", "删除车组测试组"],
            "sousuocheliang": ["自动化测试组"],
            "xinzengcheliang": ["自动化测试组", "车辆管理组", "新增车辆测试组"],
            "xinzengchezu": ["自动化测试组", "车辆管理组", "新增车组测试组"],
            "xiugaicheliang": ["自动化测试组", "车辆管理组", "修改车辆测试组"],
            "xiugaichezu": ["自动化测试组", "车辆管理组", "修改车组测试组"],
            "wubi": ["自动化测试组", "一般测试组", "天王组"],
            "wuche": ["自动化测试组", "一般测试组", "无车组"],
            "授权币划拨": ["自动化测试组", "一般测试组", "天王组"],
            "bangding": ["自动化测试组", "用户管理组"],
            "daochu": ["自动化测试组", "用户管理组"],
            "denglu": ["自动化测试组", "用户管理组"],
            "shanchu": ["自动化测试组", "用户管理组"],
            "sousuo": ["自动化测试组", "用户管理组"],
            "xinzeng": ["自动化测试组", "用户管理组"],
            "xiugai": ["自动化测试组", "用户管理组"],
            "yonghuxinxi": ["自动化测试组", "用户管理组"],
        }
        self.LL.openUserManagementPage()  # 进入用户管理界面
        self.LL.Refresh()  # 刷新
        # 新增liuyuntian的下级用户zidonghua
        self.LL.openUserAddPage()  # 进入新增用户界面
        da = ['zidonghua', '123456', 'zidonghua', '绑定', '我的客户', '有删除权限', '15574811614']
        self.LL.user_add(da[0], da[1], da[2], da[3], da[6])
        self.LL.baocun_userAdd()  # 点击保存
        self.LL.Refresh()  # 刷新

        # 新增zidonghua的下级用户
        user_parent = ["liuyuntian", "zidonghua"]
        son_name = ["cheliangguanli", "tian", "yonghuguanli"]
        for name in son_name:
            da = [name, '123456', name, zd[name], '15574811614']
            self.LL.open_add_sub_user_page(user_parent[0:-1], user_parent[-1])  # 进入新增下级用户界面
            self.LL.add_user_bing_group(da)
            self.LL.baocun_userAdd()  # 点击保存
            self.LL.Refresh()  # 刷新

        # 新增cheliangguanli的下级用户
        user_parent = ["liuyuntian", "zidonghua", "cheliangguanli"]
        son_name = ["piliangdaoru", "shanchucheliang", "shanchuchezu", "sousuocheliang",
                    "xinzengcheliang", "xinzengchezu", "xiugaicheliang", "xiugaichezu"]
        for name in son_name:
            da = [name, '123456', name, zd[name], '15574811614']
            self.LL.open_add_sub_user_page(user_parent[0:-1], user_parent[-1])  # 进入新增下级用户界面
            self.LL.add_user_bing_group(da)
            self.LL.baocun_userAdd()  # 点击保存
            self.LL.Refresh()  # 刷新

        # 新增tian的下级用户
        user_parent = ["liuyuntian", "zidonghua", "tian"]
        son_name = ["wubi", "wuche", "授权币划拨"]
        for name in son_name:
            da = [name, '123456', name, zd[name], '15574811614']
            self.LL.open_add_sub_user_page(user_parent[0:-1], user_parent[-1])  # 进入新增下级用户界面
            self.LL.add_user_bing_group(da)
            self.LL.baocun_userAdd()  # 点击保存
            self.LL.Refresh()  # 刷新

        # 新增yonghuguanli的下级用户
        user_parent = ["liuyuntian", "zidonghua", "yonghuguanli"]
        son_name = ["bangding", "daochu", "denglu", "shanchu", "sousuo", "xinzeng", "xiugai", "yonghuxinxi"]
        for name in son_name:
            da = [name, '123456', name, zd[name], '15574811614']
            self.LL.open_add_sub_user_page(user_parent[0:-1], user_parent[-1])  # 进入新增下级用户界面
            self.LL.add_user_bing_group(da)
            self.LL.baocun_userAdd()  # 点击保存
            self.LL.Refresh()  # 刷新

        # 新增bangding的下级用户
        czIds = self.LL.DB.chezu_child_chezu("用户管理组")
        czIds_str = [str(x) for x in czIds]
        groupIds = ",".join(czIds_str)
        sql = "SELECT u.`userId` FROM bsj.`user` u WHERE u.`name`='bangding';"
        datas = self.LL.DB.return_all(sql)
        parentId = str(datas[0][0])
        API = RulesApi("liuyuntian", "123456")
        token = API.token
        for i in range(130):
            name = "bangding" + str(i)
            API.add_client_user(name, "123456", name, groupIds, parentId, token)  # 调用新增用户接口
        self.LL.Refresh()  # 刷新

        # 新增sousuo"的下级用户
        group_parent = ["自动化测试组", "用户管理组"]
        user_parent = ["liuyuntian", "zidonghua", "yonghuguanli", "sousuo"]
        son_name = ["sousuo1", "sousuo2", "中文账号"]
        for name in son_name:
            da = [name, '123456', name, group_parent, '15574811614']
            self.LL.open_add_sub_user_page(user_parent[0:-1], user_parent[-1])  # 进入新增下级用户界面
            self.LL.add_user_bing_group(da)
            self.LL.baocun_userAdd()  # 点击保存
            self.LL.Refresh()  # 刷新

        # 给用户tian添加授权币（数据库登录用户必须有修改权限）
        sql = "UPDATE bsj.`user` u SET u.`money` = '60000' WHERE u.`name` = 'tian';"
        self.LL.DB.return_all(sql)
        # 给用户xiugaicheliang添加授权币
        sql = "UPDATE bsj.`user` u SET u.`money` = '600' WHERE u.`name` = 'xiugaicheliang';"
        self.LL.DB.return_all(sql)

    def test_import_vehicle(self):
        """导入车辆"""
        zd = {
            "自动化测试组": [],
            "车辆管理组": ["自动化测试组"],
            "一般测试组": ["自动化测试组"],
            "报警组": ["自动化测试组", "一般测试组"],
            "庞博组": ["自动化测试组", "一般测试组"],
            "天王组": ["自动化测试组", "一般测试组"],
            "相同车牌组": ["自动化测试组", "一般测试组"]
        }
        self.LL.openImportPage()  # 进入批量导入界面
        self.LL.Refresh()  # 刷新
        file_names = ["自动化测试组", "车辆管理组", "一般测试组", "报警组", "庞博组", "天王组", "相同车牌组"]
        for name in file_names:
            self.LL.xuanzhongwenjian(name)  # 选中文件导入
            self.LL.dianji_by_text("点击上传")  # 点击【点击上传】
            self.LL.dianji_by_text("下一步")  # 点击下一步
            sleep(1)
            self.LL.select_vehgroup(zd[name], name)
            self.LL.dianji_by_text("提交")  # 点击提交
            self.LL.shouquanqixian("暂不授权")  # 选择授权期限
            self.LL.dianji_by_text("确定授权")  # 点击确定授权
            self.LL.Refresh()  # 刷新

    def test_set_alarm_rule(self):
        self.LL.reset_alarm_rule_bind_veh()


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(SetUpEnvironmentUnitTest("test_greate_vehgroup"))  # 添加车组
    test_suite.addTest(SetUpEnvironmentUnitTest("test_greate_user"))  # 添加用户
    test_suite.addTest(SetUpEnvironmentUnitTest("test_import_vehicle"))  # 导入车辆
    test_suite.addTest(SetUpEnvironmentUnitTest("test_set_alarm_rule"))  # 绑定规则
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
    # LL = SetUpEnvironment()
    # LL.reset_alarm_rule_bind_veh()
