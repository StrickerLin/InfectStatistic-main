import sys
import Lib


if __name__=="__main__":
    if sys.argv[1]!='list':
        print('Command Error')
        exit(1)

    #获取参数
    logPath=Lib.findInformation('-log')
    outPath=Lib.findInformation('-out')
    provinceList=Lib.findInformation('-province')
    infectTypeList=Lib.findInformation('-type')
    dateList=Lib.findInformation('-date')


    if len(logPath)!=0 or len(outPath)!=0:
        print('Command Error!')
        exit(1)

    #生成命令对象
    if len(dateList)==0:
        command=Lib.CommandHandler(logPath[0],outPath[0],provinceList,
                                   infectTypeList,None)
    else:
        command=Lib.CommandHandler(logPath[0],outPath[0],provinceList,
                                   infectTypeList,dateList[0])

    #检验参数合法性
    if not command.isArgsRightful():
        print('Args Error!')
        exit(2)

    #得到输出文件
    command.getOutputFile()