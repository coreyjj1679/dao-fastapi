# DAO Management Backend

## Environment

1. `Python 3.12.1`
2. [FastAPI cli](https://fastapi.tiangolo.com/fastapi-cli/)

## Setup Instructions

1. Clone the Repository

```
$ git clone https://github.com/coreyjj1679/dao-fastapi
$ cd dao-fastapi
```

2. Setup venv

```
$ python3 -m venv venv
$ source venv/bin/activate
```

3. Install dependencies

```
$ pip install -r requirements.txt
```

## Local development

```
$ fastapi dev app/main.py --port <PORT_NUMBER>
```

## Test

```
$ pytest app/tests/**.py
```

## Sign message

```
python3 sign.py <NONCE>
```

## API Specifications

### Authentication

- Health check
  - `GET /`
  - response:
  ```
   {"message": "OK"}
  ```

### Authentication

- Request a Nonce
  - `POST /auth/request-nonce`
  - response:
  ```
  { nonce: "<NONCE>"}
  ```
- Authenticate User

  - `POST /auth/login`
  - params:
    - `wallet_address`: ethereum address of the user
    - `signed_message`: message signed generated from `auth/request-nonce` endpoint
    - `signauture`: signature retrived after calling `signature().hex()`
  - response:

  ```
  { token: "<JWT_TOKEN>"}
  ```

- Check session

  - responses:

  ```
  {
    wallet_address: "<WALLET_ADDRESS>",
    expires: <EXPIRES_TIMESTAMP
  }
  ```

### Proposals

- get the list of proposals

  - `GET '/proposals'`
  - response:

  ```
  [
    {
      "title": "Proposal1",
      "description": "Hello World",
      "created_timestamp": 1735648314.169108,
      "status": "active",
      "proposal_id": "8affc29b10b8476aad5e1bba96b7d977",
      "proposer": "0x7a4AEbb76F721DcBBE08ed3d4787BFcD3848D53C",
      "start_timestamp": 1735648314.169108,
      "end_timestamp": 1735734714.169108
    }
  ]
  ```

- get the proposal by id

  - `GET '/proposals/{proposal_id}'`
  - params:
    - `proposal_id`: id of the proposal
  - response:

  ```
  [
    {
      "title": "Proposal1",
      "description": "Hello World",
      "created_timestamp": 1735648314.169108,
      "status": "active",
      "proposal_id": "8affc29b10b8476aad5e1bba96b7d977",
      "proposer": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
      "start_timestamp": 1735648314.169108,
      "end_timestamp": 1735734714.169108
    },
    ...
  ]
  ```

- create proposal

  - `GET '/proposals/{proposal_id}'`
  - params:
    - `title`
    - `description`
    - `start_timestamp`
    - `duration`
  - response:

    ```
    {
      "proposal_id": "string",
      "title": "string",
      "description": "string",
      "proposer": "string",
      "created_timestamp": 0,
      "start_timestamp": 0,
      "end_timestamp": 0,
      "status": "active"
    }
    ...
    ```

### Votes

- get the list of vote by proposal id

  - `GET '/proposals/{proposal_id}/results'`
  - params:
    - `proposal_id`
  - response:

  ```
  [
    {
    "vote_id": "string",
    "proposal_id": "string",
    "voter_address": "string",
    "voted_timestamp": 0,
    "option": "yes"
    }
  ]
  ```

- get the list of vote by proposal id

  - `POST '/proposals/{proposal_id}/votes'`
  - params:
    - `proposal_id`
    - `option`
  - response:

  ```
  {
    "vote_id": "string",
    "proposal_id": "string",
    "voter_address": "string",
    "voted_timestamp": 0,
    "option": "yes"
  }
  ```
