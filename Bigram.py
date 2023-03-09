#coding:gbk
import math
from generate_dict import load_bi_prefixdict,load_uni_prefixdict
from trie import aftertreatment,cut2str
import HMM
hmm=HMM.runHMM('./files/model.pkl')

#参考PPT
def buildDAG(uniprefixdict,sentence):
    """
        构建sentence句子的DAG图
        :param uniprefixdict:一元前缀词典
        :param sentence:句子
        :return:DAG
    """
    DAG={}
    N=len(sentence)
    for i in range(N):
        tmp=[]
        j=i
        frag=sentence[i]
        while j<N and frag in uniprefixdict.keys():
            if uniprefixdict[frag]>0:
                tmp.append(j)
            if uniprefixdict[frag]==0 and len(frag)==1:#认为单个字是应当被认识的
                tmp.append(j)
            j+=1
            frag=sentence[i:j+1]
        if not tmp:
            tmp.append(i)
        DAG[i]=tmp
    return DAG

def bayes(w1,w2,uniprefix_dict,biprefix_dict):
    """
        计算logP(w2|w1) 即词对w1w2出现概率
        :param word1:第一个词
        :param word2:第二个词
        :param uniprefix_dict:一元前缀词典
        :param biprefix_dict:二元前缀词典
        :return:log值
    """
    c1=c12=0
    if w1 in uniprefix_dict.keys():
        c1=uniprefix_dict[w1]
    else:
        c1=0
    if w1 in biprefix_dict.keys():
        if w2 in biprefix_dict[w1].keys():
            c12 = biprefix_dict[w1][w2]
    else:
        c12=0
    c12+=1
    c1+=len(uniprefix_dict.keys())
    return math.log(c12)-math.log(c1)

def LMseg(sentence,uniprefixdict,biprefixdict,oov):
    """
            对句子进行二元文法分词
            :param sentence:待分词句子
            :param uniprefixdict:一元前缀词典
            :param biprefixdict:二元前缀词典
            :param oov:是否使用未登录词处理
            :return:分词结果
    """
    DAG=buildDAG(uniprefixdict,sentence)#建立DAG
    for key in DAG:
        if DAG[key][0]!=key:
            break
    forward={}#前向
    backward={}#反向
    pos=5
    tmp = {}
    w1 = '<BOS>'#前五个字符默认是<BOS>
    for i in DAG[5]:
        w2 = sentence[5:i + 1]
        word2 = (5, i + 1)
        tmp[word2] = bayes(w1, w2, uniprefixdict, biprefixdict)
        if word2 in backward.keys():
            if w1 not in backward[word2]:
                backward[word2].append(w1)
        else:
            backward[word2] = []
            backward[word2].append(w1)
    forward[w1] = tmp
    while pos<len(sentence)-5:
        for nextpos in DAG[pos]:
            w1=sentence[pos:nextpos+1]
            word1=(pos,nextpos+1)#word1和2都不能用字符串表示，除非是EOS和BOS，因为字符串可以重复出现在一个句子
            nextDAG=DAG[nextpos+1]
            tmp = {}
            for nextnextpos in nextDAG:
                w2=sentence[nextpos+1:nextnextpos+1]
                word2=(nextpos+1,nextnextpos+1)
                if w2=='<':
                    w2='<EOS>'
                    word2='<EOS>'
                tmp[word2]=bayes(w1,w2,uniprefixdict,biprefixdict)
                if word2 in backward.keys():
                    if word1 not in backward[word2]:
                        backward[word2].append(word1)
                else:
                    backward[word2]=[]
                    backward[word2].append(word1)
            forward[word1]=tmp
        pos+=1
    maxcost={}
    for w in forward.keys():
        if w=='<BOS>':
            maxcost[w]=(0,w)
        else:
            fathers=backward[w]
            for i in range(len(fathers)):
                word=fathers[i]
                cost = forward[word][w] + maxcost[word][0]
                if i==0:
                    max=cost
                    father=word
                else:
                    if cost>max:
                        max = cost
                        father = word
            maxcost[w] = (max, father)
    eosfathers=backward['<EOS>']
    for i in range(len(eosfathers)):
        word=eosfathers[i]
        cost = forward[word]['<EOS>'] + maxcost[word][0]
        if i==0:
            max = cost
            father = word
        else:
            if cost>max:
                max = cost
                father = word
    maxcost['<EOS>'] = (max, father)
    seg=[]
    path='<EOS>'
    while path!='<BOS>':
        if path=='<EOS>':
            seg.append(path)
        else:
            w = sentence[path[0]:path[1]]
            seg.append(w)
        path=maxcost[path][1]
    seg.append('<BOS>')
    seg.reverse()
    seg.pop()
    seg.pop(0)
    seg = aftertreatment(seg)
    if oov==True:
        timetag=seg[0]
        newseg=hmm.OOV(seg[1:len(seg)])
        newseg.insert(0,timetag)
        return newseg
    return seg

def runBigramseg(datapath,OOV):
    """
        对datapath路径的文件进行二元分词
        :param OOV:是否使用未登录词处理
        :return:分词结果
    """
    unidictpath = './files/onegramdic.txt'
    bidictpath = './files/bigramdic.txt'
    writepath1 = './files/seg_LM.txt'
    writepath2 = './files/seg_LMOOV.txt'
    uniprefixdict = load_uni_prefixdict(unidictpath)[0]
    biprefixdict = load_bi_prefixdict(bidictpath)
    if OOV:
        writefile = open(writepath2, 'w', encoding='GBK')
    else:
        writefile = open(writepath1, 'w', encoding='GBK')
    with open(datapath, 'r', encoding='GBK') as file:
        reader = file.readlines()
    for row in reader:
        row = row.strip()
        if len(row) != 0:
            row = '<BOS>' + row + '<EOS>'
            seq = LMseg(row, uniprefixdict, biprefixdict, OOV)
            result = cut2str(seq)
            writefile.write(result + '\n')
        else:
            writefile.write('\n')
    writefile.close()
    print('Bigram_seg done')


if __name__=='__main__':
    datapath='./files/test.txt'#更改此参数来改变待分词文件
    OOV=False#True将会使用OOV优化，结果写入seg_LMOOV.txt;False将只进行二元文法分词，结果写入seg_LM.txt
    runBigramseg(datapath,OOV)
