import random


if __name__=='__main__':
    path1='./files/199801_seg&pos.txt'
    path2='./files/199802.txt'
    path3 = './files/199803.txt'
    path4='./files/trainingdata.txt'
    file1=open(path1,'r',encoding='GBK')
    file2 = open(path2, 'r', encoding='GBK')
    file3 = open(path3, 'r', encoding='GBK')
    file4 = open(path4, 'w', encoding='GBK')
    read1=file1.readlines()
    read2 = file2.readlines()
    read3 = file3.readlines()
    for row in read1:
        rand=random.randint(1,10)
        if rand>3:
            file4.write(row)
    for row in read2:
        rand=random.randint(1,10)
        if rand>3:
            file4.write(row)
    for row in read3:
        rand=random.randint(1,10)
        if rand>3:
            file4.write(row)
    file1.close()
    file2.close()
    file3.close()
    file4.close()