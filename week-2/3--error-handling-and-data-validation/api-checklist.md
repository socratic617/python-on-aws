# API Design Checklist - Error Handling

## Implement HTTP

- [ ] Return error HTTP status codes. [FastAPI Guide](https://fastapi.tiangolo.com/tutorial/handling-errors/#raise-an-httpexception-in-your-code)

## Error handling

**Principle:** NEVER let your API crash. Always handle exceptions and return a meaningful client-facing response to the client that

- helps them understand what went wrong and how to fix it
- does not reveal internal implementation details of the API

- [ ] Globally catch errors and return a meaningful response to the user. [FastAPI Guide](https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers)
  - [ ] Catch `Exception` as `500 Internal Server Error`
  - [ ] Catch `pydantic.ValidationError` as `422 Unprocessable Entity`
- [ ] In error messages, do not reveal implementation details to the user about what went wrong. 
  - **Bad:** "the file was not found in the S3 bucket at path <...>". 
  - **Good:** "the file requested was not found at path <...>."
- [ ] **(not in this section)** Include a request ID in error messages to give to "the support team" (you). Include it in logs.

## Data validation

**Principle:** assume all API inputs are malicious until proven otherwise.

- [ ] Validate API inputs
  - [ ] Query parameters (for appropriate HTTP methods)
  - [ ] Request body (for appropriate HTTP methods)
  - [ ] Request headers
  - [ ] Path parameters
- [ ] Unit test validation logic

Use Pydantic models wherever possible.

1. [ ] Prefer JSON schema validation wherever possible, e.g.
   ```python
    class GetPeopleRequest(BaseModel):
        min_age: int = Field(..., json_schema_extra={"minimum": 0})
    ```
2. [ ] Use Pydantic validators for more complex validation. [model_validator guide](https://docs.pydantic.dev/latest/concepts/validators/#model-validators)
   ```python
    class GetPeopleRequest(BaseModel):
        min_age: int = Field(..., json_schema_extra={"minimum": 0})
        max_age: int = Field(..., json_schema_extra={"minimum": 0})
        
        @model_validator(mode="before")
        def validate_age_range(cls, values: dict):
            if values["min_age"] > values["max_age"]:
                raise ValueError("min_age must be less than or equal to max_age")
    ```

## Document your API contract

**Principle:** include as much detail as you can in your OpenAPI spec so that

1. Users can understand your endpoints without needing to hit the API
2. Client and server code generated from the OpenAPI spec has good
   1. autocompletion - for **types** and **descriptions**
   2. function and model names
   3. organization, i.e. functions are grouped

Use OpenAPI (formerly Swagger) to document your API. Include:

- [ ] API-level metadata
  - [ ] A title
  - [ ] A client-facing, markdown description of the API that does not expose imlementation details
  - [ ] API version (ideally the semantic version)
  ```python
  app = FastAPI(
      title="Petstore API",
      description="This is a simple API",
      version=__version__  # e.g. "0.1.0"
  )
  ```

- [ ] For every **API route**
  - [ ] Add a client-facing markdown docstring that does not discuss internal implementation details. [FastAPI guide](https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#advanced-description-from-docstring)
  - [ ] Document the request inputs
    - [ ] Payload (if applicable for the HTTP method), [FastAPI guide](https://fastapi.tiangolo.com/tutorial/body/)
    - [ ] Query parameters, [FastAPI guide](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
    - [ ] Request headers, [FastAPI guide](https://fastapi.tiangolo.com/tutorial/header-params/)
  - [ ] For every response HTTP status code [FastAPI guide](https://fastapi.tiangolo.com/advanced/additional-responses/), [OpenAPI guide](https://swagger.io/docs/specification/describing-responses/)
    - [ ] Document the response model(s)
    - [ ] Document the content ([MIME](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types)) type(s)
    - [ ] Include at least one example response
      ```python
      class PutFileResponse(BaseModel):
          """Response model for `PUT /files/:filePath`."""
          success: bool
          message: str
      
          model_config = ConfigDict(
            json_schema_extra={"examples": [
                {
                  "success": True, 
                  "message": "File uploaded successfully"
                }
              ]
            }
          )
      ```
- **Schemas** (pydantic models in request/response)
  - [ ] Decide if you will use `snake_case` or `camelCase` in JSON request/response payloads. 
    - Be consistent and stick to one
    - Useful: `pydantic.alias_generators.to_camel` in `model_config`, [Pydantic guide](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.loc_by_alias)
  - [ ] Include a docstring in each Pydantic Model
    ```python
    class PutFileResponse(BaseModel):
        """Response model for `PUT /files/:filePath`."""
    ```
  - [ ] Include a description for each field 
    ```python
    Field(..., description="...")
    ```
- [ ] Give each endpoint a unique "operation ID". This influences the function name in the generated client/server code. [FastAPI Guide 1](https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid)
  ```python
  @app.get("/files/{file_path}", operation_id="get_file")
  def get_file(file_path: str):
      ...
  ```
- [ ] Use tags to group endpoints. Influences the module/folder functions are grouped in in the generated client/server code.
  ```python
  ROUTER = APIRouter(tags=["files"])

  ROUTER.get("/files/{file_path}", ...)
  def get_file(file_path: str):
      ...
  ```
