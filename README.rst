----------
Muskel API
----------

Muskel is an REST API for managing your workouts.

.........
Resources
.........

- **Templates** *(Templates for new workouts)*
    - **Exercises** *(Exercises that can be tracked)*
- **Workouts** *(Workout is created from a template)*
    - **Moves** *(Moves are exercises with their performance info)*

****
Todo
****
- API documentation (OAS?)
- User registration
- External configuration setup
- Development guide 
- Deployment guide
- Extensive error handling


************
Instructions
************

+++++++
MongoDB
+++++++
- Install mongo on docker: ``docker pull mongo``
- Make local folder for data on host system: ``mkdir mongodata``
- Run container: ``docker run -it -v /home/oze/stuff/mongodata:/data/db -p 27017:27017 --name mongodb -d mongo``
- Attach to container: ``sudo docker exec -it mongodb bash``
- More info on https://phoenixnap.com/kb/docker-mongodb


++++++++++++++++
Running the app
++++++++++++++++

- Have .env file in the home folder with SECRET, ADMIN_USERNAME and ADMIN_PASSWORD keys
- Run muskel.py to create admin user
- Run with: ``gunicorn --reload muskel``

