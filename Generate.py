from CsvProcessor import process_line

infile = open("chessData.csv")
infile.readline()

for line in infile:
    print(line)
    line = process_line(line)
