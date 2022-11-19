Instructions on how to run :

Install kafka: https://kafka.apache.org/quickstart

Start kafka from terminal with Kraft

KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
bin/kafka-server-start.sh config/kraft/server.properties

Create a Topic in Kafka

bin/kafka-topics.sh --create --topic assignment --bootstrap-server localhost:9092

UnZip Assignment3 folder and open Question1 folder and run Scrapper.py file

Download Elasticsearch 8.5.1 (https://www.elastic.co/downloads/)

Open terminal where elasticsearch is installed and run "bin/elasticsearch"

Download kibana 8.5.1 (https://www.elastic.co/downloads/kibana)

Open terminal where kibana is installed and run "bin/kibana"


Now install logstash (https://www.elastic.co/downloads/logstash)

Now open terminal where logstash is installed and run this command "bin/logstash -f config/logstash-sample.conf"

Edit logstash-sample.conf file 

# Sample Logstash configuration for creating a simple
# Beats -> Logstash -> Elasticsearch pipeline.

input {
kafka 
{
bootstrap_servers => "localhost:9092"
topics => ["assignment"]
} 
}

output { 
elasticsearch  {
hosts => ["http://localhost:9200"]
index => "assignment"
workers => 1 
}
}

Now open terminal and run this command to create index "curl -X PUT "localhost:9200/assignment"

Now it's push data from kafka topic to elasticsearch and you will get the visualization on dashboard 
http://localhost:5601/app/home#/
