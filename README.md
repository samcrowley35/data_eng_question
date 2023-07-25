# Solution to data engineering take home problem

### Decisions made during development
- How will you read messages from the queue?
    - To read the messages from the SQS queue, I used python's request library because it was much more convenient to use compared to the AWS boto3 package.

- What type of data structures should be used?
    - In my solution, I simply used python dictionaries to extract the login information, then used the values within it to make a list to insert into the Postgres table.

- How will you mask the PII data so that duplicate values can be identified?
    - In my solution, I used the Fernet module to mask the data.
    - This encryption scheme only uses one key, so if data analysts had access to said key, they could easily decrypt the encrypted/masked fields as well as see duplicate encrypted values to identify users in the Postgres table.

- What will be your strategy for connecting and writing to Postgres?
    - To do this, I used the psycopg2 module to connect the the Postgres database hosted within the docker container.

- Where and how will your application run?
    - See the section below

### Setup and execution steps
1. Clone the repo to your local machine.

2. Create a python environment to run read_queue.py in. Use the command ```python3 -m venv env``` to create it, then ```source env/bin/activate``` to run it.

3. Install all the necessary modules with the command ```pip install -r requirements.txt```

4. To activate the docker containers that host Localstack and Postgres, run ```docker-compose up -d```
    - To check and see if all is well, run the ```docker ps``` command

5. After Localstack and Postgres are spun up, run the python script with the command ```python3 read_queue.py```. Note: for some machines, you may need to use 'python' rather than 'python3'.
    - This script runs infinitely and reads from the local stack every five seconds so be sure to hit CTRL+C to end it.

6. After ending the script, you can check and see that the data was successfully transferred over to Postgres using the following commands.
    - ```psql -d postgres -U postgres -p 5432 -h localhost -W```
    - Note: ```postgres``` is the password for the database
    - Then ```select * from user_logins;``` in the query console

7. After exiting from Postgres, run the ```docker-compose down``` command to shut down the Localstack and Postgres containers. 

### Questions
- How would you deploy this application in production?
    - Instead of having this program run infinitely, I would use a pub/sub topic that would be triggered whenever a new login occurs so that all logins are transformed and placed into the Postgres table.
    - Additionally, I would use much more extensive error handling to make sure that all stages of this process move along smoothly.

- What other components would you want to add to make this production ready?
    - As I mentioned before, I'd like to use cloud Pub/Sub tools to handle new logins rather than an infinitely running script.

- How can this application scale with a growing dataset?
    - If this app were deployed as a microservice/Cloud Function using a cloud provider such as AWS or GCP, it could easily be a scaled by adjusting certain settings, or it could use a multi-threading approach to do so.

- How can PII be recovered later on?
    - The PII could be recovered using a Google Cloud Secret (not sure what the AWS equivalent of that is) for the encryption key so that data analysts and data scientists alike can access and mask the PII fields.

- What are the assumptions you made?
    - I assumed that the person who will be running this has python, docker, and psql downloaded on their machine. However, the instructions say to "assume the evaluator does not have prior experience executing programs in your chosen language and needs documentation" so I made sure to give specific instructions on how to set up the python environment and run the script. 
