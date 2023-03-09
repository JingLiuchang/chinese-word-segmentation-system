# -*- coding:gbk -*-
import re

def contains_chinese(strs):
    for char in strs:
        if '\u4e00' <= char <= '\u9fa5':
            return True
    return False

def regularfilter(strs):
    flag=0
    for char in strs:
        if '\u4e00' <= char <= '\u9fa5':
            flag=1#至少有一个汉字
    if flag==0:
        return False
    # 数字+一个汉字
    prog1 = '[０-９]{1,}[^\x00-\xff]'
    num1 = re.findall(prog1, strs)

    if len(num1)>0 :
        return False
    elif len(num1)==0 and flag==1:
        return True

def generate_dict3(input_path):
    flag = 0
    begin = 0
    end = 0
    wordlist = []
    MAX=11
    maxlength=0
    f = open('./files/dic3.txt', 'w', encoding='GBK')
    with open(input_path, 'r') as file:
        reader = file.readlines()
        j = 0
        for row in reader:
            j += 1
            print(j)
            if len(row) == 1 or j<=2300:#空
                continue
            else:#后90%
                for i in range(len(row)):
                    if row[i] == ' ' and flag == 0:
                        flag = 1
                    if row[i] == ' ' and flag == 1:
                        flag = 0
                        begin = i + 1#找到开始
                    if row[i] == '/':
                        end = i#找到结束
                    if begin and end:
                        word = row[begin:end]
                        begin = 0
                        end = 0
                        if len(word) and contains_chinese(word):
                            if word not in wordlist and len(word) < MAX:
                                if len(word)>maxlength:
                                    maxlength=len(word)
                                wordlist.append(word)
                                f.write(word+'\n')
        f.write(str(maxlength)+'\n')
        f.close()
def load_dict3(dict_path):
    dictaslist=[]
    with open(dict_path, 'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            dictaslist.append(row[0:len(row)-1])
    return dictaslist

def generate_1gramdict_withouttags(inputpath):
    filted=open('./files/filter.txt','w',encoding='GBK')
    onegram={}
    with open(inputpath,'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            row=row.strip()
            if len(row)!=0:
                row=row.split('  ')
                row=row[1:len(row)]
                for i in range(len(row)):
                    items=row[i].split('/')
                    if regularfilter(items[0]):
                        if items[1]=='nr':
                            continue
                        if items[0][0]=='[':
                            items[0]=items[0][1:]
                        if items[0][-1]==']':
                            items[0]=items[0][0:len(items[0])-1]
                        if items[0] not in onegram.keys():
                            onegram[items[0]]=1
                        else:
                            onegram[items[0]]+=1
                    else:
                        if '\u4e00'<=items[0][len(items[0])-1]<= '\u9fa5':
                            filted.write(items[0][len(items[0])-1]+'\n')

    with open('./files/onegramdic.txt','w',encoding='GBK') as result:
        for key in onegram:
            result.write(key+'  '+str(onegram[key])+'\n')
    filted.close()

def generate_1gramdict(inputpath):
    onegram={}
    with open(inputpath,'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            row=row.strip()
            if len(row)!=0:
                row=row.split('  ')
                row=row[1:len(row)]
                for i in range(len(row)):
                    items=row[i].split('/')
                    if contains_chinese(items[0]):
                        if len(items[0])>5 and items[1]=='nr':
                            continue
                        if items[0][0]=='[':
                            items[0]=items[0][1:]
                        if items[0][-1]==']':
                            items[0]=items[0][0:len(items[0])-1]
                        items=tuple(items)
                        if items not in onegram.keys():
                            onegram[items]=1
                        else:
                            onegram[items]+=1
    with open('./files/onegramdic.txt','w',encoding='GBK') as result:
        for key in onegram:
            result.write(key[0]+'  '+str(onegram[key])+'  '+key[1]+'\n')

def generate_bigramdict_withouttags(inputpath):
    bigram = {}
    with open(inputpath, 'r', encoding='GBK') as file:
        reader = file.readlines()
        for row in reader:
            row = row.strip()
            if len(row) != 0:
                row = row.split('  ')
                row = row[1:len(row)]
                words=[]
                for i in range(len(row)):
                    items = row[i].split('/')
                    if items[1] == 'nr':
                        continue
                    if regularfilter(items[0]):
                        if items[0][0] == '[':
                            items[0] = items[0][1:]
                        if items[0][-1] == ']':
                            items[0] = items[0][0:len(items[0]) - 1]
                        words.append(items[0])
                words.insert(0,'<BOS>')
                words.append('<EOS>')
                for i in range(len(words)-1):
                    item=(words[i],words[i+1])
                    if item not in bigram.keys():
                        bigram[item]=1
                    else:
                        bigram[item]+=1
    with open('./files/bigramdic.txt','w',encoding='GBK') as result:
        for key in bigram:
            result.write(key[0]+'  '+key[1]+'  '+str(bigram[key])+'\n')

def load_uni_prefixdict(dictpath):
    prefixdict={}
    total_fre=0
    with open(dictpath,'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            row=row.strip()
            row=row.split('  ')
            prefixdict[row[0]]=int(row[1])
            total_fre+=int(row[1])
            for i in range(len(row[0])):
                prefix=row[0][:i+1]
                if prefix not in prefixdict.keys():
                    prefixdict[prefix]=0
    return prefixdict,total_fre

def load_bi_prefixdict(dictpath):
    prefixdict={}
    with open(dictpath,'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            row=row.strip()
            row=row.split('  ')
            if row[0] not in prefixdict.keys():
                prefixdict[row[0]]={row[1]:int(row[2])}
            else:
                prefixdict[row[0]][row[1]]=int(row[2])
    return prefixdict

if __name__=='__main__':
    '''
    path='./files/199801_seg&pos.txt'
    generate_dict3(path)
    path1='./files/dic3.txt'
    dict=load_dict3(path1)
    length=23
    length=int(dict[len(dict)-1])
    print(length)
    print(type(length))
    
    path='./files/trainingdata.txt'
    generate_1gramdict_withouttags(path)
    generate_bigramdict_withouttags(path)
    path1 = './files/onegramdic.txt'
    path2='./files/bigramdic.txt'
    unidict=load_uni_prefixdict(path1)
    bidict=load_bi_prefixdict(path2)
    print(type(bidict))
    print(type(unidict))
    '''










