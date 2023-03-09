# encoding=GBK

import pickle
import math
import re
class triHMM():
    def __init__(self):
        self.Unidict = {}
        self.Bidict = {}
        self.Tridict ={}  # 元素是key:(w1,w2,w3) value:出现次数
        self.P1 = 0
        self.P2 = 0
        self.P3 = 0
        self.totallen=0
        self.status = ('B', 'M', 'E', 'S')
    def train(self,datapath,savepath):
        trainingdata = []
        with open(datapath, 'r', encoding='utf-8') as datafile:
            reader = datafile.readlines()
            for row in reader:
                rowdata = []
                row = row.strip()
                row = row.split(' ')
                for wordtag in row:
                    word_tag = wordtag.split('/')
                    rowdata.append(tuple(word_tag))
                trainingdata.append(rowdata)
        for row in trainingdata:
            wordspan=(('', 'BOS'),('', 'BOS'))
            if wordspan in self.Bidict.keys():
                self.Bidict[wordspan]+=1
            else:
                self.Bidict[wordspan]=1
            if wordspan[0] in self.Unidict.keys():
                self.Unidict[wordspan[0]]+=2
                self.totallen+=2
            else:
                self.Unidict[wordspan[0]] =2
                self.totallen += 2

            for word_tag in row:
                tmp=[]
                tmp.append(word_tag)
                word_tag=tuple(tmp)
                wordspan=wordspan+word_tag
                if wordspan in self.Tridict.keys():
                    self.Tridict[wordspan]+=1
                else:
                    self.Tridict[wordspan]=1
                if wordspan[1:] in self.Bidict.keys():
                    self.Bidict[wordspan[1:]]+=1
                else:
                    self.Bidict[wordspan[1:]] = 1
                if wordspan[2] in self.Unidict.keys():
                    self.Unidict[wordspan[2]]+=1
                    self.totallen+=1
                else:
                    self.Unidict[wordspan[2]]=1
                    self.totallen+=1
                wordspan=wordspan[1:]

        tris=sorted(self.Tridict.keys(),key=lambda x: self.Tridict[x])


        p=[0,0,0]
        count=[0,0,0]
        i=0
        for trigram in tris:
            i+=1
            try:
                p[2] = (self.Tridict[trigram] - 1) / (self.Bidict[trigram[0:2]] - 1)  # 三元组频率/三元组前两元频率
            except:
                p[2]=0
            try:
                p[1] = (self.Bidict[trigram[1:]]-1)/ (self.Unidict[trigram[1]] - 1)   # 三元组后二元频率/三元组中间元频率
            except:
                p[1]=0
            try:
                p[0]= (self.Unidict[trigram[2]]-1)/ (self.totallen-1)    # 三元组后二元频率/三元组中间元频率
            except:
                p[0]=0

            maxindex = p.index(max(p))
            count[maxindex]+=self.Tridict[trigram]

        self.P1=count[0]/sum(count)
        self.P2=count[1]/sum(count)
        self.P3=count[2]/sum(count)
        print(self.P1)
        print(self.P2)
        print(self.P3)

        with open(savepath, "wb") as file:
            pickle.dump(self.P1, file)
            pickle.dump(self.P2, file)
            pickle.dump(self.P3, file)
            pickle.dump(self.Unidict, file)
            pickle.dump(self.Bidict, file)
            pickle.dump(self.Tridict, file)
            pickle.dump(self.totallen,file)
            print('done training')

    def loadmodel(self,path):
        with open(path, "rb") as file:
            self.P1=pickle.load(file)
            self.P2 = pickle.load(file)
            self.P3 = pickle.load(file)
            self.Unidict = pickle.load(file)
            self.Bidict=pickle.load(file)
            self.Tridict=pickle.load(file)
            self.totallen=pickle.load(file)


    def cal_log(self, char1, char2, char3):
        Uni = self.P1 * self.Unidict.get(char3,0)/self.totallen
        try:
            Bi=self.P2*self.Bidict.get((char2,char3),0)/self.Unidict.get(char2,0)
        except:
            Bi=0
        try:
            Tri = self.P3 * self.Tridict.get((char1, char2, char3), 0) / self.Bidict.get((char1, char2), 0)
        except:
            Tri=0
        try:
            return math.log(Uni + Bi + Tri)
        except:
            return float('-inf')




    def tag(self,sentence):
        bigrams=[((('', 'BOS'), ('', 'BOS')), 0.0, [])]
        for char in sentence:
            flag = 0
            floor={}
            for state in self.status:
                if self.Unidict.get((char,state),0) !=0:
                    flag=1
                    break
            if flag==0:
                for state in self.status:
                    for bigram in bigrams:
                        floor[(bigram[0][1], (char, state))] = (bigram[1], bigram[2] + [state])#key:((a,b),(ch,q))
                bigrams = list(map(lambda x: (x[0], x[1][0], x[1][1]), floor.items()))
                continue
            for state in self.status:
                for bigram in bigrams:
                    current_temp=self.cal_log(bigram[0][0], bigram[0][1], (char, state))
                    temp_p = bigram[1] + current_temp
                    if (not (bigram[0][1],(char, state)) in floor) or temp_p > floor[(bigram[0][1],(char, state))][0]:
                        floor[(bigram[0][1], (char, state))] = (temp_p, bigram[2] + [state])
            bigrams = list(map(lambda x: (x[0], x[1][0], x[1][1]), floor.items()))
        return zip(sentence, max(bigrams, key=lambda x: x[1])[2])

    def tag_line(self, data):#打标签,data是句子
        current = [((('', 'BOS'), ('', 'BOS')), 0.0, [])]
        for ch in data:#ch是字
            stage = {}
            not_exist = True#标致是否在词典里
            for state in self.status:
                if self.Unidict.get((ch,state),0)!= 0:#词频不为零
                    not_exist = False
                    break
            if not_exist:#不在词典
                for state in self.status:
                    for pre_word in current:
                        stage[(pre_word[0][1], (ch, state))] = (pre_word[1], pre_word[2] + [state])
                current = list(map(lambda x: (x[0], x[1][0], x[1][1]),stage.items()))
                continue
            for state in self.status:
                for pre_word in current:
                    current_temp=self.cal_log_line(pre_word[0][0], pre_word[0][1], (ch, state))
                    temp_p = pre_word[1] + current_temp
                    if (not (pre_word[0][1],(ch, state)) in stage) or temp_p > stage[(pre_word[0][1],(ch, state))][0]:
                        stage[(pre_word[0][1], (ch, state))] = (temp_p, pre_word[2] + [state])
            current = list(map(lambda x: (x[0], x[1][0], x[1][1]), stage.items()))

        temp=zip(data, max(current, key=lambda x: x[1])[2])
        return temp




def tag1cut(sentence):
        i=0
        cut=[]
        while i<len(sentence):
            word,tag=sentence[i]
            tmpword=''
            if i<len(sentence)-1:
                if tag == 'S' or tag == 'E':
                    tmpword = tmpword + word
                    cut.append(tmpword)
                    i += 1
                    continue

                if tag == 'B' :
                    if sentence[i + 1][1] == 'S' or sentence[i + 1][1] == 'B':
                        cut.append(word)
                        i += 1
                        continue
                    if sentence[i + 1][1] == 'M':
                        j = i + 1
                        tmpword = tmpword + word
                        while j<len(sentence) and sentence[j][1] == 'M':
                            tmpword = tmpword + sentence[j][0]
                            j += 1
                        if j==len(sentence):
                            j-=1
                        if sentence[j][1]=='M':
                            i=j+1
                            cut.append(tmpword)
                            continue
                        if sentence[j][1] == 'E' :
                            tmpword = tmpword + sentence[j][0]
                            cut.append(tmpword)
                            i = j + 1
                            continue
                        else:
                            cut.append(tmpword)
                            i = j
                            continue
                    if sentence[i + 1][1] == 'E':
                        tmpword = tmpword + word + sentence[i + 1][0]
                        cut.append(tmpword)
                        i += 2
                        continue

                if tag == 'M':
                    if sentence[i + 1][1] == 'M':
                        tmpword = tmpword + word
                        j = i + 1
                        while j<len(sentence) and sentence[j][1] == 'M'  :
                            tmpword = tmpword + sentence[j][0]
                            j += 1
                        if j==len(sentence):
                            j-=1
                        if sentence[j][1]=='M':
                            i=j+1
                            cut.append(tmpword)
                            continue
                        if sentence[j][1] == 'E' :
                            tmpword = tmpword + sentence[j][0]
                            cut.append(tmpword)
                            i = j + 1
                            continue
                        else:
                            cut.append(tmpword)
                            i = j
                            continue
                    if sentence[i + 1][1] == 'E':
                        tmpword = tmpword + word + sentence[i + 1][0]
                        cut.append(tmpword)
                        i += 2
                        continue
                    if sentence[i + 1][1] == 'S' or sentence[i + 1][1] == 'B':
                        cut.append(word)
                        i = i + 1
                        continue
            else:
                cut.append(word)
                i+=1
        return cut


if __name__=='__main__':
    trainingdatapath='./files/BMSE.txt'
    modelsavepath= './files/biHMMmodel.pkl'
    model = triHMM()
    #model.train(trainingdatapath,modelsavepath)#如果要重新训练请取消此行注释
    model.loadmodel(modelsavepath)
    testpath = './files/test.txt'#在这里更换需要分词的文件
    writepath='./files/finaloptimized_seg.txt'
    writefile=open(writepath,'w',encoding='GBK')
    with open(testpath,'r',encoding='GBK') as datafile:
        reader=datafile.readlines()
        for row in reader:
            row=row.strip()
            if len(row)!=0:
                pattern = '[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}'
                timetag = re.findall(pattern, row)
                row = re.sub(pattern, '', row)
                tag = model.tag(row)
                seg = tag1cut(list(tag))
                #print('seg',seg)
                if len(timetag) != 0:
                    seg.insert(0, timetag[0])
                result = ''
                #print(seg)
                for word in seg:
                    result += word + '/' + '  '
                writefile.write(result + '\n')
            else:
                writefile.write('\n')

    writefile.close()


