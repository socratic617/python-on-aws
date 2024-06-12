# API Design Checklist - Part 2

## Implement HTTP

- [ ] Error handling
  - [ ] Return meaningful, precise status codes indicating the nature of the request success or failure.

## Error handling

- [ ] NEVER let your API crash without sending a meaningful error response to the user so that they can debug. Globally handle all exceptions.
  - [ ] In error messages, do not reveal implementation details to the user about what went wrong. Bad: "the file was not found in the S3 bucket at path <...>". Good: "the file requested was not found at path <...>."
  - [ ] In error messages, give a request ID that the user can use to refer to the error when contacting support. They will use this to look up the exact error logs which have the implementation details.

## Document your API contract

Use OpenAPI (formerly Swagger) to document your API. Include:

- [ ] A description of the API
- [ ] Request and response schemas
- [ ] Example requests and responses, including
  - [ ] At least one example response for every HTTP status code returned
    - [ ] Include an example error message in the example
- [ ] Decide if you will use `snake_case` or `camelCase` in JSON request/response payloads. Be consistent and stick to one.

## Extra

- [ ] Do data validation / sanitation on the server side (think Pydantic models)
- [ ] Implement unit tests from the perspective of a client that is unaware of the server's implementation details

