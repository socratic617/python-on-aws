# API Design Checklist - Part 1

## Implement HTTP

- [ ] Use HTTP methods, i.e. GET, POST, DELETE, etc.
  - [ ] Use query parameters for filtering, sorting, and pagination in GET requests.
  - [ ] Use request body for POST and PUT requests.
- [ ] Return meaningful status codes indicating the nature of the request success or failure
- [ ] For GET requests, support pagination, sorting, and filtering using query parameters where appropriate

## Follow formal REST (largely covered by implementing HTTP "right")

- [ ] Uniform Interface
  - [ ] Use standard HTTP methods
  - [ ] Use standard HTTP status codes
  - [ ] Use standard HTTP headers
  - [ ] Implement HATEOAS (rarely done in practice)
- [ ] Stateless
  - [ ] Do not store client state on the server
- [ ] Client-Server decoupling
  - [ ] Ensure that the server is not dependent on details of the client.
        You could write tests from the perspective of a client that is unaware
        of the server's implementation details. This is a good testing practice
        anyway.
- [ ] Cacheable - Use caching headers where appropriate to limit requests made to the API server
- [ ] Layered System - Hide implementation details about the server, and services that the server calls out to, e.g. AWS S3 from the client

## Follow informal REST

- [ ] Use resource-oriented design, i.e. nouns for URLs and plural nouns for collections of resources. (e.g. `/users`, `/users/1`)

## Extra

- [ ] Do data validation / sanitation on the server side (Pydantic models are an excellent way to do this)
  - [ ] Think through what data validation is necessary for each endpoint, e.g. valid ranges, mutually exclusive parameters, regex patterns (such as for an email or IP address), etc.
- [ ] Implement unit tests from the perspective of a client that is unaware of the server's implementation details


