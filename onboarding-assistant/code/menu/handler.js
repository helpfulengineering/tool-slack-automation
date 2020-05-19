"use strict";

const path = require("path");
const fuzzyaldrin = require("fuzzaldrin-plus");
const data = require(path.resolve(__dirname, "./data.json"));


module.exports.menu = async event => {
  let payload = JSON.parse(event.body.payload);
  if(payload && payload.type == "block_suggestion") {
    return {"options":
        query(payload.value, ...payload.action_id.split(":")).map(item => {
            return {
                "text": {"type": "plain_text", "text": item},
                "value": item
            }
        })
    };
  } else {
    return "400";
  }
};


function query(string, source, limit = undefined) {
  // Not implemented yet: dynamic (external) data sources.
  let results = string ? fuzzyaldrin.filter(data[source], string) : data[source];
  return results.slice(0, limit);
}
