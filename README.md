# FastAPI-2FA-OTP
The idea behind this simple application is to design and test a [Multi-factor authentication](https://en.wikipedia.org/wiki/Multi-factor_authentication) based on random 
[one time password](https://en.wikipedia.org/wiki/One-time_password)  and implemented through the framework FastAPI.


### QuickStart using Docker
*NB the next steps should not change depending on the SO used. Otherwise, please report any errors/mistakes by emailing me or just creating an new issue. Thank you.*  

Clone the repository and move onto the new folder and be sure you're using the main branch.

Run ```docker compose --env-file apps\users_service\development.env -f apps\users_service\docker-compose.yaml up -d``` 
and wait it to finish. Then, login to the new container with ```docker exec -it fastapi.login2fa.users bash```

Once inside the container, you should be able to run the app instance by running ```. ./stack/development/fastapi/dryRun.sh```

FastAPI is based on OpenAPI which generates an interactive API documentation and exploration web user interfaces (you should find it [here](http://127.0.0.1:8201/docs)).
In addition, into ```docs``` folder you find postman collection and environment with which to test the running app. 


### Environment
The backend service is developed by using the web framework ***[FastAPI](https://fastapi.tiangolo.com/)*** (version 0.89.1), ***[Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/)*** and ***PostgreSQL*** (version 12), all based on ***[Docker](https://www.docker.com/)***. *FastAPI* is a popular 
framework for creating REST services. It is described as being very fast to code and the fastest *Python* web framework available (with performances comparable to *NodeJS* and *Go*). *Tortoise ORM* 
is a very young project, is designed to be functional and familiar to *Django ORM*. In particular, it is thought to support *[asyncio](https://docs.python.org/3/library/asyncio.html)* with a clean API 
*(NB I probably could have chosen a more famous ORM, but I was curious to try and test it)*.

Both application and database are deployed in two different *Docker* containers. *Docker* is an open-source containerization platform used for developing, deploying, and managing applications, and all their dependencies,
in lightweight virtualized environments called containers *(using containers has several advantages including replicability, security and simplicity)*.
 

### 2FA, JWT and OTP
The application security is based on ```JWT```. *JWT* is a standard to codify JSON objects in a long string. It has consists of different features, but mainly 
we can summerize them into two points:
  * it is not encrypted, so it allows to share info;
  * it is signed, so who emits a JWT can also verify it;
  * has an expiration date, which improves app security.

Generally web applications employed two kind of tokens:
* access_token, which are used to allow an application to access an API.
* refresh_token, is a credential artifact that apps can use to get a new access token without user interaction.

This application generates access and refresh token by using the homonymous python library [jwt](https://pyjwt.readthedocs.io/en/latest/). Contextually it assigns 
an expiration time of, respectively, one hour for access token and one month for refresh token.

As per usual practice, in this simple application JWT are generated when user sends her credentials to the appropriate endpoint (```127.0.0.1:8201/api/v1/auth/login```). This endpoint 
works in two different ways based on user's 2FA preference:
* user has disabled 2FA:
  * service returns an access and refresh token.
* user has enable 2FA, then the system:
  * returns a temporary token (which its expiration time is 4 minutes);
  * generates a new OTP by using *[pyotp]()* library;
  * sends it to the user by email (actually emailing is substituted by a .txt file ```apps/users_service/logs/otp-logs.txt```;
  * saves the couple ```(temporary token, generated otp)``` on db, into otps table.

Starting from the generation of temporary token, the user will have four minutes to send the received otp (including into headers the temporary token as Authentication bearer) to the 
appropriate endpoint (```127.0.0.1:8201/api/v1/auth/verify-otp```). After validating temporary token, the application searches, on table otps, a record which described the received pair 
```(temporary token, generated otp)```. Finally, if the db contains an active record with these values, the application generate, and return, to user an access and refresh 
token and, in addition, it invalidates the returned record (so that it cannot be reused). 


### API
***Login2FA*** app consists of two main sub-routes:
* ***<em>/auth</em>***: here we find those endpoints connected with authentication flow:
  * */token* - POST: given a couple of username and password of an active user, it returns two different responses based on user's 2FA preferences: if user does not enable the two factor authentication, it returns access and refresh token, otherwise, a temporary token it would be returned (which the user will use to confirm the otp received by email).
  * */refresh-token* - POST: given a valid refresh token this endpoint returns a new couple of valid access and refresh token (useful in order to avoid unnecessary reauthentication).
  * */verify-token* - POST: it takes in input an access token and checks if it is valid or not.
  * */verify-otp* - POST: when the user enables 2FA, upon next authentication request, the app sends to the user a generated OTP which will be asked to complete the authentication.   
* ***<em>/users</em>***: in this route endpoints concerning user management find their place (useful for testing auth flow):
  * */registration* - POST: through this endpoint user can create her account.
  * */me* - GET: returns authenticated user information (identified by the access token passed in the headers).
  * */change-password* - POST: given a couple of password it updates the password of user who sent the request.
  * */* - GET: it is used by admin users for listing all registered users or retrieve a specific user.
  * */* - PATCH: allows users to update their account info; in addition, it permits user admins to update other users' info (for example add/remove admins, ecc.).
  * */* - DELETE: is the endpoint through which users can remove their account from the app. Similarly to previous endpoint, admins can use this endpoint in order to remove other users.


### TEST
Tests are based on *[pytest](https://docs.pytest.org/en/7.2.x/)* and are located in ```app/tests``` folder. They consist of two separated files: one where auth endpoints will be tested, 
the another concerning user endpoints.

***How do I launch tests?***<br>
****Short answer****
From ```fastapi.login2fa.users``` container run ```pytest ./app/tests/*```.<br>
****Long answer****
Unfortunately, during tests implementation, I had faced some (unresolved) problems between Tortoise ORM and Pytest. To overcome this problem, tests send requests to app through *[requests]()* library. 
The consequence of this decision is that tests must be runned from another instance of the container where backend service is located.<br>
*In other words open a new shell window, login to ```fastapi.login2fa.users``` container with ```docker exec -it fastapi.login2fa.users bash```, then run ```pytest ./app/tests/*```*  
