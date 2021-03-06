"use strict";

const path = require("path");
const AWS = require("aws-sdk");
const fuzzyaldrin = require("fuzzaldrin-plus");
const data = require(path.resolve(__dirname, "./data.json"));
const { Client, Status } = require("@googlemaps/google-maps-services-js");

function getConfiguration() {
  return new Promise((resolve) => {
    if (!global.configuration) {
      const client = new AWS.SecretsManager({
        region: process.env.AWS_DEFAULT_REGION,
      });
      client.getSecretValue({ SecretId: process.env.SECRET_ARN }, function (
        error,
        data
      ) {
        if (error) console.log(error);
        else global.configuration = JSON.parse(data.SecretString);
        resolve(global.configuration);
      });
    } else {
      resolve(global.configuration);
    }
  });
}

module.exports.menu = async (event) => {
  if (event.source === "serverless-plugin-warmup") {
    return "";
  }
  let payload = JSON.parse(event.body.payload);
  if (payload && payload.type == "block_suggestion") {
    return {
      options: (
        await query(payload.value, ...payload.action_id.split(":"))
      ).map((item) => {
        return {
          text: { type: "plain_text", text: item.text },
          value: item.value,
        };
      }),
    };
  } else {
    return "400";
  }
};

async function query(string, source, limit = undefined, session = undefined) {
  if (source == "location") {
    var results = await googleMapsQuery(string, session);
  } else {
    var results = (string
      ? fuzzyaldrin.filter(data[source], string)
      : data[source]
    ).map((item) => {
      return { text: item, value: item };
    });
  }
  return results.slice(0, limit);
}

async function googleMapsQuery(string, session) {
  const client = new Client({});
  var place = await client.placeAutocomplete({
    params: {
      input: string,
      sessiontoken: session,
      types: "(regions)",
      key: (await getConfiguration()).google_maps_token,
    },
    timeout: 1000, // milliseconds
  });
  if (place.data.status === Status.OK) {
    return place.data.predictions.map((prediction) => {
      return { value: prediction.reference, text: prediction.description };
    });
  } else {
    console.log(place.data.error_message);
  }
}
