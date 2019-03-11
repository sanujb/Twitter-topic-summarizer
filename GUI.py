import Tkinter as tk
import os
import operator
from nltk.stem.porter import *
from PR import *
from PIL import Image, ImageTk
import TweetAPI as twapi


APP_WIDTH = 1000
APP_HEIGHT = 600


class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.widgets = []

        # Format - City: [(dot_location_id), (text_location_id)]
        self.cities = {'New York': [[248, 174], [270, 190], (40.7128, -74.0060)],
                       'Los Angeles': [[130, 210], [160, 225], (34.0522, -118.2437)],
                       'San Francisco': [[118, 196], [100, 182], (37.7749, -122.4194)],
                       'New Delhi': [[623, 239], [660, 250], (28.6139, 77.2090)]}
        self.init_page()

    def init_page(self):
        for w in self.widgets:
            w.destroy()
        del self.widgets[:]

        self.widgets.append(tk.Label(text='Select from the given locations to fetch trending topics', font='bold 13'))
        self.widgets[-1].place(x=int(APP_WIDTH / 2) - 220, y=10)

        self.show_map()
        self.widgets.append(tk.Label(text='Current Selection'))
        self.widgets[-1].place(x=255, y=546)
        self.init_page_selection = [tk.Entry(width=15), '']
        self.init_page_selection[0].place(x=400, y=550)
        self.widgets.append(self.init_page_selection[0])

        self.widgets.append(tk.Button(text='Next', command=self.topic_selection_screen, state='disabled'))
        self.widgets[-1].place(x=920, y=540)

    def onCityClick(self, event):
        id = event.widget.find_closest(event.x, event.y)[0]
        if id not in self.id_to_city:
            return
        self.init_page_selection[0].delete(0, 'end')
        self.init_page_selection[0].insert(0, self.id_to_city[id])
        self.init_page_selection[1] = self.id_to_city[id]
        self.widgets[-1].config(state= 'normal')

    def show_map(self):
        X, Y, DOT, TEXT, ID = 0, 1, 0, 1, 2

        load = Image.open('./Data/world_map.png')
        load = load.resize([940, 500], Image.ANTIALIAS)
        self.mapRender = ImageTk.PhotoImage(load)

        canvasX_border = 30
        canvas = tk.Canvas(height=int(0.85*APP_HEIGHT), width=APP_WIDTH - 2*canvasX_border)
        canvas.place(x=canvasX_border, y=40)
        canvas.create_image((450,250), image=self.mapRender)
        # canvas.bind('<Button-1>', self.onCityClick)
        self.id_to_city = {}

        for city, val in self.cities.items():
            val[DOT].append(canvas.create_oval(val[DOT][X]-4, val[DOT][Y]-4,val[DOT][X]+3, val[DOT][Y]+3, fill='red'))
            canvas.tag_bind(val[DOT][ID], '<Button-1>', self.onCityClick)
            val[TEXT].append(canvas.create_text(val[TEXT][X], val[TEXT][Y], text=city))
            self.id_to_city[val[DOT][ID]] = city

        self.canvas_map = canvas
        self.widgets.append(canvas)

    def topic_selection_screen(self, haveTrends = False):
        for w in self.widgets:
            w.destroy()
        del self.widgets[:]

        if not haveTrends:
            self.trends = twapi.get_trending_topics(self.cities[self.init_page_selection[1]][2])

        self.widgets.append(tk.Button(text='Back', command=self.init_page))
        self.widgets[-1].place(x=50, y = 540)

        self.widgets.append(tk.Label(text = 'Select a topic to begin summarizing',font = 'bold 13'))
        self.widgets[-1].place(x=320, y=10)

        self.widgets.append(tk.Button(text='Fetch Tweets and Summarize', command=self.openSummary))
        self.widgets[-1].place(x=600, y=300)

        self.topicSelection = tk.Listbox()
        self.topicSelection.config(width=40, activestyle=None)
        self.topicsSorted = sorted(self.trends.items(), key=operator.itemgetter(1), reverse=True)
        # self.topicSelection.insert(tk.ACTIVE, topicsSorted[0][0] + ' - ' + str(topicsSorted[0][1][0]) + ' Tweets')
        for t in self.topicsSorted:
            self.topicSelection.insert(tk.END, t[0] + ' - ' + str(t[1][0]) + ' Tweets')
        self.topicSelection.select_anchor(0)
        self.topicSelection.select_set(0)
        self.topicSelection.place(x=70, y=60)
        self.widgets.append(self.topicSelection)


    def openSummary(self):
        self.selectedTopic = self.topicsSorted[self.topicSelection.curselection()[0]]
        print(self.selectedTopic)
        for w in self.widgets:
            w.destroy()
        del self.widgets[:]

        self.widgets.append(tk.Button(text='Back', command= lambda : self.topic_selection_screen(True)))
        self.widgets[-1].place(x=50, y=540)

        self.widgets.append(tk.Label(text = 'Summary of topic: '+ self.selectedTopic[0], font='bold 14'))
        self.widgets[-1].place(x=30, y=11)

        tweets = twapi.getTweets(self.selectedTopic[1][1], self.cities[self.init_page_selection[1]][2], 2)
        raw_length = len(tweets)
        print 'before: ',len(tweets)
        tweets, spam_stats, spam_tweets = twapi.preprocess(tweets)
        final_length = len(tweets)
        print 'after:', len(tweets), spam_stats
        # w.append(tk.Button(text = 'Back', command = self.mainPage))
        # w[-1].place(x=APP_WIDTH-70, y=APP_HEIGHT-50)
        #
        # public_tweets = readTweets(selected_topic)
        # public_tweets,spam_stats,spam_tweets = preprocess(public_tweets,selected_topic)
        res = computeStuff(self.selectedTopic[0])
        print 'RES:', res

        self.widgets.append(tk.Label(text = 'Tweet Statistics',font = 'bold 12'))
        self.widgets[-1].place(x=30, y=40)

        self.widgets.append(tk.Label(text = 'Total Tweets Retrieved: ' + str(raw_length), font = 'bold 10'))
        self.widgets[-1].place(x=40, y=65)

        self.widgets.append(tk.Label(text = 'Tweets Removed:' + str(raw_length - final_length), font = 'bold 10'))
        self.widgets[-1].place(x=40, y=85)

        self.widgets.append(tk.Label(text = '- Users with more than 5 Tweets: ' + str(spam_stats['Users_maxTweets'])))
        self.widgets[-1].place(x=50, y=105)

        self.widgets.append(tk.Label(text = 'Removed ' + str(spam_stats['Tweets_maxTweets']) + ' tweets'))
        self.widgets[-1].place(x=64, y=125)

        self.widgets.append(tk.Label(text = '- Users with Reputation below 0.01: ' + str(spam_stats['Users_lowRep'])))
        self.widgets[-1].place(x=50, y=145)

        self.widgets.append(tk.Label(text = 'Removed ' + str(spam_stats['Tweets_lowRep']) + ' tweets'))
        self.widgets[-1].place(x=64, y=165)

        self.widgets.append(tk.Label(text = '- Users with account age less than 2 days: '+str(spam_stats['Users_minAge'])))
        self.widgets[-1].place(x=50, y=185)

        self.widgets.append(tk.Label(text = 'Removed ' + str(spam_stats['Tweets_minAge']) + ' tweets'))
        self.widgets[-1].place(x=64, y=205)

        self.widgets.append(tk.Label(text = '- Tweets with more than 3 hashtags: '+str(spam_stats['hashtags'])))
        self.widgets[-1].place(x=50, y=225)

        self.widgets.append(tk.Label(text = '- Tweets with more than 2 URLs: '+str(spam_stats['url'])))
        self.widgets[-1].place(x=50, y=245)

        self.widgets.append(tk.Label(text = '- Duplicate Tweets removed: ' + str(spam_stats['duplicate'])))
        self.widgets[-1].place(x=50, y=265)

        self.widgets.append(tk.Label(text = 'Tweets left after pre-processing: ' + str(final_length), font = 'bold 10'))
        self.widgets[-1].place(x=40, y=305)

        self.widgets.append(tk.Label(text = '2 Summaries Generated:', font = 'bold 12'))
        self.widgets[-1].place(x=40, y=335)

        self.widgets.append(tk.Label(text = res[0], font = 'bold 10'))
        self.widgets[-1].place(x=45, y=360)

        self.widgets.append(tk.Label(text = res[1], font = 'bold 10'))
        self.widgets[-1].place(x=45, y=380)

        # gt = []
        # with open('GT.txt') as f:
        #     for line in f:
        #         gt.append(line)
        #
        # for line in gt:
        #     if selected_topic in line:
        #         st, GrT,Sco = line.split('\t')
        #
        # self.widgets.append(tk.Label(text = 'Ground Truth:', font = 'bold 12'))
        # self.widgets[-1].place(x=40, y=405)
        #
        # self.widgets.append(tk.Label(text = GrT, font = 'bold 10'))
        # self.widgets[-1].place(x=45, y=430)
        #
        # self.widgets.append(tk.Label(text = 'Score: '+Sco, font = 'bold 12'))
        # self.widgets[-1].place(x=360, y=460)
        #
        # totRes = res[0]+res[1]
        # totRes = totRes.replace('\xe2\x80\x93','')
        # totRes = totRes.replace('\xe2\x80\x99','')
        # totRes = totRes.replace('\xe2\x80\x98','')
        # totRes = totRes.replace('\'s',' ').encode('utf8').split(' ')
        # #print GrT,totRes
        # GrT = GrT.split(' ')
        #
        # stemmer = PorterStemmer()
        # totRes = [stemmer.stem(k) for k in totRes]
        # GrT = [stemmer.stem(k) for k in GrT]
        #
        # prec_num = 0                    #ROUGE-1 Calculation
        # prec_den = float(len(GrT))
        # for k in GrT:
        #     if k in totRes:
        #         prec_num+=1
        #
        # #print prec_num,prec_den
        #
        # prec = prec_num/float(prec_den)
        #
        # self.widgets.append(tk.Label(text = 'ROUGE-1 : '+str('{0:.3f}'.format(prec)), font = 'bold 12'))
        # self.widgets[-1].place(x=490, y=460)

root = tk.Tk()
root.resizable(width=False,height=False)
root.geometry('{}x{}'.format(APP_WIDTH,APP_HEIGHT))
root.title('Twitter Topics Summarization v0.5')

MainApplication(root)
root.mainloop()