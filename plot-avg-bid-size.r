library(cumstats)
X11()
data <- read.csv(file="bids.csv", header=TRUE, sep=",")
# set margins
par(mar=c(5,4,4,5)+.1)

# load data as time
d = as.POSIXct(data$time, origin="1970-01-01", format="%s")
r <- round(range(d), "hours")

# plot cumulative bids
plot(d, cumsum(data$amount), type="lines", xlab="time [h]", ylab="bid sum [eth]", xaxt="n")

mtext(paste("mean=", mean(data$amount), "median=", median(data$amount)), side = 3)



# plot bid amount
par(new=TRUE)
mean_bid = cummean(data$amount)
plot(d,  mean_bid, xaxt="n", yaxt="n", type="lines", xlab="", ylab="", col="red")

# plot x axis
r <- as.POSIXct(round(range(d), "hours"))
axis.POSIXct(1, at = seq(r[1], r[2], by = "hour"), format = "%H")

# plot right y axis
axis(4, at=pretty(mean_bid))
mtext("cumulative mean [eth]", side=4, line=3)
invisible(readLines("stdin", n=1))
