# bar plot: labels in first col, heights in second col

args = commandArgs(trailingOnly=TRUE)
if(length(args)==0){
  stop("csv_bplot.R [csv file name]");
}
d = read.csv(file=args[1], header= TRUE)
print(dim(d))
fields <- colnames(d)

print(length(d[,2]))
png(paste(args[1], "_bplot.png", sep=''))
barplot(d[,2],
	names.arg = d[,1], # bar labels
	main=fields[1], #paste(args[1]),
	xlab=c(""), #colnames(d)[1],
	ylab=colnames(d)[2],
	horiz=FALSE,
	las = 3)
dev.off()
