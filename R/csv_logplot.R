# plot points, with best fit, from csv (two col)
# csv_logplot is same script with log transformation?

args = commandArgs(trailingOnly=TRUE)
if(length(args)==0){
  stop("csv_plot.R [csv file name]");
}
d = read.csv(file=args[1], header= TRUE)
fields <- colnames(d)
png(paste(args[1], "_plot.png", sep=''))

dt <- (log(d + exp(1)) - 1)
l <- lm(dt) #l <- lm(dt)
print(l)
# plot(l): LOOK AT THIS

r_sq <-summary(l)$r.squared
print(r_sq)

plot(dt[,1] ~ dt[,2], xlab=paste("f(",fields[2],")"), ylab=paste("f(", fields[1], ")"))
titl <- paste("f(", fields[1], ") vs f(", fields[2], ") with f(*) =log((*) + e) -1)")

print(l)
print(l[0])
print(l[1])
abline(l, col="red")#l$coefficients[0], l$coefficients[1], col="red")

legend("topright", bty="n", legend=paste("r^2 =", format(r_sq, digits=4)), col="red")
title(main = titl)
dev.off()

write.csv(r_sq, paste(args[1], "_rsq.txt", sep=''))
