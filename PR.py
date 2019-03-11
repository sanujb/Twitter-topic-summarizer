import math
import io

english_stop = ['A', 'The','a','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under'
,'again','further','then','once','here','there','when','where','why','how'
,'all','any','both','each','few','more','most','other','some','such'
,'no','nor','not','only','own','same','so','than','too','very']

def read_tweets(filename):
    tweets = io.open(filename, encoding='utf-8').readlines()
    return tweets

class Node:

    def __init__(self, word, freqency=1.0):
        self.word = word
        self.freqency = freqency
        self.incoming = []  # node objects
        self.outgoing = []  # node objects

    def get_incoming_node(self, word):
       # print self.incoming, word
        for node in self.incoming:
            if node.word == word:
                return node
        return False

    def get_outgoing_node(self, word):
        for node in self.outgoing:
            if node.word == word:
                return node
        return False

    def __repr__(self):
        return self.word


def prepend_nodes(node, initial, index):
    for word in reversed(initial):
     #   print 'Node is %s' % node.word

        current_word_node = node.get_incoming_node(word)
        if current_word_node:
            if word in english_stop:
                current_word_node.freqency = 0.0
            else:
                logage = float(math.log(float(age[index])))
                repit = float(math.sqrt(float(reput[index])))
                logactivity = float(math.log(float(activity[index])))
                rtwtcnt = float(math.sqrt(1+float(retweet_count[index])))
                w=(logage)*(repit)*(logactivity)*(rtwtcnt)
                #w=(current_word_node.freqency+1)*(age[index])
                #print current_word_node.freqency+1
                #print age[index]
                #w=(float(current_word_node.freqency+1))*(float(math.log(age[index])))*(float(math.pow(reput[index]),2))*(float(math.log(activity[index])))*(float(math.sqrt(1+retweet)))
                current_word_node.freqency += w
            node = current_word_node
        else:
            new_node = Node(word)
            # print new_node.word
            # print new_node.freqency
            # print new_node.incoming + new_node.outgoing
            if word in english_stop:
                new_node.freqency = 0
            # print "testing before linking:"
            # print new_node.incoming

            #print node.outgoing
            # new_node.outgoing.append(node)
            # print "After appending node to outgoing of new_node:"
            # print node.incoming
            # print node.outgoing
            # print new_node.outgoing
            # print new_node.incoming

            node.incoming.append(new_node)
            #print 'For '+ node.word + ' ' + node.incoming + '| For ' + new_node.word + ' ' + new_node.outgoing
            # print "After appending new_node to incoming of node:"
            # print node.incoming
            # print node.outgoing
            # print new_node.outgoing
            # print new_node.incoming
          #  print 'Node Added: ' + new_node.word + ' Prepended to: ' + node.word + '\n'
            node = new_node


def append_nodes(node, following, index):
    for word in following:
      #  print 'Node is %s' % node.word
        current_word_node = node.get_outgoing_node(word)

        if current_word_node:
       #     print 'current_word_node is', current_word_node
            if word in english_stop:
                current_word_node.freqency = 0.0
            else:
                lg = float(math.log(float(age[index])))
                pw = float(reput[index])
                actvty = float(math.log(float(activity[index])))
                rtwt = float(math.sqrt(float(math.sqrt(1+float(retweet_count[index])))))
                w=(lg)*(pw)*(actvty)*(rtwt)
                #print current_word_node.freqency+1
                current_word_node.freqency += float(w/10.0)
            node = current_word_node
        else:
            new_node = Node(word)
            if word in english_stop:
                new_node.freqency = 0
            # new_node.incoming.append(node)
         #   print 'Node is', node.word, 'New Node is', new_node.word
            node.outgoing.append(new_node)
          #  print 'Node Added: ' + new_node.word + ' Appended to: ' + node.word + '\n'
            node = new_node


def make_graph(tweets, root_phrase):
    root_node = Node(root_phrase)
    root_node.freqency = 0
    index=0
    for tweet in tweets:
        if root_phrase in tweet:
            initial, following = tweet[:tweet.find(root_phrase)], tweet[tweet.find(root_phrase)+len(root_phrase):]
            initial = initial.split()
            following = following.split()
            prepend_nodes(root_node, initial, index)
            append_nodes(root_node, following, index)
        index += 1
    return root_node


def maximux_path_outgoing(root_node):
    if not len(root_node.outgoing):
        return (root_node.freqency, root_node.word)
    all_cases = [maximux_path_outgoing(child) for child in root_node.outgoing]
    weights_all_cases = [x[0] for x in all_cases]
    index = weights_all_cases.index(max(weights_all_cases))
    freqency, word = all_cases[index]
    return (root_node.freqency + freqency, root_node.word + ' ' + word)




def maximux_path_incoming(root_node):
    if not len(root_node.incoming):
        return (root_node.freqency, root_node.word)
    all_cases = [maximux_path_incoming(child) for child in root_node.incoming]
    weights_all_cases = [x[0] for x in all_cases]
    index = weights_all_cases.index(max(weights_all_cases))
    freqency, word = all_cases[index]
    return (root_node.freqency + freqency, root_node.word + ' ' + word)

def computeStuff(selected_topic):
    tweets = read_tweets('./Data/fetchedTweets.txt')
    global age, reput, activity, retweet_count, text
    age=[]
    reput=[]
    activity=[]
    retweet_count=[]
    text=[]
    for tweet in tweets:
        age_obj, reput_obj, activity_obj, retweet_count_obj, text_obj=tweet.split("\t")
        age.append(age_obj)
        reput.append(reput_obj)
        activity.append(activity_obj)
        retweet_count.append(retweet_count_obj)
        text.append(text_obj)

    root_node = make_graph(text,selected_topic)
    #print 'Graph made\n'
    freq0, str0 = maximux_path_incoming(root_node)
    freq1, str1 = maximux_path_outgoing(root_node)
    pre_pure = " ".join(reversed(str0.split()[len(root_node.word.split()):]))
    pre_pure = pre_pure + " " + selected_topic
    #print freq0, freq1
    #print pre_pure, root_node.word
    #print str1

    #print "1st partial summary:"

    res = []
    new_root_node=make_graph(tweets, str1)
    freq00, str00 = maximux_path_incoming(root_node)
    freq11, str11 = maximux_path_outgoing(root_node)
    pre_pure_new = " ".join(reversed(str00.split()[len(new_root_node.word.split()):]))
    pre_pure_new = pre_pure_new + " " + str1
    if freq00 > freq11:
        #res.append(pre_pure_new)
        res.append(new_root_node.word)
    else:
        res.append(str11)

    #print "2nd partial summary:"
    new_root_node=make_graph(tweets, pre_pure)
    freq2, str2=maximux_path_incoming(new_root_node)
    freq3, str3=maximux_path_outgoing(new_root_node)
    pure_str2= " ".join(reversed(str2.split()[len(new_root_node.word.split()):]))
    pure_str2 = pure_str2 + " " + pre_pure
    if freq2>freq3:
        #res.append(pure_str2)
        res.append(new_root_node.word)
    else:
        res.append(str3)

    return res