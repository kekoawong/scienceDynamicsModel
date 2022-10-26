import pickle
import csv

def convertToCSV(infile, outfile):
    with open(infile, "rb") as fileObj:
        [distrib1, distrib2Obj, distrib3, numAuthors, numPapers, numTopics] = pickle.load(fileObj)
    print(f'loaded data from {infile}')
    
    # open csv file
    typeNames = list(distrib2Obj.keys())
    typeVals = list(distrib2Obj.values())
    len1 = len(distrib1)
    len2 = len(typeVals[0])
    len3 = len(typeVals[1])
    len45 = len(distrib3[0])
    with open(outfile, 'w') as fileObj:
        write = csv.writer(fileObj)
        write.writerow(["Number of Authors:", numAuthors])
        write.writerow(["Number of Papers:", numPapers])
        write.writerow(["Number of Topics:", numTopics])
        write.writerow(["degree-density-values", f'credit-distrib-{typeNames[0].lower()}', f'credit-distrib-{typeNames[1].lower()}', "percent-marg-x", "avg-credit-y"])
        for rowNum in range(max(len1, len2, len3, len45)):
            cell1 = None if rowNum >= len1 else distrib1[rowNum]
            cell2 = None if rowNum >= len2 else typeVals[0][rowNum]
            cell3 = None if rowNum >= len3 else typeVals[1][rowNum]
            cell4 = None if rowNum >= len45 else distrib3[0][rowNum]
            cell5 = None if rowNum >= len45 else distrib3[1][rowNum]
            write.writerow([cell1, cell2, cell3, cell4, cell5])
    print(f'Completed writing to {outfile}')

convertToCSV('pickle-outputs/model-1.pi', 'csv-outputs/model-1.csv')
convertToCSV('pickle-outputs/model-2.pi', 'csv-outputs/model-2.csv')
convertToCSV('pickle-outputs/model-3.pi', 'csv-outputs/model-3.csv')
