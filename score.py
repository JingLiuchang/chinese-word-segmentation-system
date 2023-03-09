import re


def eval(testset,hatset):
    total_hat=0
    total_test=0
    TP=0
    for i in range(len(testset)):
        testcut=testset[i]
        hatcut=hatset[i]
        total_test+=len(testcut)
        total_hat+=len(hatcut)
        testpos=[]
        hatpos=[]
        pos=0
        for j in range(len(testcut)):
            pos+=len(testcut[j])
            testpos.append(pos)
        pos=0
        for j in range(len(hatcut)):
            pos+=len(hatcut[j])
            hatpos.append(pos)
        posT=0
        posH=0
        t=h=0
        while (posT<testpos[len(testpos)-1]) or (posH<hatpos[len(hatpos)-1]):
            try:
                posT = testpos[t]
                posH = hatpos[h]
            except:
                total_test -= len(testcut)
                total_hat -= len(hatcut)
                break
            if posT==posH:
                TP+=1
                t+=1
                h+=1
            else:
                while True:
                    if posH>posT:
                        t+=1
                        try:
                            posT=testpos[t]
                        except:
                            total_test -= len(testcut)
                            total_hat -= len(hatcut)
                            break
                    elif posH<posT:
                        h+=1
                        try:
                            posH = hatpos[h]
                        except:
                            total_test -= len(testcut)
                            total_hat -= len(hatcut)
                            break
                    else:
                        t+=1
                        h+=1
                        break
    try:
        pre = TP / total_hat
        recall = TP / total_test
    except:
        pre=1
        recall=1
    return pre,recall

def ansbuild(path):
    A = open(path, 'r', encoding='GBK')
    readA = A.readlines()
    ans = []
    for row in readA:
        if len(row) - 1:
            row = re.sub(r'\s*|[a-zA-Z]*|\[|\]', '', row)
            row = row.split('/')
            row.pop()
            ans.append(row)
    return ans

def hatbuild(path):
    hat=open(path,'r',encoding='GBK')
    readhat=hat.readlines()
    hat=[]
    for row in readhat:
        if len(row) - 1:
            row = re.sub(r'\s+', '', row)
            row = row.split('/')
            row.pop()
            hat.append(row)
    return hat

def printscore(standardpath,segpath):
    ans = ansbuild(standardpath)
    hat = hatbuild(segpath)
    p, r = eval(ans, hat)
    print('P:',p)
    print('R:',r)
    print('F1:',2*p*r/(p+r))


if __name__=='__main__':
    bigram='./files/seg_LM.txt'
    bigramOOV='./files/seg_LMOOV.txt'
    biHMM='./files/finaloptimized_seg.txt'
    standard='./files/test_standard.txt'

    printscore(standard,bigram)
    printscore(standard,bigramOOV)
    printscore(standard,biHMM)




