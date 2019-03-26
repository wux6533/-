# -*- coding:utf-8 -*-
from BeautifulReport import BeautifulReport
from base.mail import sendEmai
import unittest
import xlrd
import os


class boyunshikongTestRunner(object):
    # 遍历找出以Test.py 结尾的文件，导入
    @staticmethod
    def find_pyfile_and_import(rootDir):
        list_dirs = os.walk(rootDir)
        for dirName, subdirlist, filelist in list_dirs:
            for f in filelist:
                file_name = f
                if file_name[-7:] == "Test.py":
                    if dirName[-1:] != "/":
                        impath = dirName.replace("/", ".")[2:].replace("\\", ".")
                    else:
                        impath = dirName.replace("/", ".")[2:-1].replace("\\", ".")
                    if impath != "":
                        exe_str = "from " + impath + "." + file_name[0:-3] + " import " + file_name[0:-7] + "UnitTest"
                    else:
                        exe_str = "import" + file_name[0:-3]
                    print(exe_str)
                    exec(exe_str, globals())

    # 读取文件，组装测试用例
    @staticmethod
    def get_xls_case_by_index(sheet_name_list):
        xls_path = "./excelFile/case_management.xls"
        file = xlrd.open_workbook(xls_path)
        caseList = []
        for sheet_name in sheet_name_list:
            sheet = file.sheet_by_name(sheet_name)
            nrows = sheet.nrows
            for i in range(nrows):
                if sheet.row_values(i)[0].strip().upper() == 'YES' and sheet.row_values(i)[5] <= 2:
                    ClassName = sheet.cell_value(i, 2)
                    caseName = sheet.cell_value(i, 3)
                    # 组装测试用例格式 类名.("方法名")
                    case = '%s("%s")' % (ClassName.strip(), caseName.strip())
                    caseList.append(case)
        return caseList

    # 将测试用例添加到测试套件中
    def get_test_suite(self, testDir, sheet_name_list):
        """
        :param testDir: 为所有脚本的顶层目录
        :param sheet_name_list: 想要读取的表名
        """
        test_suite = unittest.TestSuite()
        self.find_pyfile_and_import(testDir)
        testCaseList = self.get_xls_case_by_index(sheet_name_list)
        for test_case in testCaseList:
            test_suite.addTest(eval(test_case))
        return test_suite


if __name__ == "__main__":
    # "登录", "用户管理", "车辆管理", "批量导入", "车辆授权", "实时报警", "综合报表", "指令",
    # "车辆显示"
    Run = boyunshikongTestRunner()
    sheet_list = ["综合报表"]
    suite = Run.get_test_suite("./test_case", sheet_list)
    result = BeautifulReport(suite)
    result.report(filename='test_result', description='博云视控自动化测试报告', log_path='./report')
    sendEmai(['1531996630@qq.com', '3003521126@qq.com', '852240095@qq.com'])
    # os.system("shutdown -s -t 60")
