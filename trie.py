from generate_dict import contains_chinese
import time
import FMMandBMM

class Node():
    def __init__(self,c):
        self.C=c
        self.end=False
        self.hashlen=5000
        self.children=[False for i in range(self.hashlen)]
    def Hash(self,c):
        return ord(c)%4999
    def addchild(self,newnode):
        h=self.Hash(newnode.C)
        while not self.children[h]==False:
            h=(h+1)%self.hashlen
        self.children[h]=newnode
        return h
    def ifexist(self,c):
        h=self.Hash(c)
        temp=h
        if self.children[h]==False:
            return False
        else:
            while self.children[h].C!=c:
                h=(h+1)%self.hashlen
                if self.children[h]==False or h==temp:
                    return False
        return self.children[h]

class Trie(object):
    def __init__(self):
        self.root=Node('')
    def buildtree(self,W):
        nodepointer=self.root
        for C in W:
            next_node=nodepointer.ifexist(C)
            if next_node==False:
                newnode=Node(C)
                h=nodepointer.addchild(newnode)
                nodepointer=newnode
            else:
                nodepointer=next_node
        nodepointer.end=True

    def search(self,W):
        nodepointer=self.root
        for C in W:
            next_node=nodepointer.ifexist(C)
            if next_node==False:
                return False
            else:
                nodepointer=next_node
        return nodepointer.end


def gettreedict(dictpath):
    treedict=Trie()
    with open(dictpath,'r',encoding='GBK') as file:
        reader=file.readlines()
        for row in reader:
            row=row[0:len(row)-1]
            treedict.buildtree(row)
    return treedict

def FMM(sentence,tree,span):# sentence:待分词句子# dict:词典
    length=len(sentence)
    head=0
    cut=[]#分词结果
    while head<length:
        tail=head+span-1
        if tail>length-1:
            tail=length-1
        for i in range(span):
            if tail==head:#单字
                cut.append(sentence[head:tail+1])
                head+=1
                break
            if tree.search(sentence[head:tail + 1]):
                cut.append(sentence[head:tail+1])
                head=tail+1
                break
            tail-=1
    return cut

def BMM(sentence,tree,span):
    length=len(sentence)
    tail=length-1
    cut = []  # 分词结果
    while tail>=0:
        head=tail-span+1
        if head<0:
            head=0
        for i in range(span):
            if head==tail:
                cut.append(sentence[head:tail+1])
                tail-=1
                break
            if tree.search(sentence[head:tail + 1]):
                cut.append(sentence[head:tail+1])
                tail=head-1
                break
            head+=1
    cut=cut[::-1]
    return cut

def aftertreatment(cut):
    temp =''
    flag = 0
    first=0
    newcut = []
    j=0
    units=['年', '月', '日', '份', '时', '万', '亿', '分', '式', '团', '点', '兆', '钟', '型', '号', '井', '机', '划', '中', '米', '半', '秒', '制', '育', '艇', '师', '军', '期', '车', '级', '多', '类']
    for item in cut:
        j+=1
        if not contains_chinese(item):  # 不含中文就写入temp
            temp += item
            if j==len(cut):#到最后一个了
                newcut.append(temp)
            flag = 1#flag标志正在累计非中文
        else:#含中文
            if flag == 0:
                newcut.append(item)
            elif flag == 1:
                flag = 0
                if item in units:#累计符号后的中文是一个量纲
                    temp=temp+item
                    newcut.append(temp)
                    temp=''
                else:
                    newcut.append(temp)
                    temp = ''
                    newcut.append(item)
    return newcut

def optimizedaftertreatment(cut):
    temp =''
    flag = 0
    first=0
    newcut = []
    j=0
    units=['年', '月', '日', '份', '时', '万', '亿', '分', '式', '团', '点', '兆', '钟', '型', '号', '井', '机', '划', '中', '米', '半', '秒', '制', '育', '艇', '师', '军', '期', '车', '级', '多', '类']
    for item in cut:
        j+=1
        if not contains_chinese(item):  # 不含中文就写入temp
            temp += item
            if j==len(cut):#到最后一个了
                newcut.append(temp)
            flag = 1#flag标志正在累计非中文
        else:#含中文
            if flag == 0:
                newcut.append(item)
            elif flag == 1:
                flag = 0
                if item in units:#累计符号后的中文是一个量纲
                    temp=temp+item
                    newcut.append(temp)
                    temp=''
                else:
                    if first!=0:
                        newcut.append(temp)
                        temp = ''
                        newcut.append(item)
                    else:
                        newcut.append(temp[0:len(temp)-1])
                        newcut.append(temp)


    return newcut

def cut2str(cut):
    seg_result=''
    for i in range(len(cut)):
        seg_result=seg_result+cut[i]+'/'+' '
    return seg_result

if __name__=='__main__':
    span=10
    FMMbaseline=59010
    BMMbaseline=58130
    path1 = './files/dic3.txt'
    treedict = gettreedict(path1)
    path2 = './files/199801_sent.txt'

    path3 = './files/seg_FMM.txt'
    path4 = './files/seg_BMM.txt'
    path5='./files/TimeCost.txt'
    print('building tree')
    treedict = gettreedict(path1)
    print('done')
    FMMfile = open(path3, 'w', encoding='GBK')
    BMMfile = open(path4, 'w', encoding='GBK')
    timefile=open(path5,'w',encoding='GBK')

    start = time.time()
    with open(path2, 'r') as input:
        reader = input.readlines()
        for sentence in reader:
            if len(sentence) - 1:  # 非空
                sentence = sentence.strip()
                cut = FMM(sentence, treedict, span)
                cut = aftertreatment(cut)
                result = cut2str(cut)
                FMMfile.write(result + '\n')
            else:
                FMMfile.write('\n')


    end = time.time()
    timefile.write('优化前FMM处理预计耗时：'+str(FMMbaseline)+'\n')
    timefile.write('优化后FMM处理句子耗时：' + str(end-start) + '\n')
    FMMfile.close()
    

    start = time.time()
    with open(path2, 'r') as input:
        reader = input.readlines()
        for sentence in reader:
            if len(sentence) - 1:  # 非空
                sentence = sentence.strip()
                cut = BMM(sentence, treedict, span)
                cut = aftertreatment(cut)
                result = cut2str(cut)
                BMMfile.write(result + '\n')
            else:
                BMMfile.write('\n')


    end = time.time()
    timefile.write('优化前BMM处理预计耗时：' + str(BMMbaseline) + '\n')
    timefile.write('优化后BMM处理耗时：' + str(end - start) + '\n')
    BMMfile.close()

