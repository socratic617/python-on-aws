# Assignment: Implement initial Files API endpoints

In this exercise, you will implement the following basic REST API endpoints for the Files API:

- `GET /files`: List files with pagination support.
- `GET /files/{filePath}`: Get a file by its path.
- `POST /files`: Upload a new file.
- `PUT /files/{filePath}`: Upload or overwrite a file.

There are 2 main parts to this assignment:

1. implement the endpoints as shown below by their example requests and responses
2. for each endpoint, implement the full checklist laid out in [`./api-checklist.md`](./api-checklist.md)

Subsequent assignments will build on this one, adding more polish in their own checklist items.

**Note:** the primary goal of this exercise is for learning, so if you get stuck, do not hesitate to
refer to the answer key.

## Endpoints and Schemas Summary

### 1. List Files
- **Endpoint**: `GET /files`
- **Query Parameters**:
  - `pageSize` (optional, integer, default: 10)
  - `directory` (optional, string, default: "")
  - `pageToken` (optional, string)
- **Response**: JSON with a list of files and pagination tokens.

#### Example Request:
```
GET /files?pageSize=5&directory=myfolder&pageToken=abc123 HTTP/1.1
Host: api.example.com
```

#### Example Response:
```json
{
  "files": [
    {
      "key": "myfolder/file1.txt",
      "lastModified": "2023-01-01T00:00:00Z",
      "sizeBytes": 12345
    },
    {
      "key": "myfolder/file2.txt",
      "lastModified": "2023-01-02T00:00:00Z",
      "sizeBytes": 67890
    }
  ],
  "nextPageToken": "next_page_token_value",
  "remainingPages": 2
}
```

### 2. Get File
- **Endpoint**: `GET /files/{filePath}`
- **Path Parameters**:
  - `filePath` (required, string)
- **Response**: Returns the file content or a 404 error if not found.

#### Example Request:
```
GET /files/myfolder/file1.txt HTTP/1.1
Host: api.example.com
```

#### Example Response:
```json
{
  "key": "myfolder/file1.txt",
  "lastModified": "2023-01-01T00:00:00Z",
  "sizeBytes": 12345,
  "content": "base64_encoded_content_here"
}
```

#### Example Error Response:
```json
{
  "detail": "File not found: myfolder/file1.txt"
}
```

### 3. Upload File
- **Endpoint**: `POST /files`
- **Request Body**: Accept a file in the request body as binary data.
- **Response**: Return a 201 status code on success.

#### Example Request:

NOTE: this is a `multipart/form-data` request.

```
POST /files HTTP/1.1
Host: api.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="file1.txt"
Content-Type: text/plain

(file content here)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### Example Response:
```json
{
  "message": "File uploaded: path/to/file"
}
```

### 4. Upload or Overwrite File
- **Endpoint**: `PUT /files/{filePath}`
- **Path Parameters**:
  - `filePath` (required, string)
- **Request Body**: Accept a file in the request body as binary data.
- **Response**: Return a 200 status code if the file is overwritten, or a 201 status code if the file is newly created.

#### Example Request:
```
PUT /files/myfolder/file1.txt HTTP/1.1
Host: api.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="file1.txt"
Content-Type: text/plain

(file content here)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### Example Response for Overwrite:
```json
{
  "message": "File overwritten: myfolder/file1.txt"
}
```

#### Example Response for New File:
```json
{
  "message": "File uploaded: myfolder/file1.txt"
}
```

### 5. Delete File
- **Endpoint**: `DELETE /files/{filePath}`
- **Path Parameters**:
  - `filePath` (required, string)
- **Response**: Return a 200 status code on successful deletion, or a 404 status code if the file is not found.

#### Example Request:
```
DELETE /files/myfolder/file1.txt HTTP/1.1
Host: api.example.com
```

#### Example Response:
```json
{
  "message": "File deleted successfully"
}
```

#### Example Error Response:
```json
{
  "detail": "File not found: myfolder/file1.txt"
}
```
