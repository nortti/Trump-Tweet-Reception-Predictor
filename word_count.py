#!/usr/bin/env python
import pandas as pd
import string
import plotly as py
import plotly.graph_objs as go
from nltk.stem.porter import PorterStemmer
from collections import Counter
import operator

def generate(json_data, out_dir, num_top_words = 25):
    stopword_file = "stop-word-list.csv"

    # Data IN
    df = pd.read_json(json_data)[['text', 'retweet_count', 'favorite_count']]
    user = pd.read_json(json_data)[['user']]['user'][0]

    name = user.get('name')
    screen_name = user.get('screen_name')

    # Stopwords
    with open(stopword_file) as f:
        stopwords = set(f.read().split(", "))

    df['text'] = df['text'].apply(lambda row: ''.join(l for l in row.lower() if l not in string.punctuation))
    df['text'] = df['text'].apply(lambda row: ' '.join([word for word in row.split() if word not in stopwords]))
    ps = PorterStemmer()
    df['text'] = df['text'].apply(lambda row: ' '.join([ps.stem(word) for word in row.split()]))

    # Wordcount

    words = Counter();

    # Simple word count

    for row in df['text']:
            wordlist = row.split()
            words.update(word for word in wordlist)

    topW = words.most_common(num_top_words)

    trace1 = go.Bar(
                x=[val[0] for val in topW],
                y=[val[1] for val in topW],
        )
    data1 = go.Data([trace1])

    layout1 = go.Layout(
        title= name+"'s Tweet Words: Word Count",
            font=dict(size=18),
        xaxis= dict(
            title= 'Most Used Words',
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'Word Count',
            ticklen= 5,
            gridwidth= 2,
        ),
        showlegend= False
    )

    fig = go.Figure(data=data1, layout=layout1)
    py.offline.plot(fig, filename = out_dir + 'top_words.html')

    retweets = {}
    likes = {}
    combi = {}

    for i in range(0, len(df['text'])):
            wordlist = df['text'][i].split()
            for w in wordlist:
                    if not w in retweets:
                            retweets[w] = df['retweet_count'][i]
                            likes[w]=df['favorite_count'][i]
                            combi[w]=(df['retweet_count'][i],df['favorite_count'][i])
                    else:
                            retweets[w] = retweets[w] + df['retweet_count'][i]
                            likes[w] = likes[w] + df['favorite_count'][i]
                            combi[w] = (retweets[w] + df['retweet_count'][i], likes[w] + df['favorite_count'][i])

    # arrenge words by retweets / likes for every tweet the word appear
    ret_sort = sorted(retweets.items(), key=operator.itemgetter(1), reverse=True)
    topW_re = ret_sort[:num_top_words]
    lik_sort = sorted(likes.items(), key=operator.itemgetter(1), reverse=True)
    topW_li = lik_sort[:num_top_words]

    # Retweets

    retro = {}
    for i in range(0, len(ret_sort)):
            retro[ret_sort[i][0]] = (float(ret_sort[i][1])/words.get(ret_sort[i][0]))
    retro_sort = sorted(retro.items(), key=operator.itemgetter(1), reverse=True)

    # Likes

    litro = {}
    for i in range(0, len(lik_sort)):
            litro[lik_sort[i][0]] = (float(lik_sort[i][1])/words.get(lik_sort[i][0]))
    litro_sort = sorted(litro.items(), key=operator.itemgetter(1), reverse=True)

    # Overall plots

    # Calculate accumulate respond
    accumulate_responds = []
    for w in combi.keys():
        accumulate_responds.append(words[w])

    # Normalize accumulate_responds to use as size of bubble
    accumulate_responds_normalized = [float(i)/max(accumulate_responds) for i in accumulate_responds]
    sizeref = 2*max(accumulate_responds_normalized)/(80**2)

    # cumulative likes / retweets for words

    fig_data1 = []
    trace_f1= go.Scatter(
            x = [combi[key][0] for key in combi.keys()],
            y = [combi[key][1] for key in combi.keys()],
        mode= 'markers',
        marker= dict(
            symbol = 'circle',
            sizemode = 'area',
            sizeref = sizeref,
            sizemin = 6,
            size = accumulate_responds_normalized,
            line= dict(width=1),
            color= 'rgb(93, 164, 214)',
            opacity= 0.8),
            textfont = dict(
                    size = 20),
            text= [key+': '+str(words[key]) for key in combi.keys()])
    fig_data1.append(trace_f1);

    layout_f1= go.Layout(
        title= name+"'s Tweet Words: Accumulative response count",
            font=dict(size=18),
        hovermode= 'closest',
        xaxis= dict(
            title= 'Retweet Count',
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'Favorite Count',
            ticklen= 5,
            gridwidth= 2,
        ),
        showlegend= False
    )
    fig_f1 = go.Figure(data = fig_data1, layout=layout_f1)
    py.offline.plot(fig_f1, filename = out_dir + 'overall_words.html')

    # Average likes / retweets for word

    fig_data2 = []
    trace_f2= go.Scatter(
            x = [float(combi[key][0])/words.get(key) for key in combi.keys()],
            y = [float(combi[key][1])/words.get(key) for key in combi.keys()],
        mode= 'markers',
        marker= dict(
            symbol = 'circle',
            sizemode = 'area',
            sizeref = sizeref,
            sizemin = 6,
            size = accumulate_responds_normalized,
            line= dict(width=1),
            color= 'rgb(93, 164, 214)',
            opacity= 0.8),
            textfont = dict(
                    size = 20),
            text= [key+': '+str(words[key]) for key in combi.keys()])
    fig_data2.append(trace_f2);

    layout_f2= go.Layout(
        title= name+"'s Tweet Words: Average Count",
            font=dict(size=18),
        hovermode= 'closest',
        xaxis= dict(
            title= 'Retweet Count',
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'Favorite Count',
            ticklen= 5,
            gridwidth= 2,
        ),
        showlegend= False
    )
    fig_f2 = go.Figure(data = fig_data2, layout=layout_f2)
    py.offline.plot(fig_f2, filename = out_dir + 'overall_average_words.html')
