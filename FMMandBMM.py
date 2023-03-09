from generate_dict import load_dict3,contains_chinese
import time


def if_in_list(word,dictlist):
    for i in range(len(dictlist)-1):
        if dictlist[i]==word:
            return True

def cut2str(cut):
    seg_result=''
    for i in range(len(cut)):
        seg_result=seg_result+cut[i]+'/'+' '
    return seg_result

def FMM(sentence,dict):# sentence:待分词句子# dict:词典
    length=len(sentence)
    span=int(dict[len(dict)-1])
    head=0
    score1=0#切分个数
    score2=0#单字切分个数
    cut=[]#分词结果
    while head<length:
        score1+=1
        tail=head+span-1
        if tail>length-1:
            tail=length-1
        for i in range(span):
            if tail==head:
                cut.append(sentence[head:tail+1])
                score2+=1
                head+=1
                break
            if if_in_list(sentence[head:tail + 1],dict):
                cut.append(sentence[head:tail+1])
                head=tail+1
                break
            tail-=1
    return cut

def BMM(sentence,dict):
    length=len(sentence)
    span = int(dict[len(dict)-1])
    tail=length-1
    score1 = 0  # 切分个数
    score2 = 0  # 单字切分个数
    cut = []  # 分词结果
    while tail>=0:
        score1+=1
        head=tail-span+1
        if head<0:
            head=0
        for i in range(span):
            if head==tail:
                cut.append(sentence[head:tail+1])
                score2+=1
                tail-=1
                break
            if if_in_list(sentence[head:tail + 1],dict):
                cut.append(sentence[head:tail+1])
                tail=head-1
                break
            head+=1
    cut=cut[::-1]
    return cut

def aftertreatment(cut):
    temp =''
    flag = 0
    newcut = []
    for item in cut:
        if not contains_chinese(item):  # 不含中文
            temp += item
            flag = 1
        else:
            if flag == 0:
                newcut.append(item)
            elif flag == 1:
                flag = 0
                newcut.append(temp)
                temp = ''
                newcut.append(item)
    return newcut


if __name__=='__main__':

    path1 = './files/dic3.txt'
    path2 = './files/199801_sent.txt'
    path3='./files/seg_FMM.txt'
    path4='./files/seg_BMM.txt'
    dict = load_dict3(path1)
    max=500
    FMMfile=open(path3,'w',encoding='utf-8')
    BMMfile=open(path4, 'w', encoding='utf-8')
    start=time.time()
    with open(path2,'r') as input:
        reader=input.readlines()
        j=0
        for sentence in reader:
            j+=1
            if len(sentence)-1:#非空
                if j<=max:
                    cut=FMM(sentence,dict)
                    cut=aftertreatment(cut)
                    result=cut2str(cut)
                    FMMfile.write(result+'\n')
                    print('FMM完成',j,'/',max)
                else:
                    break;

    end=time.time()
    print('FMM处理',max,'个耗时：',end-start)
    FMMfile.close()
    start = time.time()



    with open(path2, 'r') as input:
        reader = input.readlines()
        j = 0
        for sentence in reader:
            j += 1
            if len(sentence) - 1:  # 非空
                if j <= max:
                    cut = BMM(sentence, dict)
                    cut = aftertreatment(cut)
                    result = cut2str(cut)
                    BMMfile.write(result + '\n')
                    print('BMM完成', j, '/',max)
                else:
                    break;
    end = time.time()
    print('BMM处理',max,'个耗时：', end - start)
    BMMfile.close()



