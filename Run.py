#!/bin/env python3

import pretty_errors
import PIL
from PIL import Image
from colorama import init, Fore
from pathlib import Path
import subprocess
import shutil
import random
import errno
import math
import uuid
import sys
import os
import re

init(autoreset=True)
os.system('mode con cols=85 lines=45')

def initScript(argv0):
    print(Fore.GREEN + '正在初始化...\n')

    workDir = {}

    scriptPath = os.path.dirname(argv0)
    scriptFullPath = os.path.abspath(scriptPath)

    print(Fore.CYAN + '脚本路径:' + Fore.RESET, scriptFullPath, '\n')

    workDir['imageMagickPath'] = os.path.join(scriptFullPath, 'imagemagick')
    workDir['inputPath'] = os.path.join(scriptFullPath, 'input_imgs')
    workDir['outputPath'] = os.path.join(scriptFullPath, 'output_imgs')
    workDir['tempPath'] = os.path.join(scriptFullPath, 'temp')

    # 检查 input_imgs 是否存在
    try:
        print(Fore.CYAN + '正在定位输入文件夹...\n')
        os.makedirs(workDir['inputPath'])
        print(Fore.RED + '输入文件夹 input_imgs 不存在，正在创建...\n')
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise
        else:
            print(Fore.CYAN + '输入文件夹为:' + Fore.RESET, 'input_imgs ...\n')

    # 检查 output_imgs 是否存在
    try:
        print(Fore.CYAN + '正在定位输出文件夹...\n')
        os.makedirs(workDir['outputPath'])
        print(Fore.RED + '输出文件夹 output_imgs 不存在，正在创建...\n')
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise
        else:
            print(Fore.CYAN + '输出文件夹为:' + Fore.RESET, 'output_imgs ...\n')

    # 检查 temp 是否存在
    try:
        print(Fore.CYAN + '正在定位临时文件夹...\n')
        os.makedirs(workDir['tempPath'])
        print(Fore.RED + '临时文件夹 temp 不存在，正在创建...\n')
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise
        else:
            print(Fore.CYAN + '临时文件夹为:' + Fore.RESET, 'temp ...\n')
    
    return(workDir)    # dict

def initImageMagick(workDirDict):
    magickCmd = {}

    magickCmd['magick'] = os.path.join(workDir['imageMagickPath'], 'magick.exe')
    magickCmd['convert'] = os.path.join(workDir['imageMagickPath'],  'convert.exe')
    
    try:
        exeFile = Path(magickCmd['magick'])
        exeExists = exeFile.resolve(strict = True)
    except FileNotFoundError:
        print(Fore.RED + '错误:' + Fore.RESET, 'ImageMagick 不存在\n')
        print(Fore.YELLOW + '请参考: ' + Fore.RESET, 'https://github.com/chinanoahli/Ero_Img_Blender/tree/main/imagemagick\n')
        input('按 Enter 退出程序 ...')
        sys.exit(-1)
    else:
        print(Fore.CYAN + '已找到' + Fore.RESET, 'ImageMagick ...\n')

    magickCmd['magick'] = '"' + magickCmd['magick'] + '"' 
    magickCmd['convert'] = '"' + magickCmd['convert'] + '"' 

    magickCmd['appendToBottom'] = magickCmd['convert'] + ' -append <SOURCESLIST> <OUTPUTFULLPATH>'
    magickCmd['appendToRight'] = magickCmd['convert'] + ' +append <SOURCESLIST> <OUTPUTFULLPATH>'
    magickCmd['cropImg'] = magickCmd['convert'] + ' "<INPUTFULLPATH>" -crop <PART>x<PART>@ +repage +adjoin "<OUTPUTFILENAME>.%d.<FORMAT>"'
    magickCmd['extentImg'] = magickCmd['magick'] + ' "<INPUTFULLPATH>" -background black -extent <HIGH>x<WIDTH> "<OUTPUTFULLPATH>"'
    magickCmd['getHigh'] = magickCmd['magick'] + ' identify -format "%h" "<INPUTFULLPATH>"'
    magickCmd['getWidth'] = magickCmd['magick'] + ' identify -format "%w" "<INPUTFULLPATH>"'

    return(magickCmd)    # dict

def sequenceGenerator(parts):
    totalParts = parts * parts
    sequence = []

    for count in range(0, totalParts):
        sequence.append(str(count))

    random.shuffle(sequence)

    return(sequence)    # str in list

def magickExecutor(magickCmd, command, mode=None, imgFullPath = None, part = None, format = None, width = None, high = None, outputFullPath = None, imgInfoDict = None, fileListStr = None, debug=None):
    # command:
    # 1. appendToBottom    fileListStr outputFullPath
    # 2. appendToRight     fileListStr outputFullPath
    # 3. cropImg           imgFullPath outputFullPath part imgInfoDict
    # 4. extentImg         imgFullPath outputFullPath mode width high 
    # 5. getHigh           imgFullPath
    # 6. getWidth          imgFullPath
    #
    # *. debug = 'debug' 就会输出所有执行的命令

    if command == 'appendToBottom':
        cmd = magickCmd['appendToBottom'].replace('<SOURCESLIST>', fileListStr)
        cmd = cmd.replace('<OUTPUTFULLPATH>', '"' + outputFullPath + '"')

        if debug == 'debug':
            print(Fore.RED + 'magickExecutor appendToBottom:' + Fore.RESET, cmd)

        cmdReturn = os.popen(cmd).read()
        if cmdReturn not in ('', None):
            return(cmdReturn)

    elif command == 'appendToRight':
        cmd = magickCmd['appendToRight'].replace('<SOURCESLIST>', fileListStr)
        cmd = cmd.replace('<OUTPUTFULLPATH>', '"' + outputFullPath + '"')

        cmdReturn = os.popen(cmd).read()
        if cmdReturn not in ('', None):
            return(cmdReturn)

    elif command == 'cropImg':
        print(Fore.CYAN + '正在将图片拆分为:' + Fore.RESET, part, 'x', part)
        cmd = magickCmd[command].replace('<INPUTFULLPATH>', imgFullPath)
        cmd = cmd.replace('<PART>', str(part))
        cmd = cmd.replace('<OUTPUTFILENAME>', outputFullPath)
        cmd = cmd.replace('<FORMAT>', imgInfoDict['imgFormat'])

        cmdReturn = os.popen(cmd).read()
        return(cmdReturn)

    elif command == 'extentImg':
        if mode == 'encrypt':
            print(Fore.CYAN + '正在将图片扩展到:' + Fore.RESET, width, 'x', high)
        if mode == 'decrypt':
            print(Fore.CYAN + '正在将图片裁剪到:' + Fore.RESET, width, 'x', high)

        cmd = magickCmd[command].replace('<INPUTFULLPATH>', imgFullPath)
        cmd = cmd.replace('<WIDTH>', str(width))
        cmd = cmd.replace('<HIGH>', str(high))
        cmd = cmd.replace('<OUTPUTFULLPATH>', outputFullPath)

        cmdReturn = os.popen(cmd).read()
        return(cmdReturn)

    elif command == 'getHigh':
        cmd = magickCmd[command].replace('<INPUTFULLPATH>', imgFullPath)
        cmdReturn = os.popen(cmd).read()

        return cmdReturn

    elif command == 'getWidth':
        cmd = magickCmd[command].replace('<INPUTFULLPATH>', imgFullPath)
        cmdReturn = os.popen(cmd).read()

        return cmdReturn

def combineImg(mode, passwordB, passwordR, magickCmd, sequence, part, workDir, imgInfoDict):
    password = ''
    password = password + 'R' + str(passwordR) + '.'
    password = password + 'B' + str(passwordB) + '.'

    sequenceStr = ''

    for numStr in sequence:
        password = password + numStr + '.'
        sequenceStr = sequenceStr + numStr + '.'

    password = password[0: -1]
    print(Fore.CYAN + '正在以序列:' + Fore.RESET, sequenceStr[0: -1], '重组图片 ...')

    fileList = []
    sequenceCounter = 0
    for line in range(0, part):
        fileInLine = []
        for column in range(0,part):
            fileName = ''
            if mode == 'encrypt':
                fileName = imgInfoDict['imgNameWithoutExtname'] + '.' + sequence[sequenceCounter] + '.' + imgInfoDict['imgFormat']
            if mode == 'decrypt':
                fileName = imgInfoDict['newNameWithoutExtname'] + '.' + sequence[sequenceCounter] + '.' + imgInfoDict['imgFormat']
            sequenceCounter = sequenceCounter + 1
            fileInLine.append(fileName)
        fileList.append(fileInLine)

    lineCounter = 0
    for line in fileList:
        lineStr = ''
        for column in line:
            lineStr = lineStr + '"' + os.path.join(workDir['tempPath'], column) + '" '
        if mode == 'encrypt':
            fileName = imgInfoDict['imgNameWithoutExtname'] + '.line' + str(lineCounter) + '.' + imgInfoDict['imgFormat']
        if mode == 'decrypt':
            fileName = imgInfoDict['newNameWithoutExtname'] + '.line' + str(lineCounter) + '.' + imgInfoDict['imgFormat']
        outputFullPath = os.path.join(workDir['tempPath'], fileName)

        cmdReturn = magickExecutor(magickCmd, 'appendToRight', fileListStr = lineStr, outputFullPath = outputFullPath, debug = debugFlag)

        if cmdReturn not in ('', None):
            print('func combineImg appendToRight:', cmdReturn)

        lineCounter = lineCounter + 1

    lineList = []
    for line in range(0, part):
        if mode == 'encrypt':
            fileName = imgInfoDict['imgNameWithoutExtname'] + '.line' + str(line) + '.' + imgInfoDict['imgFormat']
        if mode == 'decrypt':
            fileName = imgInfoDict['newNameWithoutExtname'] + '.line' + str(line) + '.' + imgInfoDict['imgFormat']

        fileFullName = os.path.join(workDir['tempPath'], fileName)
        lineList.append(fileFullName)

    lineStr = ''
    for line in lineList:
        lineStr = lineStr + '"' + line + '" '

    if mode == 'encrypt':
        fileName = imgInfoDict['imgNameWithoutExtname'] + '.' + password + '.' + imgInfoDict['imgFormat']
        outputFullPath = os.path.join(workDir['outputPath'], fileName)
    if mode == 'decrypt':
        fileName = imgInfoDict['newNameWithoutExtname'] + '.Extented.' + imgInfoDict['imgFormat']
        outputFullPath = os.path.join(workDir['tempPath'], fileName)

    cmdReturn = magickExecutor(magickCmd, 'appendToBottom', fileListStr = lineStr, outputFullPath = outputFullPath, debug = debugFlag)
    if cmdReturn not in ('', None):
        print('func combineImg appendToBottom:', cmdReturn)

    return password

def getEncryptStatus(fileName):
    regEx = re.compile(r'R[0-9]\.B[0-9]\.(([0-9]{0,2}\.){9,25})')
    search = regEx.search(fileName)

    if search is not None:
        password = search.group(0)[0:-1]
        return(True, password)
    else:
        return(False, None)

def getImgInfo(imgFullName, inputPath, magickCmd):
    info = {}

    imgPath = os.path.join(inputPath, imgFullName) 
    try:
        imgFormat = Image.open(imgPath).format

        if imgFormat in ('BMP', 'JPEG', 'JPG', 'PNG'):
            originWidth = magickExecutor(magickCmd, 'getHigh', imgFullPath = imgPath, debug = debugFlag)
            originHigh = magickExecutor(magickCmd,'getWidth', imgFullPath = imgPath, debug = debugFlag)

            info['imgFullName'] = imgFullName
            info['width'] = int(originWidth)
            info['high']  = int(originHigh)
            info['imgNameWithoutExtname'] = ''

            imgNameSplit = imgFullName.split('.')
            info['imgFormat'] = imgNameSplit[len(imgNameSplit) - 1]

            for i in range(0, len(imgNameSplit) - 1):
                info['imgNameWithoutExtname'] = info['imgNameWithoutExtname'] + imgNameSplit[i] + '.'

            if info['imgNameWithoutExtname'][-1] == '.':
                info['imgNameWithoutExtname'] = info['imgNameWithoutExtname'][0: -1]
            
            info['encrypted'] = None
            info['password'] = None

            result = getEncryptStatus(info['imgFullName'])

            if result[0] == True:
                info['encrypted'] = result[0]
                info['password'] = result[1]
            else:
                info['encrypted'] = result[0]

            return(info)    # dicts

        else:
            return None

    except PIL.UnidentifiedImageError:
        return None

def getExtentSize(picDict, part):
    widthModable = picDict['width'] % part
    widthDevPart = picDict['width'] // part
    highModable = picDict['high'] % part
    highDevPart = picDict['high'] // part
    newWidth = picDict['width']
    newHigh = picDict['high']

    if widthModable != 0:
        newWidth = widthDevPart * part + part
    
    if highModable != 0:
        newHigh = highDevPart * part + part

    extentedSize = {}
    extentedSize['width'] = newWidth
    extentedSize['high'] = newHigh

    return extentedSize    # dict

def listImgsAtInputPath(inputPath, magickCmd):
    fileList = os.listdir(inputPath)

    if len(fileList) == 0:
        print(Fore.RED + '\n错误:' + Fore.RESET ,'输入文件夹无文件!\n      请将要处理的图片放入', Fore.YELLOW + inputPath + Fore.RESET, ', 然后再运行本脚本!\n')
        input('按 Enter 退出程序 ...')
        sys.exit(-1)

    picsList = []
    
    for fileName in os.listdir(inputPath):
        info = getImgInfo(fileName, inputPath, magickCmd)
        if info != None:
            picsList.append(info)

    if len(picsList) == 0:
        print(Fore.RED + '\n错误:' + Fore.RESET ,'输入文件夹不包含有效的图片文件!\n      请将要处理的图片放入', Fore.YELLOW + inputPath + Fore.RESET, ', 然后再运行本脚本!\n')
        input('按 Enter 退出程序 ...')
        sys.exit(-1)

    return(picsList)    # dict in list

def decryptImg(mode, passwordStr, workDir, imgInfoDict, magickCmd):
    # 将密码字符串转换为列表, 通过密码长度计算拆分数量
    passwordList = passwordStr.split('.')
    allParts = len(passwordList) - 2
    splitPart = int(math.sqrt(allParts))
    totalParts = splitPart * splitPart

    # 拆分图片
    imgFullPath = os.path.join(workDir['inputPath'], imgInfoDict['imgFullName'])
    outputFullPath = os.path.join(workDir['tempPath'], imgInfoDict['newNameWithoutExtname'])
    cmdReturn = magickExecutor(magickCmd, 'cropImg', imgFullPath = imgFullPath, outputFullPath = outputFullPath, part = splitPart, imgInfoDict = imgInfoDict, debug = debugFlag)
    if cmdReturn not in ('', None):
        print('func decryptImg corpImg:', cmdReturn)
    
    # 重建正确的恢复序列
    restoreSequence = []         # 恢复序列
    passwordNumsSequence = []    # 密码序列

    # 将密码中的数字单独提取到一个列表中
    for password in passwordList:
        if password.isdigit():
            passwordNumsSequence.append(password)
    
    # 循环 totalParts 次, 即密码的总长度, 如 0~9 0~16 0~25
    for sequenceCounter in range(0, totalParts):
        # 标志数是遍历密码序列时的标记, 如标志数为 2 , 则标示已经遍历到密码序列中第三个密码
        passwordCounter = 0
        # 遍历密码序列
        for password in passwordNumsSequence:
            if password != str(sequenceCounter):
                # 如果在密码序列中, 当前位密码与最外层循环次数不相等, 就将标志数+1
                passwordCounter += 1
            else:
                # 如果在密码序列中, 当前位密码与最外层循环次数相等, 标志数所标示的位置即是正确的顺序, 将标志数存到恢复序列, 并将标志数清零
                restoreSequence.append(str(passwordCounter))
                passwordCounter = 0

    # 重组图片
    restorePic = combineImg('decrypt', passwordB = passwordList[1], passwordR = passwordList[0], magickCmd = magickCmd, sequence = restoreSequence, part = splitPart, workDir = workDir, imgInfoDict = imgInfoDict)

    # 去除扩展的黑边
    realWidth = imgInfoDict['width'] - int(passwordList[0][-1])
    realHigh = imgInfoDict['high'] - int(passwordList[1][-1])

    imgFullPath = os.path.join(workDir['tempPath'], imgInfoDict['newNameWithoutExtname'] + '.Extented.' + imgInfoDict['imgFormat'])
    outputFullPath = os.path.join(workDir['outputPath'], imgInfoDict['newNameWithoutExtname'] + '.Decrypt.' + imgInfoDict['imgFormat'])

    cmdReturn = magickExecutor(magickCmd, 'extentImg', mode = 'decrypt', imgFullPath = imgFullPath, outputFullPath = outputFullPath, width = realWidth, high = realHigh, debug = debugFlag)
    if cmdReturn not in ('', None):
        print('func decryptImg extentImg:', cmdReturn)

    print(Fore.CYAN + '新文件名为:' + Fore.RESET, imgInfoDict['newFullName'], '...\n')

while True:
    print('                ┌────────────────────────────────────────────────┐')
    print('                ┃                   ' + Fore.YELLOW + '色图混淆器' + Fore.RESET + ' v 1.0             ┃')
    print('                ┃                                 by: ' + Fore.CYAN + 'chinanoahli' + Fore.RESET + '┃')
    print('                ┃                                                ┃')
    print('                ┃', Fore.YELLOW + '本工具支持的图片格式:' + Fore.RESET, '*.jpg', '*.jpeg', '*.png', '*.bmp ┃')
    print('                └────────────────────────────────────────────────┘\n')

    if len(sys.argv) > 1:
        if sys.argv[1] == 'debug':
            debugFlag = sys.argv[1]
    else:
        debugFlag = None
    
    workDir = initScript(sys.argv[0])
    magickCmd = initImageMagick(workDir['imageMagickPath'])
        
    print(Fore.CYAN + '正在扫描输入文件夹 ...')
    imgsList = listImgsAtInputPath(workDir['inputPath'], magickCmd)
    print('扫描完成, 输入文件夹包含', Fore.YELLOW + str(len(imgsList)) + Fore.RESET, '个图片文件\n')

    print(Fore.YELLOW + '请选择需要的操作:')
    print(Fore.CYAN + '1.' + Fore.RESET, '我要开车')
    print('   混淆图片, 批量处理所有图片')
    print('   文件名带有色图密码的图片将会被跳过\n')
    print(Fore.CYAN + '2.' + Fore.RESET, '我要开冲')
    print('   还原图片, 输入文件夹里的图片文件名如果' + Fore.RED + '包含' + Fore.RESET + '色图密码则可以自动批量还原')
    print('   否则，请选择手动还原模式，并根据提示输入色图密码\n')
    print(Fore.CYAN + '3.' + Fore.RESET, '查看图片文件列表\n')

    print('输入', Fore.CYAN + '序号' + Fore.RESET, '并按 Enter 开始选择的操作, 输入', Fore.RED + 'x / q' + Fore.RESET, '以退出脚本: ', end = '')
    mainMenuSelected = input()

    # 混淆图片
    if mainMenuSelected == '1':

        # 选择混淆等级
        while True:
            print(Fore.YELLOW + '\n混淆等级:')
            print(Fore.CYAN + '1.' + Fore.RESET, '把所有输入的图片拆分成 3x3 等分, 然后重新组合出新图片')
            print(Fore.CYAN + '2.' + Fore.RESET, '把所有输入的图片拆分成 4x4 等分, 然后重新组合出新图片')
            print(Fore.CYAN + '3.' + Fore.RESET, '把所有输入的图片拆分成 5x5 等分, 然后重新组合出新图片\n')

            splitPartSelected = input('请选择混淆等级: ')
            print('\n')

            if splitPartSelected == '1':
                splitPart = 3
                break
            elif splitPartSelected == '2':
                splitPart = 4
                break
            elif splitPartSelected == '3':
                splitPart = 5
                break
            else:
                print(Fore.RED + '错误:' + Fore.RESET, '输入错误, 请重新输入!\n')

        sequence = sequenceGenerator(splitPart)

        print(Fore.YELLOW + '开始重组图片:')

        for img in imgsList:
            if img['encrypted'] == False:
                print(Fore.CYAN + '正在处理:' + Fore.RESET, img['imgFullName'], '...')
                fullImgPath = os.path.join(workDir['inputPath'], img['imgFullName'])

                # 扩展图片分辨率
                extentedSize = getExtentSize(img, splitPart)
                outputFullPath = os.path.join(workDir['tempPath'], img['imgFullName'])
                cmdReturn = magickExecutor(magickCmd, 'extentImg', mode = 'encrypt', imgFullPath = fullImgPath, outputFullPath = outputFullPath, width = extentedSize['width'], high = extentedSize['high'], debug = debugFlag)
                if cmdReturn not in ('', None):
                    print('main encrypt extentImg:', cmdReturn)

                passwordR = extentedSize['width'] - img['width']
                passwordB = extentedSize['high'] - img['high']

                # 拆分图片
                extentedFileName = img['imgNameWithoutExtname']
                imgFullPath = os.path.join(workDir['tempPath'], img['imgFullName'])
                outputFullPath = os.path.join(workDir['tempPath'], extentedFileName)
                cmdReturn = magickExecutor(magickCmd, 'cropImg', imgFullPath = imgFullPath, outputFullPath = outputFullPath, part = splitPart, imgInfoDict = img, debug = debugFlag)
                if cmdReturn not in ('', None):
                    print('main encrypt cropImg:', cmdReturn)

                # 重组图片
                password = combineImg('encrypt', passwordB, passwordR, magickCmd, sequence, splitPart, workDir, img)
                print(Fore.RED + '色图密码为:', Fore.YELLOW + password, '\n')

        print(Fore.GREEN + '图片处理完成, 已输出到', Fore.YELLOW + workDir['outputPath'])
        print('图片文件名包含' + Fore.RED + '色图密码' + Fore.RESET + ', 分享图片时请记得把色图密码也一同分享!\n')

        print(Fore.YELLOW + '正在清理临时文件...\n')
        shutil.rmtree(workDir['tempPath'])

        input('按 Enter 继续...')
        os.system('cls')

    # 还原图片
    elif mainMenuSelected == '2':
        while True:
            print(Fore.YELLOW + '请选择还原模式:')
            print(Fore.CYAN + '1.' + Fore.RESET, '自动还原')
            print('   自动还原所有输入文件夹中' + Fore.RED + '文件名带有色图密码' + Fore.RESET + '的图片\n')
            print(Fore.CYAN + '2.' + Fore.RESET, '手动还原')
            print('   从列表中选择需要还原的图片, 然后' + Fore.RED + '手动输入色图密码' + Fore.RESET + '以还原图片')
            print('   需要先将图片放到' + Fore.RED + '输入文件夹\n')
            print('输入', Fore.CYAN + '序号' + Fore.RESET, '并按 Enter 以开始还原: ', end='')

            restoreMenuSelected = input()
            print('\n')
            
            # 自动还原
            if restoreMenuSelected == '1':
                print(Fore.YELLOW + '开始处理图片:')
                for img in imgsList:
                    if img['encrypted'] == True:
                        print(Fore.CYAN + '正在处理:' + Fore.RESET, img['imgFullName'], '...')
                        print(Fore.CYAN + '色图密码:' + Fore.RESET, img['password'])
                        # 从旧文件名里去掉密码, 如果去掉后为空, 就生成一个UUID作为新文件名
                        if img['imgNameWithoutExtname'].replace(img['password'], '') == '':
                            newName = str(uuid.uuid4())
                            img['newNameWithoutExtname'] = newName
                            img['newFullName'] = newName + '.' + img['imgFormat']
                        else:
                            img['newNameWithoutExtname'] = img['imgNameWithoutExtname'].replace(img['password'], '')[0: -1]
                            img['newFullName'] = img['imgFullName'].replace(img['password'] + '.', '')

                        decryptImg('decypt', passwordStr = img['password'], workDir = workDir, imgInfoDict = img, magickCmd = magickCmd)

                print(Fore.GREEN + '图片处理完成, 已输出到', Fore.YELLOW + workDir['outputPath'])

                print(Fore.YELLOW + '正在清理临时文件...\n')
                shutil.rmtree(workDir['tempPath'])

                input('按 Enter 继续...')
                os.system('cls')
                break

            # 手动还原
            elif restoreMenuSelected == '2':
                print('输入文件夹包含下列文件:\n')

                fileCounter = 0
                for img in imgsList:
                    print(Fore.CYAN + '图片序号:' + Fore.RESET, fileCounter)
                    print(Fore.CYAN + '图片名称:' + Fore.RESET, img['imgNameWithoutExtname'])
                    print(Fore.CYAN + '图片格式:' + Fore.RESET, img['imgFormat'])
                    print(Fore.CYAN + '图片宽度:' + Fore.RESET, img['width'])
                    print(Fore.CYAN + '图片高度:' + Fore.RESET, img['high'])
                    if img['encrypted'] == True:
                        print(Fore.CYAN + '是否加密:', Fore.RED + '是')
                        print(Fore.CYAN + '色图密码:' + Fore.RESET, img['password'], '\n')
                    else:
                        print(Fore.CYAN + '是否加密:' + Fore.RESET, '未知', '\n')
                    fileCounter = fileCounter + 1

                print(Fore.YELLOW + '请选选择需要还原的图片序号: ', end = '')
                restoreSelected = input()

                if restoreSelected.isdigit() == False and int(restoreSelected) > len(imgsList):
                    print(Fore.RED + '错误:' + Fore.RESET, '色图序号无法识别, 请重试!\n')
                    input('按 Enter 继续...\n')
                    continue
                
                print(Fore.YELLOW + '请输入色图密码 (复制密码后, 在本窗口单击鼠标右键即可粘贴): ', end = '')
                password = input()

                regEx = re.compile(r'R[0-9]\.B[0-9]\.(([0-9]{0,2}\.){9,25})')
                search = regEx.search(password + '.')
                if search is None:
                    print(Fore.RED + '错误:' + Fore.RESET, '色图密码无法识别, 请重试!\n')
                    input('按 Enter 继续...\n')
                    continue

                imgInfoDict = imgsList[int(restoreSelected)]
                imgInfoDict['encrypted'] = True
                imgInfoDict['password'] = password
                imgInfoDict['newNameWithoutExtname'] = imgInfoDict['imgNameWithoutExtname']
                imgInfoDict['newFullName'] = imgInfoDict['imgFullName']

                decryptImg('decypt', passwordStr = password, workDir = workDir, imgInfoDict = imgInfoDict, magickCmd = magickCmd)

                print(Fore.GREEN + '图片处理完成, 已输出到', Fore.YELLOW + workDir['outputPath'])

                print(Fore.YELLOW + '正在清理临时文件...\n')
                shutil.rmtree(workDir['tempPath'])

                input('按 Enter 继续...')
                os.system('cls')
                break

            # 输入错误
            else:
                print(Fore.RED + '错误:' + Fore.RESET, '输入错误, 请重新输入!\n')

    # 查看文件列表
    elif mainMenuSelected == '3':
        print('输入文件夹包含下列文件:\n')
        
        fileCounter = 0
        for img in imgsList:
            print(Fore.CYAN + '图片序号:' + Fore.RESET, fileCounter)
            print(Fore.CYAN + '图片名称:' + Fore.RESET, img['imgNameWithoutExtname'])
            print(Fore.CYAN + '图片格式:' + Fore.RESET, img['imgFormat'])
            print(Fore.CYAN + '图片宽度:' + Fore.RESET, img['width'])
            print(Fore.CYAN + '图片高度:' + Fore.RESET, img['high'])
            if img['encrypted'] == True:
                print(Fore.CYAN + '是否加密:', Fore.RED + '是')
                print(Fore.CYAN + '色图密码:' + Fore.RESET, img['password'], '\n')
            else:
                print(Fore.CYAN + '是否加密:' + Fore.RESET, '否', '\n')
            fileCounter = fileCounter + 1

        input('按 Enter 继续...')
        os.system('cls')

    elif mainMenuSelected in ('x', 'X', 'q', 'Q'):
        break
    else:
        print(Fore.RED + '错误:' + Fore.RESET, '输入错误, 请重按 Enter 新输入!\n', end='')
        input()
        os.system('cls')

print('已退出!\n')