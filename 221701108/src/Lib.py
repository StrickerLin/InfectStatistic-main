/**
 * Lib
 * TODO
 *
 * @author StrikerLin
 * @version 1.0
 * @since 02.17.2020
 */


import sys
import os
import re
import time

ProvinceList=['全国','安徽','北京','重庆','福建','甘肃','广东','广西','贵州','海南','河北',
              '河南','黑龙江','湖北','湖南','吉林','江苏','江西','辽宁','内蒙古','宁夏',
              '青海','山东','山西','陕西','上海','四川','天津','西藏','新疆','云南','浙江']
InfectTypeList=['ip','sp','cure','dead']
InfectTypeListCN=['感染患者','疑似患者','治愈','死亡']


class FileOperator:
    def __init__(self,path):
        self.path=path
        self.fileObj=None

    def writeLine(self,strarg):
        if not self.fileObj or self.fileObj.closed:
            try:
                self.fileObj=open(self.path,"w")
            except OSError:
                print("File Error!")
                exit(3)
        else:
            if str(self.fileObj.mode)!="w":
                try:
                    self.fileObj.close()
                    self.fileObj=open(self.path,"w")
                except OSError:
                    print("File Error!")
                    exit(3)
        self.fileObj.write(strarg+"\n")


    def readLine(self):
        if not self.fileObj or self.fileObj.closed:
            try:
                self.fileObj=open(self.path,"r")
            except OSError:
                print("File Read Error\n!FileName:"+self.path)
                exit(3)
        else:
            if self.fileObj.mode!="r":
                try:
                    self.fileObj.close()
                    self.fileObj=open(self.path,"r")
                except OSError:
                    print("File Error")
                    exit(3)
        return self.fileObj.readline()

    def close(self):
        if self.fileObj!=None and not self.fileObj.closed:
            return self.fileObj.close()
        return True


class CommandHandler:
    def __init__(self,inPath,outPath,provinceList,infectTypeList,date):
        self.logPath=inPath
        self.outPath=outPath
        self.provinceList=provinceList
        if len(infectTypeList)==0:
            self.infectTypeList=InfectTypeList
        else:
            self.infectTypeList=infectTypeList
        self.date=date

    def isArgsRightful(self):
        if self.logPath==None or not os.path.exists(self.logPath):
            return False
        #print("log right")
        if self.outPath==None:
            return False

        for item in self.provinceList:
            if item not in ProvinceList:
                return False
        #print("province right")
        for item in self.infectTypeList:
            if item not in InfectTypeList:
                return False
        #print("type right")

        if self.date:
            fileList=os.listdir(self.logPath)
            for file in fileList:
               date1=file.split(".")[0]
               if dateCompare(date1,self.date):
                   return True
        else:
            return True
        return False

    def getOutputFile(self):
        foperator=FileOperator(self.outPath)
        staticList=self.getStaticList()
        if len(self.provinceList)!=0:
            for p in ProvinceList:
                if p in self.provinceList:
                    line=p+' '
                    for t in self.infectTypeList:
                        line=line+InfectTypeListCN[InfectTypeList.index(t)]+" "+str(staticList[InfectTypeList.index(t)][ProvinceList.index(p)])+'人 '
                    foperator.writeLine(line)
        else:
            for p in ProvinceList:
                line=p+' '
                count=0
                for t in self.infectTypeList:
                    count+=staticList[InfectTypeList.index(t)][ProvinceList.index(p)]
                if count!=0:
                    for t in self.infectTypeList:
                        line = line+InfectTypeListCN[InfectTypeList.index(t)]+" "+str(staticList[InfectTypeList.index(t)][ProvinceList.index(p)])+'人 '
                    foperator.writeLine(line)
        foperator.close()

    def getStaticList(self):
        list = [[0 for i in range(len(ProvinceList))] for j in range(len(InfectTypeList))]
        fileList=self.getFileList()
        for file in fileList:
            foperator=FileOperator(self.logPath+"\\"+file)
            line=foperator.readLine()
            while line:
                obj=re.match("(.+) 新增 (.+) (\\d+)人",line)
                if obj:
                    if obj.group(2) in InfectTypeListCN:
                        list[InfectTypeListCN.index(obj.group(2))][ProvinceList.index(obj.group(1))]+=\
                              int(obj.group(3))
                        list[InfectTypeListCN.index(obj.group(2))][0]+=int(obj.group(3))
                obj=re.match("(.+) (.+) 流入 (.+) (\\d+)人",line)
                if obj:
                    if obj.group(2) in InfectTypeListCN and \
                                    obj.group(1) in ProvinceList and \
                                    obj.group(3)in ProvinceList:
                        list[InfectTypeListCN.index(obj.group(2))][ProvinceList.index(obj.group(1))]-=\
                              int(obj.group(4))
                        list[InfectTypeListCN.index(obj.group(2))][ProvinceList.index(obj.group(3))]+=\
                              int(obj.group(4))
                obj=re.match("(.+) 死亡 (\\d+)人",line)
                if obj:
                    list[InfectTypeList.index("ip")][ProvinceList.index(obj.group(1))]-=int(obj.group(2))
                    list[InfectTypeList.index("dead")][ProvinceList.index(obj.group(1))]+=int(obj.group(2))
                    list[InfectTypeList.index("dead")][0]+=int(obj.group(2))
                obj=re.match("(.+) 治愈 (\\d+)人",line)
                if obj:
                    list[InfectTypeList.index("ip")][ProvinceList.index(obj.group(1))]-=int(obj.group(2))
                    list[InfectTypeList.index("cure")][ProvinceList.index(obj.group(1))]+=int(obj.group(2))
                    list[InfectTypeList.index("cure")][0]+=int(obj.group(2))
                obj=re.match("(.+) .+ 确诊感染 (\\d+)人",line)
                if obj:
                    list[InfectTypeList.index("sp")][ProvinceList.index(obj.group(1))]-=int(obj.group(2))
                    list[InfectTypeList.index("ip")][ProvinceList.index(obj.group(1))]+=int(obj.group(2))
                    list[InfectTypeList.index("sp")][0]-=int(obj.group(2))
                    list[InfectTypeList.index("ip")][0]+=int(obj.group(2))
                obj=re.match("(.+) 排除 .+ (\\d+)人",line)
                if obj:
                    list[InfectTypeList.index("sp")][ProvinceList.index(obj.group(1))]-=int(obj.group(2))
                    list[InfectTypeList.index("sp")][0]-=int(obj.group(2))
                line = foperator.readLine()
        return list

    def getFileList(self):
        fileList=os.listdir(self.logPath)
        if self.date!=None:
            for file in fileList:
                str=file.split(".")[0]
                if not dateCompare(self.date,str):
                    fileList.remove(file)
        return fileList


def findInformation(informationName):
    list=[]
    args=sys.argv
    try:
        i=args.index(informationName)+1
        while i<len(args):
            if args[i][0]!='-':
                list.append(args[i])
            else:
                break
            i+=1
    except ValueError:
        return list
    return list

#比较datestr1和datestr2的大小
def dateCompare(datestr1,datestr2):
    time1=time.mktime(time.strptime(datestr1,"%Y-%m-%d"))
    time2=time.mktime(time.strptime(datestr2,"%Y-%m-%d"))
    return time1>=time2