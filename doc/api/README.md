# API Documentation

## /convert

#### Supported requests:
POST

#### Parameters:
Parameters must be sent as JSON objects (`application/json`).

| Parameter | Required? | Description                                                       | Datatype |
|-----------|-----------|-------------------------------------------------------------------|----------|
| query     | yes       | A number to convert.                                              | string   |
| language  | yes       | Must be `sux`. (Future releases will support additional scripts.) | string   |
| system    | no        | Optional: if specified, the query will be evaluated with the chosen number system. If no system is specified, the API will return a list of possible readings for the query. Allowed values are `date`, `cardinal`, `length`, `surface`, `volume`, `dry capacity`, `liquid capacity`, `weight`, and `bricks` | string   |

#### Returns:
A JSON object with the following fields:

| Parameter | Description                                             | Datatype |
|-----------|---------------------------------------------------------|----------|
| readings  | A list of possible readings for the given query string. | list     |

Each item in the list of readings is a JSON object with the following fields:

| Parameter    | Description                                                                                                                                                                                                                                         | Datatype |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| query        | The original query string.                                                                                                                                                                                                                          | string   |
| system       | The number system which gives this reading. One of `date`, `cardinal`, `length`, `surface`, `volume`, `dry capacity`, `liquid capacity`, `weight`, or `bricks`.                                                                                     | string   |
| value        | The value of the query string, as measured in an appropriate ancient unit.                                                                                                                                                                          | float    |
| unit         | The ancient unit used to measure the query string. For ease of comparison, all values from a given number system are evaluated with the same unit: e.g. "5(asz) ninda" and "1(asz) gi" will both be evaluated in "gi" (~3m) since both are lengths. | string   |
| modern\_value | The value of the query string, as measured in an appropriate modern unit.                                                                                                                                                                           | float    |
| modern\_unit  | The modern unit used to measure the query string. For ease of comparison, all values from a given number system are evaluated with the same unit: e.g. "5(asz) ninda" and "1(asz) gi" will both be evaluated in metres since both are lengths.      | string    |

#### Example:
Query:
```json
{
  "query": "1(u) sar",
  "language": "sux",
  "system":, "surface"
}
```

Reponse:
```json
{
  "readings": [
    {
      "modern_unit": "m^2",
      "modern_value": 360,
      "query": "1(u) sar",
      "system": "surface",
      "unit": "gin2",
      "value": 600
    }
  ]
}
```

We see that the number '1(u) sar' equals 600 gin2, which is approximately 360 m^2.

## /canparse

#### Supported requests:
POST

#### Parameters:
Parameters must be sent as JSON objects (`application/json`).

| Parameter | Required? | Description                                       | Datatype |
|-----------|-----------|---------------------------------------------------|----------|
| query     | yes       | A string which might represent a number.          | string   |
| language  | yes       | Must be `sux`. (Future releases will support additional scripts.) | string   |
| greedy    | no        | Boolean specifying whether to greedily parse missing signs. If `true`, broken and missing signs will be ignored, so e.g. "1(u) ... sze" will be considered a valid number. Defaults to `false`. | bool     |

#### Returns:
A JSON object with the following fields:

| Parameter | Description                                             | Datatype |
|-----------|---------------------------------------------------------|----------|
| bricks     | Boolean specifying whether the query can be evaluated as a volume of bricks.  | bool     |
| cardinal  | Boolean specifying whether the query can be evaluated as a cardinal number. | bool     |
| date      | Boolean specifying whether the query can be evaluated as a date. | bool     |
| dry capacity  | Boolean specifying whether the query can be evaluated as a dry capacity measure.  | bool     |
| liquid capacity | Boolean specifying whether the query can be evaluated as a liquid capacity measure. | bool     |
| length | Boolean specifying whether the query can be evaluated as a length. | bool     |
| surface | Boolean specifying whether the query can be evaluated as a surface area measurement.   | bool     |
| volume | Boolean specifying whether the query can be evaluated as a volume measurement. | bool     |
| weight | Boolean specifying whether the query can be evaluated as a weight. | bool     |

#### Example:
Query:
```json
{
  "query":, "1(iku) GAN2 1(u) sar",
  "language": "sux",
  "greedy": false
}
```

Reponse:
```json
{
  "bricks": false,
  "cardinal": false,
  "date": false,
  "dry capacity": false,
  "length": false,
  "liquid capacity": false,
  "surface": true,
  "volume": false,
  "weight": false
}
```

We see that the query can only be parsed as a surface area measurement.


## /commodify

#### Supported requests:
POST

#### Parameters:
Parameters must be sent as JSON objects (`application/json`).

| Parameter | Required? | Description                                                       | Datatype |
|-----------|-----------|-------------------------------------------------------------------|----------|
| cdli\_no   | no        | The CDLI number of a document to analyse for commodities, e.g. `P100839`.                         | string   |
| text      | no        | A string to analyse for commodities.                              | string   |

You must provide `text` or `cdli_no`, but not both.

#### Returns:
A JSON object with the following fields:

| Parameter | Description                                             | Datatype |
|-----------|---------------------------------------------------------|----------|
| entries   | A list of entries in the given text.                    | list     |

Each item in the list of entries is a JSON object with the following fields:

| Parameter    | Description                                                                                                                                                                                                                                         | Datatype |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| count        | The value of the object counted in this entry. A tuple where the first item is the original numeral string, and the second is a list of possible readings. See the documentation for the `/convert` endpoint for details on how readings are structured.    | [string, list] |
| words  | A list of the words which follow the numeral. Words annotated with `_COM` have been identified as counted objects (commodities). | string   |

#### Example:
Query:
```json
{
  "text":, "2(u) {gesz}ildag4 sir2-sir2-ra 6(asz@c) {gesz}giparx(KISAL)"
}
```

Reponse:
```json
{
  "entries": [
    {
      "count": [
        "2(u)",
        [
          {
            "modern_unit": "",
            "modern_value": 20,
            "query": "2(u)",
            "system": "cardinal",
            "unit": "",
            "value": 20
          },
          ...
        ]
      ],
      "words": [
        "{gesz}ildag4_COM",
        "sir2-sir2-ra"
      ]
    },
    {
      "count": [
        "6(asz)",
        [
          {
            "modern_unit": "",
            "modern_value": 6,
            "query": "6(asz)",
            "system": "cardinal",
            "unit": "",
            "value": 6
          },
          ...
        ]
      ],
      "words": [
        "{gesz}giparx(KISAL)_COM"
      ]
    }
  ]
}
```

In the first entry we see that "{gesz}ildag4" (poplar) is labeled as a commodity, but the modifying adjective (sir2-sir2-ra, "dense") is not. 

