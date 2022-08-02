#--------------------------------------------
#   Name: Raunak Agarwal
#   ID: 1636678
#   CMPUT 274, Fall 2020
#
#   Assignment #1: ooclassifier
#--------------------------------------------
import sys
import copy     # for deepcopy()

Debug = False   # Sometimes, print for debugging
InputFilename = "file.input.txt"
TargetWords = [
        'outside', 'today', 'weather', 'raining', 'nice', 'rain', 'snow',
        'day', 'winter', 'cold', 'warm', 'snowing', 'out', 'hope', 'boots',
        'sunny', 'windy', 'coming', 'perfect', 'need', 'sun', 'on', 'was',
        '-40', 'jackets', 'wish', 'fog', 'pretty', 'summer'
        ]


def open_file(filename=InputFilename):
    try:
        f = open(filename, "r")
        return(f)
    except FileNotFoundError:
        # FileNotFoundError is subclass of OSError
        if Debug:
            print("File Not Found")
        return(sys.stdin)
    except OSError:
        if Debug:
            print("Other OS Error")
        return(sys.stdin)


def safe_input(f=None, prompt=""):
    try:
        # Case:  Stdin
        if f is sys.stdin or f is None:
            line = input(prompt)
        # Case:  From file
        else:
            assert not (f is None)
            assert (f is not None)
            line = f.readline()
            if Debug:
                print("readline: ", line, end='')
            if line == "":  # Check EOF before strip()
                if Debug:
                    print("EOF")
                return("", False)
        return(line.strip(), True)
    except EOFError:
        return("", False)


class C274:
    def __init__(self):
        self.type = str(self.__class__)
        return

    def __str__(self):
        return(self.type)

    def __repr__(self):
        s = "<%d> %s" % (id(self), self.type)
        return(s)


class ClassifyByTarget(C274):
    def __init__(self, lw=[]):
        # FIXME:  Call superclass, here and for all classes
        self.type = str(self.__class__)
        self.allWords = 0
        self.theCount = 0
        self.nonTarget = []
        self.set_target_words(lw)
        self.initTF()
        return

    def initTF(self):
        self.TP = 0
        self.FP = 0
        self.TN = 0
        self.FN = 0
        return

    def get_TF(self):
        return(self.TP, self.FP, self.TN, self.FN)

    # FIXME:  Use Python properties
    #     https://www.python-course.eu/python3_properties.php
    def set_target_words(self, lw):
        # Could also do self.targetWords = lw.copy().  Thanks, TA Jason Cannon
        self.targetWords = copy.deepcopy(lw)
        return

    def get_target_words(self):
        return(self.targetWords)

    def get_allWords(self):
        return(self.allWords)

    def incr_allWords(self):
        self.allWords += 1
        return

    def get_theCount(self):
        return(self.theCount)

    def incr_theCount(self):
        self.theCount += 1
        return

    def get_nonTarget(self):
        return(self.nonTarget)

    def add_nonTarget(self, w):
        self.nonTarget.append(w)
        return

    def print_config(self):
        print("-------- Print Config --------")
        ln = len(self.get_target_words())
        print("TargetWords Hardcoded (%d): " % ln, end='')
        print(self.get_target_words())
        return

    def print_run_info(self):
        print("-------- Print Run Info --------")
        print("All words:%3s. " % self.get_allWords(), end='')
        print(" Target words:%3s" % self.get_theCount())
        print("Non-Target words (%d): " % len(self.get_nonTarget()), end='')
        print(self.get_nonTarget())
        return

    def print_confusion_matrix(self, targetLabel, doKey=False, tag=""):
        assert (self.TP + self.TP + self.FP + self.TN) > 0
        print(tag+"-------- Confusion Matrix --------")
        print(tag+"%10s | %13s" % ('Predict', 'Label'))
        print(tag+"-----------+----------------------")
        print(tag+"%10s | %10s %10s" % (' ', targetLabel, 'not'))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'TP   ', 'FP   '))
        print(tag+"%10s | %10d %10d" % (targetLabel, self.TP, self.FP))
        if doKey:
            print(tag+"%10s | %10s %10s" % ('', 'FN   ', 'TN   '))
        print(tag+"%10s | %10d %10d" % ('not', self.FN, self.TN))
        return

    def eval_training_set(self, tset, targetLabel):
        print("-------- Evaluate Training Set --------")
        self.initTF()
        z = zip(tset.get_instances(), tset.get_lines())
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class()
            if lb == targetLabel:
                if cl:
                    self.TP += 1
                    outcome = "TP"
                else:
                    self.FN += 1
                    outcome = "FN"
            else:
                if cl:
                    self.FP += 1
                    outcome = "FP"
                else:
                    self.TN += 1
                    outcome = "TN"
            explain = ti.get_explain()
            print("TW %s: ( %10s) %s" % (outcome, explain, w))
            if Debug:
                print("-->", ti.get_words())
        self.print_confusion_matrix(targetLabel)
        return

    def classify_by_words(self, ti, update=False, tlabel="last"):
        inClass = False
        evidence = ''
        lw = ti.get_words()
        for w in lw:
            if update:
                self.incr_allWords()
            if w in self.get_target_words():    # FIXME Write predicate
                inClass = True
                if update:
                    self.incr_theCount()
                if evidence == '':
                    evidence = w            # FIXME Use first word, but change
            elif w != '':
                if update and (w not in self.get_nonTarget()):
                    self.add_nonTarget(w)
        if evidence == '':
            evidence = '#negative'
        if update:
            ti.set_class(inClass, tlabel, evidence)
        return(inClass, evidence)

    # Could use a decorator, but not now
    def classify(self, ti, update=False, tlabel="last"):
        cl, e = self.classify_by_words(ti, update, tlabel)
        return(cl, e)


class TrainingInstance(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inst = dict()
        # FIXME:  Get rid of dict, and use attributes
        self.inst["label"] = "N/A"      # Class, given by oracle
        self.inst["words"] = []         # Bag of words
        self.inst["class"] = ""         # Class, by classifier
        self.inst["explain"] = ""       # Explanation for classification
        self.inst["experiments"] = dict()   # Previous classifier runs
        return

    def get_label(self):
        return(self.inst["label"])

    def get_words(self):
        return(self.inst["words"])

    def set_class(self, theClass, tlabel="last", explain=""):
        # tlabel = tag label
        self.inst["class"] = theClass
        self.inst["experiments"][tlabel] = theClass
        self.inst["explain"] = explain
        return

    def get_class_by_tag(self, tlabel):             # tlabel = tag label
        cl = self.inst["experiments"].get(tlabel)
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_explain(self):
        cl = self.inst.get("explain")
        if cl is None:
            return("N/A")
        else:
            return(cl)

    def get_class(self):
        return self.inst["class"]

    def process_input_line(
                self, line, run=None,
                tlabel="read", inclLabel=True
            ):
        for w in line.split():
            if w[0] == "#":
                self.inst["label"] = w
                # FIXME: For testing only.  Compare to previous version.
                if inclLabel:
                    self.inst["words"].append(w)
            else:
                self.inst["words"].append(w)

        if not (run is None):
            cl, e = run.classify(self, update=True, tlabel=tlabel)
        return(self)

    def preprocess_words(self,mode="",i=[]):
        """
        preprocesses the individual traning instances
        depending on the mode.
        Arguments: Mode 
                    i: training instance
        """
        lw=i.get_words()
        lw=self.lower_case(lw)
        if mode=="" or mode=='keep-stops' or mode=='keep-digits':
            lw=self.punc_rem(lw)
        if mode=="" or mode=='keep-stops' or mode=='keep-symbols':    
            lw=self.dig_rem(lw)
        if mode=="" or mode=='keep-symbols' or mode=='keep-digits':
            lw=self.stop_rem(lw)
        i.inst['words']=lw
        #self.inst['words'].append(lw)    
        #self.inst["words"]=lw
        return


    def lower_case(self,t):
        lw=[x.lower() for x in t]
        return lw

    def punc_rem(self,lw=[]):
        targ=[]
        for t in lw:
            for c in t:
                if c.isnumeric()!=True and c.isalpha()!=True:
                    t=t.replace(c,'')
            targ.append(t)
            lw=targ
        return lw     

    def dig_rem(self,lw=[]):
        newtarg=[]
        for t in lw:
            if t.isnumeric()==True or t.isalpha()==True:
                newtarg.append(t)
            else:
                for c in t:
                    if c.isnumeric()==True:
                        t=t.replace(c,'')

                newtarg.append(t)
                lw=newtarg
        return lw

    def stop_rem(self,lw=[]):
        stop_wds=["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
        "you", "your","yours", "yourself", "yourselves", "he", "him",
        "his", "himself", "she", "her","hers", "herself", "it", "its", 
        "itself", "they", "them", "their", "theirs","themselves", "what",
         "which","who", "whom", "this", "that", "these", "those", 
        "am", "is", "are", "was", "were", "be","been", "being", "have",
        "has","had","having", "do", "does", "did", "doing","a","an","the",
        "and", "but", "if","or","because","as","until","while","of","at",
        "by","for", "with","about", "against", "between", "into",
        "through", "during","before", "after","above", "below", "to", 
        "from", "up", "down", "in", "out", "on","off", "over",
        "under", "again", "further", "then", "once", "here", "there",
        "when", "where","why", "how", "all", "any", "both", "each",
        "few", "more", "most", "other","some", "such", "no", "nor",
        "not", "only", "own", "same", "so","than","too", "very", "s",
        "t", "can", "will", "just", "don", "should", "now"]
        fintarg=[]

        for t in lw:
            if t not in stop_wds:
                fintarg.append(t)
            lw=fintarg    
        return lw    


class TrainingSet(C274):
    def __init__(self):
        self.type = str(self.__class__)
        self.inObjList = []     # Unparsed lines, from training set
        self.inObjHash = []     # Parsed lines, in dictionary/hash
        return


    def get_instances(self):
        return(self.inObjHash)      # FIXME Should protect this more

    def get_lines(self):
        return(self.inObjList)      # FIXME Should protect this more

    def print_training_set(self):
        print("-------- Print Training Set --------")
        z = zip(self.inObjHash, self.inObjList)
        for ti, w in z:
            lb = ti.get_label()
            cl = ti.get_class_by_tag("last")     # Not used
            explain = ti.get_explain()
            print("( %s) (%s) %s" % (lb, explain, w))
            if Debug:
                print("-->", ti.get_words())
        return

    def process_input_stream(self, inFile, run=None):
        assert not (inFile is None), "Assume valid file object"
        cFlag = True
        while cFlag:
            line, cFlag = safe_input(inFile)
            if not cFlag:
                break
            assert cFlag, "Assume valid input hereafter"

            # Check for comments
            if line[0] == '%':  # Comments must start with %
                continue

            # Save the training data input, by line
            self.inObjList.append(line)
            # Save the training data input, after parsing
            ti = TrainingInstance()
            ti.process_input_line(line, run=run)
            self.inObjHash.append(ti)
        return
    def preprocess(self,mode=""):
        """
        Converts individual instances of the trainingSet
        and preprocesses them by calling method preprocess_words.

        Argument:mode
        
        Returns: None
        """
        lw=[]
        ts=self.get_instances()
        ti=TrainingInstance()
        for i in ts:
            ti.preprocess_words(mode,i)


            #self.set_preprocess_words(lw,i)
            #self.inObjHash[i][1]['words']=lw
            #print(self.inObjHash)
        return

    def return_nfolds(self,num=3):
        """
        Creates sub data sets from the original dataset.
        The number of sub data sets created depends on num.

        Arguments:
        -num: number of sub data sets

        Returns:
        -A list of objects of class TrainingSet which contain
        the smaller datasets
        """
        ins=copy.deepcopy(self.get_instances())
        lin=copy.deepcopy(self.get_lines())
        leng=len(ins)
        list_of_nfolds=[]
        for i in range(num):
            newtset=TrainingSet()
            k=i
            for j in range(k,leng,num):
                newtset.add_fold(ins[j])
                newtset.add_fold_lin(lin[j])
            list_of_nfolds.append(newtset.copy())
            '''t=copy.deepcopy(self)
            ins=t.get_instances()
            lin=t.get_lines()
            ret_n_folds.append()'''
        return list_of_nfolds

    def add_fold_lin(self,lin):
        self.inObjList.append(lin)
        return

    def copy(self):
        p=copy.deepcopy(self)
        return p

    def add_fold(self,tset):
        self.inObjHash.append(tset)
        return

class ClassifyByTopN(ClassifyByTarget):
    def __init__(self,lw=[]):
        self.type = str(self.__class__)
        self.all_words=[]
        super().__init__(lw)
        return

    def target_top_n(self,tset,num=5,label=''):
        """
        Takes in tset, num, label as the input arguments
        and the sets new Target words.
        It creates a dictionary which has the words and their
        frequency.

        Arguments:
            -tset: training set
            -num: number of highest frequency terms.
            -label:only counts the frequency of words which
            have the label as label. 
        """
        ts=tset.get_instances()
        for i in ts:
                if i.get_label()==label:
                    for j in i.get_words():
                        self.all_words.append(j)
        set_of_all_words=set(self.all_words)
        list_of_all_words=list(set_of_all_words)
        emp_dict={}
        for i in list_of_all_words:
            emp_dict[i]=self.all_words.count(i)

        
        y=self.get_topn_nums(emp_dict,num)

        w=self.get_targ_words_from_y(y,emp_dict)

        self.set_target_words(w)
        '''word_set=set(word_list)
        dict={}
        for i in word_set:
            dict[i]=word_list.count(i)
        print(dict)'''
        return

    def get_targ_words_from_y(self,y=[],emp_dict={}):
        '''
        finds the keys(words) in emp_dict which have
        the same frequency as y.
        Arguments:
        -emp_dict:dictionary of words and their respective frequencies
        -y: list of highest frequencies

        Returns a list of target words.
        '''
        w=[]
        for vals in y:
            for key,value in emp_dict.items():
                if vals==value:
                    w.append(key)
        return w

    def get_topn_nums(self,emp_dict={},num=5):
        """
        Finds the highest values(frequencies) in emp_dict.

        Arguments
        -emp_dict: dictionary of words and the frequencies
        
        Returns a list of highest frequencies. Where one frequency is
        only present once.

        """
        y=[]
        val=sorted(emp_dict.values(),reverse=True)
        y.append(val[0])
        for i in range(len(val)):
            if len(y)==num:
                break
            if val[i+1] in y:
                pass
            else:
                y.append(val[i+1])
        return y

 

def basemain():
    tset = TrainingSet()
    run1 = ClassifyByTopN()
    print(run1)     # Just to show __str__
    lr = [run1]
    print(lr)       # Just to show __repr__

    argc = len(sys.argv)
    if argc == 1:   # Use stdin, or default filename
        inFile = open_file()
        assert not (inFile is None), "Assume valid file object"
        tset.process_input_stream(inFile, run1)
        inFile.close()
    else:
        for f in sys.argv[1:]:
            inFile = open_file(f)
            assert not (inFile is None), "Assume valid file object"
            tset.process_input_stream(inFile, run1)
            inFile.close()
    if Debug:
        tset.print_training_set()
    run1.print_config()     
    run1.print_run_info()   
    run1.eval_training_set(tset, '#weather') 
    return


if __name__ == "__main__":
    basemain()
