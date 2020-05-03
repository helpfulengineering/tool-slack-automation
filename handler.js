"use strict";
const querystring = require("querystring");
const fuzzyaldrin = require("fuzzaldrin-plus");
const data = require("./data.json");

module.exports.search = async event => {
  let payload = JSON.parse(querystring.parse(event.body).payload)
  let [list, limit] = (
    payload.action_id.includes(":")
    ? payload.action_id.split(":")
    : [payload.action_id, 10]
  );
  if(payload.type == "block_suggestion" && list in data) {
    let matches = fuzzyaldrin.filter(
      data[list],
      payload.value
    );
    let options = matches.map(item => {
      return {"text": item, "value": item}
    });
    return {
      statusCode: 200,
      body: JSON.stringify(
        {"options": options.slice(0, limit)}
      )
    };
  } else {
    return {
      statusCode: 404,
      body: "404"
    };
  }
};
