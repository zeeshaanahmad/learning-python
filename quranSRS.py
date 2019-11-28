import ezsheets
import math
import pprint
import datetime
import dateparser


def addRevision(date, page, wordMistakes, lineMistakes, currentInterval):
    None


def getScore(wordMistakes, lineMistakes):
    return wordMistakes * 1 + lineMistakes * 4


def getNextInterval(page,score, currentInterval):
    # Convert score into an interval delta
    if score == 0:  # Perfect page
        intervalDelta = +3
    elif score == 1:  # 1 Word Mistake
        intervalDelta = +2
    elif score <= 3:  # 3 Word Mistakes
        intervalDelta = +1
    elif score == 4:  # 1 Line Mistake
        intervalDelta = 0
    elif score <= 8:  # 2 Line Mistakes
        intervalDelta = -1
    elif score <= 12:  # 3 Line Mistakes
        intervalDelta = -2
    elif score <= 20:  # 5 Line Mistakes
        intervalDelta = -3
    elif score <= 30:  # 7.5 Line Mistakes - Half a page
        intervalDelta = -5
    else:  # More than half a page
        intervalDelta = -7

    nextInterval = currentInterval + intervalDelta

    # If Score is 8 or more (2 line mistakes or more), then we have to restrict the max Interval
    if score == 4:  # 1 Line Mistake - 40 days max
        maxInterval = 40
    elif score <= 8:  # 2 Line Mistakes - 30 days/1 month max
        maxInterval = 30
    elif score <= 12:  # 3 Line Mistakes - 3 weeks max
        maxInterval = 21
    elif score <= 20:  # 5 Line Mistakes - 2 weeks max
        maxInterval = 14
    elif score <= 30:  # 7.5 Line Mistakes - Half a page - 1 week max
        maxInterval = 7
    else:  # More than half a page - 3 days max
        maxInterval = 3

    print(
        f"page={page}, score = {score}, currentInterval={currentInterval}, intervalDelta={intervalDelta}, nextInterval={nextInterval}, maxInterval={maxInterval}"
    )
    return nextInterval if maxInterval > nextInterval else maxInterval

def addRevision(revisionDate,page,wordMistakes,lineMistakes,currentInterval):
    score = getScore(wordMistakes, lineMistakes)
    nextInterval = getNextInterval(page,score, currentInterval)

    dueDate = revisionDate + datetime.timedelta(days=nextInterval)

    revisionList.append( {
        "revisionDate": revisionDate,
        "page": page,
        "wordMistakes": wordMistakes,
        "lineMistakes": lineMistakes,
        "score": score,
        "currentInterval": currentInterval,
        "nextInterval": nextInterval,
        "dueDate": dueDate,
    })

# Get the first sheet that contains the form responses for Quran Review data
reviewSheet = ezsheets.Spreadsheet('114LWy42iuyzIfKFrg-egp2o6jT-2XrnkzrYFSqmweOE')[0]
rows = reviewSheet.getRows(2)
#print(rows)
#rows = [
#    ["11/12/2019 10:31:49", "418", "1", "", ""],
#    ["11/12/2019 14:24:29", "469", "2", "0", "1"],
#]

rows

revisionList = []

for index, row in enumerate(rows):
    if row[0] != "":
        # Assign the columns to proper variable names
        # revisionDate = dt.datetime.strptime(row[0],'%m/%d/%Y %H:%M:%S')
        # No need to mention format string with dateutil.parser
        revisionDate = dateparser.parse(row[0]).date()
        page = row[1]

        # since empty string can be there, we can ask int function to return 0 if it finds an empty string
        wordMistakes = int(row[2] or 0)
        lineMistakes = int(row[3] or 0)
        currentInterval = int(row[4] or 0)

        if page.isdecimal():
            addRevision(revisionDate,page,wordMistakes,lineMistakes,currentInterval)
        else:
            print("page is not number:", page)
            # Get the start and end page number from the combined string which is in this format "420-425"
            startPage,endPage = page.split("-")
            #Now parse the page Numbers
            startPage = int(startPage or 0)
            endPage = int(endPage or 0)
            for i in range(startPage, endPage+1):
                addRevision(revisionDate,str(i),wordMistakes,lineMistakes,currentInterval)

len(revisionList)

pageSummaryMap ={}
pageDueMap ={}

for rev in revisionList:
    page = rev['page']
    dueDate = rev['dueDate']

    if page in pageSummaryMap:
        print("page found:",page)
        pageMapCurrent=pageSummaryMap.get(page)
        pageMapCurrent["dueDate"]=dueDate
        revisionCount = pageMapCurrent["revisionCount"]
        totalScore = pageMapCurrent["averageScore"]*revisionCount + rev['score']

        pageMapCurrent["revisionCount"] = revisionCount + 1
        pageMapCurrent["averageScore"] = totalScore/(revisionCount + 1)
        pageMapCurrent["interval"] = rev['nextInterval']

    else:
        newPageMap={
        #"page":page,
        "dueDate":dueDate,
        "revisionCount":1,
        "averageScore":rev['score'],
        "interval":rev['nextInterval']
        }
        pageSummaryMap.setdefault(page,newPageMap)

    pageDueMap[page]=dueDate

len(pageSummaryMap)

dueDateList = sorted(pageDueMap.values())

dueDateMap ={}
for dueDate in dueDateList:
    dueDateMap[dueDate] = []

dueDateMap

for page in pageSummaryMap.keys():
    dueDate = pageSummaryMap[page]['dueDate']
    dueDateMap[dueDate].append(page)
dueDateMap

today = datetime.date.today()

pagesDueList = []
for dueDate in dueDateMap.keys():
    if dueDate <= today:
        for duePage in dueDateMap[dueDate]:
            pagesDueList.append(duePage)


sorted(pagesDueList)

outputSS = ezsheets.Spreadsheet('1rHQ5WmyFz79sG8W2pNZmr6AJDuLuQEeOjSahPyPcb5o')

columnNames = list(next(iter(pageSummaryMap.values())).keys())

columnNames.insert(0,'page')

print(columnNames)

outputSheet = outputSS[0]
outputSheet.updateRow(2, ['4175', '2019-11-10', '1', '9', '-2'])

#First write the due pages in the first sheet
outputSheet = outputSS[0]

outputSheet.updateRow(1, columnNames)
for index, page in enumerate(sorted(pagesDueList)):
    outputRow = [page]
    for value in pageSummaryMap.get(page).values():
        outputRow.append(str(value))
    print(outputRow)
    #Google sheet's row number starts at 1. First row is the column name. Hence we have start at row 2
    outputSheet.updateRow(index + 2, outputRow)

#Then write the all pages in the second sheet
outputSheet = outputSS[1]
outputSheet.updateRow(1, columnNames)

pagesList = sorted(list(pageSummaryMap.keys()))

for index, page in enumerate(pagesList):
    outputRow = [page]
    for value in pageSummaryMap[page].values():
        outputRow.append(str(value))
    print(outputRow)
    outputSheet.updateRow(index + 2, outputRow)
