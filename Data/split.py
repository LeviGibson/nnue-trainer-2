x = open("chessData.csv", "w")
xv = open("val_chessData.csv", "w")

infile = open("1.csv", 'r')

for id, line in enumerate(infile):
	if id < 500000:
		xv.write(line)
	else:
		x.write(line)
	if id % 100000 == 0:print(id)
