library(cumstats)
txs <- read.csv(file="txs.csv", header=TRUE, sep=",")
data <- read.csv(file="bids.csv", header=TRUE, sep=",")

new.hashtable <- function() {
    e <- new.env()
    list(set = function(key, value) assign(as.character(key), value, e),
         get = function(key) get(as.character(key), e),
         rm = function(key) rm(as.character(key), e))
}
ht <- new.hashtable()

for(i in 1:nrow(data[1])) {
	ht$set(data$block[i], data$time[i])
}


for(i in 1:nrow(txs[1])) {
	txs$time[i] = ht$get(txs$blockNumber[i])
}

# load data as time
d = as.POSIXct(txs$time, origin="1970-01-01", format="%s")
r <- round(range(d), "hours")

X11()
par(mfrow=c(3,1))
hist( txs$gasPrice, xlab="gas price [wei]", main="", ylab="", breaks=20)
mtext(paste("max=", max(txs$gasPrice), "min=", min(txs$gasPrice), "median=", median(txs$gasPrice), "mean=", mean(txs$gasPrice)), side = 3)
hist( txs$gas, xlab="gas", main="", ylab="", breaks=20)
mtext(paste("max=", max(txs$gas), "min=", min(txs$gas), "median=", median(txs$gas), "mean=", mean(txs$gas)), side = 3)
txfee = txs$gas*txs$gasPrice
hist( txfee, xlab="gas * gasPrice", main="", ylab="", breaks=20)
mtext(paste("max=", max(txfee), "min=", min(txfee), "median=", median(txfee), "mean=", mean(txfee)), side = 3)



invisible(readLines("stdin", n=1))
