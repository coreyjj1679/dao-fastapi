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
      "proposer": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
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

  - `POST '/proposals'`
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

- vote by proposal id

  - `POST '/proposals/{proposal_id}/vote'`
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

- get the list of votes by proposal id

  - `GET '/proposals/{proposal_id}/votes'`
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

- get vote results by proposal id
  - `GET '/proposals/{proposal_id}/results'`
  - params:
    - `proposal_id`
  - response:
  ```
  {
    "proposal_id": "e5f62eb39d1747e68eb252d43dc1db5d",
    "# of votes": 6,
    "yes": 6,
    "no": 0,
    "winner": "yes"
  }
  ```

### Token-Weight Proposals

- get the list of proposals

  - `GET '/proposals/token_weight'`
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
      "end_timestamp": 1735734714.169108,
      "token_address": '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef'
    }
  ]
  ```

- get the proposal by id

  - `GET '/proposals/token_weight/{proposal_id}'`
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
      "end_timestamp": 1735734714.169108,
      "token_address": "0x8affc29b10b8476aad5e1bba96b7d977"
    },
    ...
  ]
  ```

- create token weight proposal

  - `POST '/proposals/token_weight'`
  - params:
    - `title`
    - `description`
    - `start_timestamp`
    - `duration`
    - `token_address`
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
      'token_address': '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
      "status": "active"
    }
    ...
    ```

### Token-Weight Votes

- vote by proposal id

  - `POST '/proposals/token_weight/{proposal_id}/vote'`
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
    "option": "yes",
    "weight": 0.0,
    }
  ```

- get the list of votes by proposal id

  - `GET '/proposals/token_weight/{proposal_id}/votes'`
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
      "option": "yes",
      "weight": 0.0,
    }
  ]
  ```

- get vote results by proposal id
  - `GET '/proposals/{proposal_id}/results'`
  - params:
    - `proposal_id`
  - response:
  ```
  {
    "proposal_id": "e5f62eb39d1747e68eb252d43dc1db5d",
    "total_voting_power": 6,
    "yes": 6,
    "no": 0,
    "winner": "yes"
  }
  ```
