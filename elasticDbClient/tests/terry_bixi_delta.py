curl -XPUT -H 'Content-Type: application/json' "localhost:9200/usage?pretty" -d'{
  "settings" : {
    "number_of_shards" : 3
  }
  "mappings": {
    "usage": { 
      "_all":       { "enabled": false  }, 
      "properties": { 
        "timestamp":{ "type": "date", "format" : "epoch_second" }, 
        "coordinates": { "type": "geo_point"  }, 
        "station_name": { "type": "string" },
        "delta" : { "type" : "integer"}
      }
    }
  }
}'

