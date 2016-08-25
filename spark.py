from pyspark import SparkContext
from pyspark.sql import SQLContext
import sys
from operator import add

# create SPARK and SQL contexts
sc = SparkContext(appName="MBR")
sqlContext = SQLContext(sc)

# web logs stored in AWS bucket below
bucket = 'lippe-mbr-elb'
prefix = "AWSLogs/933939612720/elasticloadbalancing/*/*/*/*"
filename = "s3n://{}/{}".format(bucket, prefix)

# resilient distributed data set
rdd = sc.textFile(filename)

def parsedUri(logEntry, columnIndex, splitToken):
    parts = logEntry.split(' ')[columnIndex].split(splitToken)
    # return the requestUri, e.g. product.html
    return parts[0]
 
file_in = rdd
pageList = file_in.map(lambda row: parsedUri(row, 2, ":"))

# set count 1 per request page
# e.g. product.html, 1
pageMap = pageList.map(lambda w: (w,1))

# reduce phase - sum count all request url in pageMap
pageReducedMap = pageMap.reduceByKey(add)

sortedMap = pageReducedMap.map(lambda x: (x[1], x[0])).sortByKey(False)

### reverse the key and number
sortedMap = sortedMap.map(lambda x:(x[1], x[0]))

# write back to S3 via dataframe
df = sqlContext.createDataFrame(sortedMap, ["source", "hits"])
filename = "s3n://lippe-mbr-elb/parsed-output2"

# create 5 partitions (output files)
df = df.repartition(5)
df.write.mode('overwrite').json(filename)
