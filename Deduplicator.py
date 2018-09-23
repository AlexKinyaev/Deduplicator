
import sys
import os
import signal
import hashlib
from collections import defaultdict
from functools import partial

DataBaseBySize = defaultdict(list)
DataBaseByMd5 = defaultdict(list)

FolderPath = ''
ReportFile = 'duplicate_report.txt'

ProgressCount = 0

def Progress(Mess):

    global ProgressCount

    prog_list = ["-","\\","|","/"]

    print('\r',prog_list[ProgressCount%4], Mess, "   ", end='')

    ProgressCount+=1


def CreateReport(ReportFile):

    global DataBaseByMd5

    print('\rCreating a report with duplicate files: %s' % (ReportFile), '\n    Please wait...\n')

    f = open(ReportFile, "w+")

    for Md5Key, ListOfDuplicates in DataBaseByMd5.items():

        f.write("\n" + Md5Key + "\n")

        for Duplicate in ListOfDuplicates:
            Progress(os.path.basename(Duplicate))       
            f.write("+ " + Duplicate + "\n")

    f.close()

    print('\rThe Report:%s has been created succesfully.    \n' % (ReportFile))

    return



def signal_handler(sig, frame):

    print('You have cancelled the process.')
    CreateReport(ReportFile)

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def CalcMd5(FilePath):

    with open(FilePath, mode='rb') as f:

        Md5Hash = hashlib.md5()

        for Buffer in iter(partial(f.read, 10485760), b''):
            Progress("Calculating md5:" + os.path.basename(FilePath))
            Md5Hash.update(Buffer)

    return Md5Hash.hexdigest()


def FindDuplicator(FilePath):

    global DataBaseByMd5
    global DataBaseBySize

    Progress("Checking:" + os.path.basename(FilePath))

    FileSize = os.stat(FilePath).st_size

    if not len(DataBaseBySize[FileSize]):
        NewItems = [FilePath, '']
        DataBaseBySize[FileSize].append(NewItems)
        return

    NewItems = [FilePath, CalcMd5(FilePath)]

    for Index, Item in enumerate(DataBaseBySize[FileSize]):
        
        Items = None

        if Item[1] == '':
            Items = [Item[0], CalcMd5(FilePath)]
            DataBaseBySize[FileSize] = [Items]
            DataBaseByMd5[Items[1]].append(Items[0])

        else:
            Items = Item

        if Items[1] == NewItems[1]:
            DataBaseByMd5[NewItems[1]].append(NewItems[0])

    DataBaseBySize[FileSize].append(NewItems)

    return


def GetContentOfDirectory(FolderPath):

    for SubFolderPath in os.listdir(FolderPath):

        ItemPath = os.path.join(FolderPath, SubFolderPath)

        if os.path.isdir(ItemPath):
            GetContentOfDirectory(ItemPath)

        elif os.path.isfile(ItemPath):
            FindDuplicator(ItemPath)

        else:
            #print("This is a special file:", Path + item)
            pass


def CheckArguments():

    global FolderPath
    global ReportFile
    
    #ListArgv = ["Dedublecator.py", "F:\ApiMon"]

    ListArgv = sys.argv

    if len(ListArgv) < 2:
        print('Deduplicator.py <Path to the Folder>')
        sys.exit(2)

    try:
        FolderPath = os.path.join(FolderPath, ListArgv[1])
    except:
        print("The Path is not correct: %s" % (FolderPath))
        return False

    if not os.path.exists(FolderPath):
        print("The Folder does not exist: %s" % (FolderPath))
        return False

    ReportFile = os.path.join(FolderPath, ReportFile)

    print("Finding duplications in the Folder: %s" % (FolderPath))
    print("You can interrupt this Process press 'CTRL+C'")

    return True


def main():


    if not CheckArguments():
        return

    GetContentOfDirectory(FolderPath)

    CreateReport(ReportFile)


if __name__ == "__main__":
    main()


