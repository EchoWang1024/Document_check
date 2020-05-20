# -*- coding: utf-8 -*-
# @Time    : 2020-05-12 15:55
# @Author  : wangzhen
# @Email   : wangzhen2014@xiaochuankeji.cn
# @File    : apk_duplication.py
# @Software: PyCharm

import os
import sys
import threading
import time
import zipfile

class FileDuplication():

    def __init__(self, target_path):

        self.target_path = target_path
        self.local_path = os.path.abspath(".")
        self.result_path = os.path.join(self.local_path, "result.txt")
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(10)

    def get_files_path(self):

        paths = []
        for root, dirs, files in os.walk(self.target_path):
            for fn in files:
                paths.append(os.path.join(root, fn))
        return paths

    def find_duplication(self):

        all_files_md5 = self.get_all_files_md5()
        md5_list_keys = []
        for i in all_files_md5.keys():
            md5_list_keys.append(i)
        length = len(md5_list_keys)
        f = open(self.result_path, "a")
        f.truncate()
        for i in range(length - 1):
            threading.Thread(target=self.in_search, args=(i, length, md5_list_keys, all_files_md5, f)).start()
        f.close()
        print("结束时间")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def in_search(self, i, length, md5_keys, all_md5, f):
        with self.sem:
            # print("当前检查文件 " +all_md5[md5_keys[i]])
            lists = []
            for j in range(i + 1, length):
                if all_md5[md5_keys[i]] == all_md5[md5_keys[j]]:
                    if md5_keys[i] != md5_keys[j]:
                        lists.append(md5_keys[j])
            if lists != []:
                self.lock.acquire()
                f.write("发现相同md5 " + all_md5[md5_keys[i]] + "\n")
                f.write(md5_keys[i] + "\n")
                for i in lists:
                    f.write(i + "\n")
                self.lock.release()

    def get_md5(self, file):

        file_md5 = os.popen("md5 " + file).read().strip()
        file_md5 = file_md5.split("=")[-1].strip(" ")
        return file_md5

    def get_all_files_md5(self):

        all_files_md5 = {}
        path = self.get_files_path()
        for i in path:
            file_md5 = self.get_md5(i)
            if file_md5 != "":
                all_files_md5.update({i: file_md5})
        print(all_files_md5)
        return all_files_md5

    def unzip_file(self, zip_src, dst_dir):
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
        else:
            print('This is not zip')


if __name__ == "__main__":

    try:
        target_path = sys.argv[1]
        print(target_path)
    except:
        target_path = None
    if target_path:
        Ad = FileDuplication(target_path)
        Ad.find_duplication()
    else:
        print("You didn't write the path, asshole！")
