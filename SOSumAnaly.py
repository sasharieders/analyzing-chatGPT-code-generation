import csv
import nltk, openai, time, string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')


class preprocessSosum:
    def __init__(self):
        self.messages = []
        self.index = 1

    #this will read in answer.csv which comes from the SOSum dataset itself 
    def loadAnswers(self, csvFilePath):
        answersData = {
            'answerBody': [],
            'sentenceIndex': [],
            'answerID': [],
        }
        with open(csvFilePath, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists
            for row in reader:
                answerBody = row[0]
                sentenceIndex = row[1]
                answerID = row[2]
                answersData['answerBody'].append(answerBody)
                answersData['sentenceIndex'].append(sentenceIndex)
                answersData['answerID'].append(answerID)
        return answersData

    #this will read in the questions.csv which comes from the SOSum data itself
    def loadQuestions(self, csvFilePath):
        questionsData = {
            'questionID': [],
            'questionType': [],
            'questionBody': [],
            'corAnswerID': []
        }
        with open(csvFilePath, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                questionID = row[0]
                questionType = row[1]
                questionBody = row[3]
                corAnswerID = row[5]

                questionsData['questionID'].append(questionID)
                questionsData['questionType'].append(questionType)
                questionsData['questionBody'].append(questionBody)
                questionsData['corAnswerID'].append(corAnswerID)
        return questionsData
    
    #this will create a dictionary that contains the relevant information for us to analyze
    def createInputData(self, answersData,questionsData):
        inputData = {
        'questionID': [],
        'answerID': [],
        'questionBody':[],
        'answerBody':[], 
        'answerSummary':[]
        }
        for i in range(len(questionsData['corAnswerID'])):
            questionID = questionsData['questionID'][i]
            corAnswerID = questionsData['corAnswerID'][i]
            questionBody = questionsData['questionBody'][i]
            corAnswerID = corAnswerID.strip('[]')
            answerIDs = corAnswerID.split(',')
            inputData['questionID'].append(questionID)
            inputData['answerID'].append(answerIDs[0])
            inputData['questionBody'].append(questionBody)
            inputData['answerBody'].append('')
        for i in range(len(inputData['answerID'])):
            answerID = inputData['answerID'][i]
            #find which row has this answerID then append the answerbody[i] to that row
            index = answersData['answerID'].index(answerID)
            if index != -1:
                inputData['answerBody'][i] = answersData['answerBody'][index]
                sumSenInd = answersData['sentenceIndex'][index]
                answerSum = answersData['answerBody'][index].strip('[]').split(',')
                answerSum = [s.strip("'") for s in answerSum]
                sentences = answerSum.copy()
                sumSenInd = [int(ind.strip('[]')) for ind in sumSenInd.split(',') if ind.strip('[]')]
                answerSum = [sentences[j] for j in sumSenInd]
                inputData['answerSummary'] = answerSum
        return inputData
    
class summaryComp:
    def __init__(self, apiKey, prompt):
        self.apiKey = apiKey
        self.prompt = prompt
        self.messages = [{"role": "system", "content": self.prompt}]
        self.index = 1

    #first we need to ask chatGPT to generate a summary, that will be given by message
    def generateSummaryArray(self, apiKey, prompt, inputData):
        import time
        messages = [{"role": "system", "content": prompt}]
        comparisonArray = {
        'summary': [],
        'questionID': [],
        'SOSummary': []
        }
        messages.append({"role": "user", "content": "Question: "})
        for i in range(len(inputData['answerID'])):
            questionBody = inputData['questionBody'][i]
            messages.append({"role": "user", "content": questionBody})
            messages.append({"role": "user", "content": "Answer: "})
            answer = inputData['answerBody'][i]
            messages.append({"role": "user", "content": answer})
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            comparisonArray['summary'].append(completion.choices[0].message['content'])
            print(completion.choices[0].message['content'])
            comparisonArray['SOSummary'].append(inputData['answerSummary'][i])
            messages = [
                {"role": "system", "content": "Here is a question with an answer from Stack Overflow. Please summarize the answer using only text from the answer: "}
            ]
            time.sleep(20)
        return comparisonArray
    
    #this takes in the array that has the chatGPT and SOSum summaries and then cleans them
    def cleanArray(self, comparisonArray):
        cleanedArray = {
        'chatGPTSummary': [],
        'SOSumSummary': []
        }
        for i in range(len(comparisonArray)):
            SOSummary = comparisonArray[i]['SOSummary']
            SOSummary = self.cleanText(SOSummary)
            cleanedArray['SOSumSummary'].append(SOSummary)
            
            chatGPTSummary = comparisonArray[i]['chatGPTSummary']
            chatGPTSummary = self.cleanText(chatGPTSummary)
            cleanedArray['chatGPTSummary'].append(chatGPTSummary)
        return cleanedArray

    #this takes in a string and returns the cleaned text 
    def cleanText(self, text):
        text = text.lower()
        stopWords = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = nltk.word_tokenize(text)
        words = [lemmatizer.lemmatize(word) for word in words if word not in stopWords]
        cleanedText = ' '.join(words)    
        return cleanedText
