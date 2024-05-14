[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Fflask3&demo-title=Flask%203%20%2B%20Vercel&demo-description=Use%20Flask%203%20on%20Vercel%20with%20Serverless%20Functions%20using%20the%20Python%20Runtime.&demo-url=https%3A%2F%2Fflask3-python-template.vercel.app%2F&demo-image=https://assets.vercel.com/image/upload/v1669994156/random/flask.png)

# Flask + Vercel

This example shows how to use Flask 3 on Vercel with Serverless Functions using the [Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python).

## Demo

https://flask-python-template.vercel.app/

## How it Works

This example uses the Web Server Gateway Interface (WSGI) with Flask to enable handling requests on Vercel with Serverless Functions.

## Running Locally

```bash
npm i -g vercel
vercel dev
```

Your Flask application is now available at `http://localhost:3000`.

## One-Click Deploy

Deploy the example using [Vercel](https://vercel.com?utm_source=github&utm_medium=readme&utm_campaign=vercel-examples):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Fflask3&demo-title=Flask%203%20%2B%20Vercel&demo-description=Use%20Flask%203%20on%20Vercel%20with%20Serverless%20Functions%20using%20the%20Python%20Runtime.&demo-url=https%3A%2F%2Fflask3-python-template.vercel.app%2F&demo-image=https://assets.vercel.com/image/upload/v1669994156/random/flask.png)

---


## Authentication

Some routes require authentication. This is done by including a bearer token in the header of the request. The token is obtained from the `/login` endpoint.

## Endpoints

### `/`

- Method: `GET`
- Description: Returns a welcome message.
- Authentication: No

### `/env`

- Method: `GET`
- Description: Returns the value of the environment variable "STRING".
- Authentication: No

### `/about`

- Method: `GET`
- Description: Returns an about message.
- Authentication: No

### `/collections`

- Method: `GET`
- Description: Returns a list of all collections in the database.
- Authentication: No

### `/test_post`

- Method: `POST`
- Description: Inserts the data from the request body into the 'users' collection.
- Authentication: No
- Body: JSON object to be inserted into the 'users' collection.
- Sample: `{"name": "John Doe", "email": "john@example.com"}`

### `/test_get`

- Method: `GET`
- Description: Retrieves data from the 'users' collection.
- Authentication: No

### `/signup`

- Method: `POST`
- Description: Creates a new user.
- Authentication: No
- Body: JSON object containing user details.
- Sample: `{"name": "John Doe", "rollno": "123", "phone": "1234567890", "password": "password", "department": "CSE", "year": "2"}`

### `/login`

- Method: `POST`
- Description: Logs in a user and returns an access token.
- Authentication: No
- Body: JSON object containing user roll number and password.
- Sample: `{"rollno": "123", "password": "password"}`

### `/profile`

- Method: `GET`
- Description: Returns the profile of the currently logged in user.
- Authentication: Yes

### `/posts`

- Method: `GET`
- Description: Returns all posts in a forum.
- Authentication: No
- Query Parameters: `forum_id` - ID of the forum.

### `/posts/create`

- Method: `POST`
- Description: Creates a new post.
- Authentication: Yes
- Body: JSON object containing post content and forum ID.
- Sample: `{"content": "This is a new post", "forum_id": "60d3b41f2047f2b96baf288a"}`

### `/posts/<post_id>`

- Method: `GET`, `PUT`, `DELETE`
- Description: Gets, updates, or deletes a specific post by ID.
- Authentication: Yes for `PUT` and `DELETE`, No for `GET`
- Body for `PUT`: JSON object containing new post content.
- Sample for `PUT`: `{"content": "This is an updated post"}`

### `/replies`

- Method: `GET`
- Description: Returns all replies to a post.
- Authentication: No
- Query Parameters: `post_id` - ID of the post.

### `/replies/create`

- Method: `POST`
- Description: Creates a new reply.
- Authentication: Yes
- Body: JSON object containing reply content and post ID.
- Sample: `{"content": "This is a new reply", "post_id": "60d3b41f2047f2b96baf288a"}`

### `/replies/<reply_id>`

- Method: `DELETE`
- Description: Deletes a specific reply by ID.
- Authentication: Yes

### `/forums`

- Method: `GET`
- Description: Returns all forums.
- Authentication: No

### `/forums/create`

- Method: `POST`
- Description: Creates a new forum.
- Authentication: Yes
- Body: JSON object containing forum title and description.
- Sample: `{"title": "New Forum", "description": "This is a new forum"}`
