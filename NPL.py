#importing pandas, a open source library used for Data Analysis.
import pandas as pd  
#importing requests, used for send HTTP requests.
import requests
#importing BeautifulSoup from bs4, used for parsing the html document(Data Crawling / Data Scraping).
from bs4 import BeautifulSoup
#importnig Regexptokenizer from nltk, used for tokenizing the text based on some pattern, it is better than sent_tokenize and word_tokenize.
from nltk.tokenize import RegexpTokenizer 
#importing numpy, used while working with arrays.
import numpy as np

#Reading or openiing the Input excel file which contains the links as DataFrame using pandas.
df = pd.read_excel('Input.xlsx')

#Copying the URL's and its ID's into two seperate Lists.
li=[url for url in df['URL']]
li1=[url1 for url1 in df['URL_ID']]

#Now sending HTTP requests for all the links and storing it in a list(page), if succesfull it would return response<200>.
page=[]
for i in li:
    page.append(requests.get(i))
    
#Parsing the html page using BeautifulSoup('html.parser') and extracting its content using .content function.
for i in range(len(page)):
    page[i] = BeautifulSoup(page[i].content,'html.parser')
    
#Now extrating text as mentioned, i.e Only the article title and article text, leaving the header and footer.
#It is done by mentioning the class which contains the article title and article text, and only extracting its content using find method.
articles = []
for i in range(len(page)):
    ab=page[i].find('div',attrs= {"class":"td-post-content"})
    
    #The if statement is used to handle exception like page not found error or 404 error as few web pages are not loading. 
    if(ab!=None):  
        articles.append(ab.text)
    else:
        articles.append("e")
        
#Used to count personal noun in the texts.        
personal_nouns = []
personal_noun =['I', 'we','my', 'ours','and' 'us','My','We','Ours','Us','And'] 
for artcl in articles:
    ans=0
    for wrd in artcl:
        if wrd == 'US':
            pass
        if wrd in personal_noun:
            ans+=1
    personal_nouns.append(ans)

#Cleaning the text by replacing '\n','?',',','!' with ' '. 
for i in range(len(articles)):
    articles[i]= articles[i].replace('\n',' ').replace('?','.').replace(',','').replace('!','')
    
#Opening stopwords file which is the combined stopwords file.
with open('Stopwords_combined.txt','r') as stp_wrd:
    stpWrd = stp_wrd.read().lower()
stpLst= stpWrd.split('\n')
stpLst[-1:] = []

#Counting words and sentences in a web page.
art=[]
sent=[]
sentences=[]
Words_length=[]
ASL=[]
for i in range(len(articles)):
    articles[i] = articles[i].lower()
    tokenizer = RegexpTokenizer(r'\w+')
    
    #Dividing the text into words.
    tokens = tokenizer.tokenize(articles[i])
    
    #Dividing the text into sentences.
    sent=articles[i].split('.')
    
    #Counting Words
    Words_length.append(len(tokens))
    
    #Counting Sentences
    sentences.append(len(sent))
    
    #Calculating Average sentence Length(ASL)
    ASL.append(Words_length[i]/sentences[i])
    
    #Cleaning the text by removing the stopwords.
    art.append(list(filter(lambda token: token not in stpLst, tokens)))
    
    #Creating seperate excel file for the cleaning text.
    df2=pd.DataFrame(art[i])
    
    #Naming the files according to the URL_ID's.
    df2.to_excel(str(li1[i])+'.xlsx',index=False)
    
#Opening positive words file.
with open('positive-words.txt','r') as pos_file:
    poswrds=pos_file.read().lower()
posLst=poswrds.split('\n')

#Opening negative words file.
with open('negative-words.txt','r') as neg_file:
    negwrds=neg_file.read().lower()
negLst=negwrds.split('\n')

#Counting Negative Words.
neg_score = [0]*len(art)
for i in range(len(art)):
    for wrd in negLst:
        for l in art[i]:
            if l==wrd:
                neg_score[i]-=1
    neg_score[i]=neg_score[i]*-1

#Counting Positive Words.
pos_score = [0]*len(art)
for i in range(len(art)):
    for wrd1 in posLst:
        for l1 in art[i]:
            if l1==wrd1:
                pos_score[i]+=1
                
#Pushing the scores into the dataframe.
df['POSITIVE SCORE']=pos_score
df['NEGATIVE SCORE']=neg_score

#Calculating the polarity score according to the given formula.
df['POLARITY SCORE'] = (df['POSITIVE SCORE']-df['NEGATIVE SCORE'])/ ((df['POSITIVE SCORE'] +df['NEGATIVE SCORE']) + 0.000001)

#Storing the length of Cleaned words in a list.
Total_cleaned_Words=[]
for i in range(len(art)) :
    Total_cleaned_Words.append(len(art[i]))

#Converting the list into numpy array, which is much faster than lists.
words_cleaned = np.array(Total_cleaned_Words)

#Calculating Subjectivity score according to the given formulae.
df['SUBJECTIVITY SCORE'] = (df['POSITIVE SCORE']+df['NEGATIVE SCORE'])/ ((words_cleaned )+ 0.000001)

#Storing Average Sentence Length in the dataframe.
df['AVG SENTENCE LENGTH'] =ASL

#Counting Complex words and Sylabble Words according to the given criteria.
complex_words = []
sylabble_counts = []
SPW=[]
for article in articles:
    sylabble_count=0
    d=article.split()
    ans=0
    for word in d:
        count=0
        for i in range(len(word)):
            if(word[i]=='a' or word[i]=='e' or word[i] =='i' or word[i] == 'o' or word[i] == 'u'):
                count+=1
            if(i==len(word)-2 and (word[i]=='e' and word[i+1]=='d')):
                count-=1
            if(i==len(word)-2 and (word[i]=='e' and word[i]=='s')):
                count-=1
        sylabble_count+=count    
        if(count>2):
            ans+=1
    sylabble_counts.append(sylabble_count)
    complex_words.append(ans)
    
#Storing the Counts as array format using numpy.
complex_words=np.array(complex_words)
Words_length=np.array(Words_length)

#Calculating and Storing in dataframes according to the formula and definition of the variable.
df['PERCENTAGE OF COMPLEX WORDS'] = complex_words/Words_length
df['FOG INDEX'] = 0.4 * (df['AVG SENTENCE LENGTH'] + df['PERCENTAGE OF COMPLEX WORDS'])
df['AVG NUMBER OF WORDS PER SENTENCES'] = df['AVG SENTENCE LENGTH']
df['COMPLEX WORD COUNT']=complex_words
df['WORD COUNT'] = Words_length

SPW = np.array(sylabble_counts)
df['SYLLABLE PER WORD'] = ((SPW)/(df['WORD COUNT']))

df['PERSONAL PRONOUN'] = personal_nouns

#Counting Characters in a word.
total_characters = []
for article in articles:
    characters = 0
    for word in article.split():
        characters+=len(word)
    total_characters.append(characters) 
    
#Calculating the average word length (AWL) in a web page.
awl=[]
for i in range(len(articles)):
    awl.append(total_characters[i]/Words_length[i])
     
#Storing AWL in dataframe.
df['AVG WORD LENGTH'] = awl

#Creating the final Output file.
df.to_excel('Output.xlsx',index=False)

#By ANAND BHATTACHARJEE