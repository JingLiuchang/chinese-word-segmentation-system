import math
import pickle
possiblefatherof={'B':['S','E'], 'M':['M','B'], 'E':['B','M'], 'S':['E','S']}
Q=['B', 'M', 'E', 'S'] #状态集.词首、词中、词尾、单字
smooth=-100000000

#最大似然训练HMM参数
class train():
    """
        训练HMM模型
    """
    def __init__(self):
        self.A={}
        self.B={}
        self.P={}
        self.total_sentence=0
        self.statecount={}
        for q in Q:
            self.B[q]={}
            self.P[q]=0
            self.statecount[q]=0
        for q in Q:
            self.A[q]={}
            for nextstate in Q:
                self.A[q][nextstate]=0

    def taglist(self,wordlist):
        """
            对句子进行BMES标注
            :param wordlist:词列表
            :return:chars:字符列表；tags:标注列表
        """
        chars = []
        tags = []
        for word in wordlist:
            word = list(word)
            chars.extend(word)
            if len(word) == 1:
                tags.append('S')
                self.P['S'] += 1
            else:
                self.P['B'] += 1
                for i in range(len(word)):
                    if i == 0:
                        tags.append('B')
                    elif i == len(word) - 1:
                        tags.append('E')
                    else:
                        tags.append('M')
        return chars, tags

    def trainparamater(self,datapath, namepath,savepath):
        """
            对句子进行二元文法分词
            :param datapath:训练数据
            :param namepath:人名信息
            :param savepath:模型保存地址
            :return:模型参数
        """
        with open(datapath, 'r', encoding='GBK') as file:
            reader = file.readlines()
            for row in reader:
                row = row.strip()
                if len(row) != 0:
                    self.total_sentence += 1
                    row = row.split('  ')
                    row = row[1:len(row)]
                    sentence = []
                    for i in range(len(row)):
                        items = row[i].split('/')  # 词：词性
                        if items[0][0] == '[':
                            items[0] = items[0][1:]
                        if items[0][-1] == ']':
                            items[0] = items[0][0:len(items[0]) - 1]
                        sentence.append(items[0])
                    chars, tags = self.taglist(sentence)

                    for i in range(len(chars)):
                        if i != len(chars) - 1:
                            self.A[tags[i]][tags[i + 1]] += 1
                        if chars[i] in self.B[tags[i]].keys():
                            self.B[tags[i]][chars[i]] += 1
                        else:
                            self.B[tags[i]][chars[i]] = 1
                        self.statecount[tags[i]] += 1
        with open(namepath, 'r', encoding='utf-8') as file:
            reader = file.readlines()
            for row in reader:
                row = row.strip()
                sentence=[]
                if len(row) != 0:
                    self.total_sentence += 1
                    #sentence.append(row[0])  #这两行安照人名分成姓+名字形式，反而使得HMM识别未登录词能力下降了
                    #sentence.append(row[1:len(row)])
                    sentence.append(row)
                    chars, tags = self.taglist(sentence)

                    for i in range(len(chars)):
                        if i != len(chars) - 1:
                            self.A[tags[i]][tags[i + 1]] += 1
                        if chars[i] in self.B[tags[i]].keys():
                            self.B[tags[i]][chars[i]] += 1
                        else:
                            self.B[tags[i]][chars[i]] = 1
                        self.statecount[tags[i]] += 1
        #最大似然估计模型参数
        for q in Q:
            for nextstate in Q:
                if self.A[q][nextstate] == 0:
                    self.A[q][nextstate] = smooth
                else:
                    self.A[q][nextstate] = math.log(self.A[q][nextstate] / self.statecount[q])
            for char in self.B[q].keys():
                self.B[q][char] = math.log(self.B[q][char] / self.statecount[q])
            if self.P[q] == 0:
                self.P[q] = smooth
            else:
                self.P[q] = math.log(self.P[q] / self.total_sentence)

        with open(savepath, 'wb') as savefile:
            pickle.dump(self.A, savefile)
            pickle.dump(self.B, savefile)
            pickle.dump(self.P, savefile)

class runHMM():
    """
        使用训练好了的HMM模型
    """

    def __init__(self,modelpath):
        self.A = {}
        self.B = {}
        self.P = {}
        with open(modelpath, "rb") as file:
            self.A = pickle.load(file)
            self.B = pickle.load(file)
            self.P = pickle.load(file)


    def find_besttags(self,sentence):
        """
            对句子sentence进行序列标注BMES
            :param sentence:待标注句子
            :return:标注结果tags和得分
        """
        wordnum=len(sentence)
        C={}#最大代价
        F={}#父节点
        #初始化每一层每一个可能状态代价是最小值，父节点是空
        for i in range(wordnum):
            C[i]={}
            F[i]={}
            for q in Q:
                C[i][q]=smooth
                F[i][q]=''
        #初始化第一层
        for q in Q:
            C[0][q]=self.P[q]+self.B[q].get(sentence[0],smooth)
            F[0][q]=''
        for i in range(1,wordnum):
            O=sentence[i]
            for q in Q:
                max=0
                father=''
                j=0
                for pre_q in possiblefatherof[q]:
                    j+=1
                    cost=C[i-1][pre_q]+self.A[pre_q][q]+self.B[q].get(O,smooth)
                    if j==1:
                        max=cost
                        father=pre_q
                    else:
                        if cost>max:
                            max=cost
                            father=pre_q
                C[i][q]=max
                F[i][q]=father
        tags=[]
        S=C[wordnum-1]['S']
        E=C[wordnum-1]['E']
        if E>=S:
            q='E'
            n=wordnum-1
            tags.append(q)
            while n>0:
                q=F[n][q]
                n-=1
                tags.append(q)
            tags.reverse()
            return E,tags
        else:
            q = 'S'
            n = wordnum - 1
            tags.append(q)
            while n > 0:
                q = F[n][q]
                n -= 1
                tags.append(q)
            tags.reverse()
            return S, tags

    def recut(self,singlewords):
        """
            对未登录词进行处理
            :param singlewords:未登录的单字成词的字符组成的字符串
            :return:分词结果
        """
        cost, tags=self.find_besttags(singlewords)
        newseg=[]
        word=''
        for i in range(len(tags)):
            if tags[i]=='B' or tags[i]=='M':
                word+=singlewords[i]
            elif tags[i]=='S' or tags[i]=='E':
                word+=singlewords[i]
                newseg.append(word)
                word=''
        return newseg

    def OOV(self,seglist):
        """
            对二元文法分词结果进行未登录词处理
            :param seglist:二元文法分词结果
            :return:新分词结果
        """
        tmp=''
        i=0
        flag=0
        while i<len(seglist):
            word=seglist[i]
            if len(word)==1:
                tmp+=word
                j=i+1
                while j<len(seglist) and len(seglist[j])==1:
                    tmp+=seglist[j]
                    j+=1
                if len(tmp)>1:
                    del seglist[i:j]
                    newseg=self.recut(tmp)
                    tmp = ''
                    k=i
                    for newword in newseg:
                        seglist.insert(k,newword)
                        k+=1
                else:
                    tmp=''
                i=j
            else:
                i+=1

        return seglist






if __name__=='__main__':
    """
        HMM标注句子效果展示
    """
    sentence='田纪云、王汉斌、倪志福'
    trainpath='./files/trainingdata.txt'
    namepath='./files/name.txt'
    savepath='./files/model.pkl'
    model=train()
    model.trainparamater(trainpath,namepath,savepath)
    hmm=runHMM('./files/model.pkl')
    cost,tags=hmm.find_besttags(sentence)
    print(sentence)
    print(tags)
    #田纪云、王汉斌、倪志福
    #['B', 'M', 'E', 'S', 'B', 'M', 'E', 'S', 'B', 'M', 'E']


