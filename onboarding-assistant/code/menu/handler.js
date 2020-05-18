"use strict";

const path = require("path");
const fuzzyaldrin = require("fuzzaldrin-plus");
const data = require(path.resolve(__dirname, "./data.json"));


module.exports.menu = async event => {
  console.log(event)
  let payload = JSON.parse(event.body.payload);
  if(payload.type == "block_suggestion") {
    let options = query(payload.value, ...payload.action_id.split(":")).map(
        item => {
          return {"value": item, "text": {"type": "plain_text", "text": item}}
        }
    );
    console.log(options)
    return {statusCode: 200, body: JSON.stringify({"options": options})};
  } else {
    return {statusCode: 400, body: "400"};
  }
};


function query(string, source, limit = undefined) {
  // Not implemented yet: dynamic (external) data sources.
  let results = fuzzyaldrin.filter(data[source], string);
  return results.slice(0, limit);
}
