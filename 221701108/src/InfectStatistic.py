import sys
import os
import re
import time

ProvinceList=['全国','安徽','北京','重庆','福建','甘肃','广东','广西','贵州','海南','河北','河南','黑龙江','湖北','湖南','吉林','江苏','江西','辽宁','内蒙古','宁夏','青海','山东','山西','陕西','上海','四川','天津','西藏','新疆','云南','浙江']
InfectTypeList=['ip','sp','cure','dead']
InfectTypeListCN=['感染患者','疑似患者','治愈','死亡']

'''
    文件操作类
    负责文件的读写
    function：
        writeLine(str)
        readLine()
        close()
'''
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
        if not self.fileObj.closed:
            self.fileObj.close()


'''
    命令处理类
    负责命令的参数验证、
        获取操作文件列表、
        得到输出文件、
        各项数据统计
'''
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
        tag = True
        if not os.path.exists(self.logPath):
            tag=False

        for item in self.provinceList:
            if item not in ProvinceList:
                tag=False

        for item in self.infectTypeList:
            if item not in InfectTypeList:
                tag=False

        if self.date:
            fileList=os.listdir(self.logPath)
            for file in fileList:
               date1=file.split(".")[0]
               if not dateCompare(date1,self.date):
                   tag=False
        return tag

    def getOutputFile(self):
        foperator=FileOperator(self.outPath)
        staticList=self.getStaticList()
        if len(self.provinceList)!=0:
            for p in self.provinceList:
                line=p+' '
                for t in self.infectTypeList:
                    line=line+InfectTypeListCN[InfectTypeList.index(t)]+" "+str(staticList[InfectTypeList.index(t)][ProvinceList.index(p)])+'人 '
                foperator.writeLine(line)
        else:
            for p in ProvinceList:
                line=p,' '
                count=0
                for t in self.infectTypeList:
                    count+=staticList[InfectTypeList.index(t)][ProvinceList.index(p)]
                if count!=0:
                    for t in self.infectTypeList:
                        line = line,InfectTypeListCN[InfectTypeList.index(t)],staticList[InfectTypeList.index(t)][ProvinceList.index(p)],'人 '
                    foperator.writeLine(line)
        foperator.close()

    def getStaticList(self):
        list = [[0 for i in range(len(ProvinceList))] for j in range(len(InfectTypeList))]
        fileList=self.getFileList()
        for file in fileList:
            foperator=FileOperator(self.logPath+"\\"+file)
            line=foperator.readLine()
            while line:
                for p in ProvinceList:
                    obj=re.match(p+" 新增 (.+) (\\d+)人",line)
                    if obj:
                        if obj.group(1) in InfectTypeListCN:
                            list[InfectTypeListCN.index(obj.group(1))][ProvinceList.index(p)]+=int(obj.group(2))
                    obj=re.match(p+" (.+) 流入 (.+) (\\d+)人",line)
                    if obj:
                        if obj.group(1) in InfectTypeListCN and obj.group(2) in ProvinceList:
                            list[InfectTypeListCN.index(obj.group(1))][ProvinceList.index(p)]-=int(obj.group(3))
                            list[InfectTypeListCN.index(obj.group(1))][ProvinceList.index(obj.group(2))]+=int(obj.group(3))
                    obj=re.match(p+" 死亡 (\\d+)人",line)
                    if obj:
                        list[InfectTypeList.index("ip")][ProvinceList.index(p)]-=int(obj.group(1))
                        list[InfectTypeList.index("dead")][ProvinceList.index(p)]+=int(obj.group(1))
                    obj=re.match(p+" 治愈 (\\d+)人",line)
                    if obj:
                        list[InfectTypeList.index("ip")][ProvinceList.index(p)]-=int(obj.group(1))
                        list[InfectTypeList.index("cure")][ProvinceList.index(p)]+=int(obj.group(1))
                        #print(list[InfectTypeList.index("ip")][ProvinceList.index(p)])
                    obj=re.match(p+" .+ 确诊感染 (\\d+)人",line)
                    if obj:
                        list[InfectTypeList.index("sp")][ProvinceList.index(p)]-=int(obj.group(1))
                        list[InfectTypeList.index("ip")][ProvinceList.index(p)]+=int(obj.group(1))
                    obj=re.match(p+" 排除 .+ (\\d+)人",line)
                    if obj:
                        list[InfectTypeList.index("sp")][ProvinceList.index(p)]-=int(obj.group(1))
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
    return time1>time2
    

if sys.argv[1]!='list':
    print('Command Error')
    exit(1)

logPath=findInformation('-log')
outPath=findInformation('-out')
provinceList=findInformation('-province')
infectTypeList=findInformation('-type')
dateList=findInformation('-date')

if len(logPath)==0 or len(outPath)==0:
    print('Command Error!')
    exit(1)
#print(logPath[0])

if len(dateList)==0:
    command=CommandHandler(logPath[0],outPath[0],provinceList,infectTypeList,None)
else:
    command=CommandHandler(logPath[0],outPath[0],provinceList,infectTypeList,dateList[0])

if not command.isArgsRightful():
    print('Args Error!')
    exit(2)

command.getOutputFile()