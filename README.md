# Docker Workshop - FRI
App for workshop on FRI made in Python

## Prerequirements
* Computer with (preferrably) Linux/macOS or Windows
* Free Heroku account
* (optional) Free New Relic account

## Set-up environment
* You can set it up locally, which works on Linux/macOS, and may also works on Windows 10 with Linux Subsystem installed.

  You will need to have the following installed:
  * Docker
  * `docker-compose` (comes bundled with Docker For Mac / Windows)
  * heroku CLI

* You can use provided Vagrant image with Virtualbox + Vagrant on any OS:
  ```bash
  curl -O http://files.celtra.com/2018-03-29/fri-docker-workshop/Vagrantfile
  vagrant up
  ```

## Tutorial
When using `vagrant`, ssh to the VM with `vagrant ssh` and change directory to `files/` via `cd ~/files`. When running locally, open terminal, and change directory to your workspace.
#### Clone code repository
```bash
git clone https://github.com/celtra/workshop-fri.git
```

#### Bring up containers and whole app
```bash
# bring up containers and whole app
cd workshop-fri
docker-compose build
docker-compose up
```

Open [http://localhost/](http://localhost/) (locally) or [http://192.168.90.90/](http://192.168.90.90/) (when using Vagrant), and you should see application running.

Opening home page works, but if you go to any of the API endpoints (e.g. `/student/`), it will return `500 Server Error`, and you will see a Python error in terminal window, since the database is empty, and doesn't contain any tables.

We prepared a simple Python script to initialize the database schema by running:
```bash
docker-compose exec app python db_init.py
```

At this point you should have a database will all required tables, but fetching API endpoints won't return anything useful, since there is no data in the database. You can import example data by running:
```bash
docker-compose exec -T db pg_restore --verbose --clean --no-acl --no-owner -U postgres -d postgres < fakedata/db.dump
```

Now you can test:
* listing students by fetching `GET /student/`
* adding a new student by sending JSON request to `POST /student/`
* updating a specific student by sending JSON request to `PUT /student/<id>`

For testing API endpoints we recommend you use a client like [Postman](https://app.getpostman.com/).

#### Let's deploy this container to Heroku...
```bash
heroku login
heroku container:login
heroku create my-beautiful-app # This creates project (you can name it however you want)
heroku container:push web -a my-beautiful-app # Pushes docker container to Heroku
```

Your website should now be available at [https://my-beautiful-app.herokuapp.com/](https://my-beautiful-app.herokuapp.com/) (change the subdomain to the name of the app you chose above). However, if everything went as planned, you should get `Application error` page, since our application expect a environment variable, to determine if it's running in development (test) or production mode.

You can check errors from your application via:
```bash
heroku logs
```
which should show something like:
```
2018-05-23T09:07:17.451064+00:00 app[web.1]: [2018-05-23 09:07:17 +0000] [482] [INFO] Booting worker with pid: 482
2018-05-23T09:07:17.678053+00:00 app[web.1]: [2018-05-23 09:07:17 +0000] [482] [INFO] Worker exiting (pid: 482)
2018-05-23T09:07:17.678159+00:00 app[web.1]: Problem getting environment. Please set APP_ENV to "test" or "prod".
2018-05-23T09:07:17.713781+00:00 app[web.1]: [2018-05-23 09:07:17 +0000] [484] [INFO] Booting worker with pid: 484
2018-05-23T09:07:17.934178+00:00 app[web.1]: [2018-05-23 09:07:17 +0000] [484] [INFO] Worker exiting (pid: 484)
2018-05-23T09:07:17.934252+00:00 app[web.1]: Problem getting environment. Please set APP_ENV to "test" or "prod".
2018-05-23T09:07:17.967671+00:00 app[web.1]: [2018-05-23 09:07:17 +0000] [486] [INFO] Booting worker with pid: 486
```

In this case the issue is that we haven't created database yet, and application tries to go in development mode (which doesn't work since we haven't set-up APP_ENV environmet variable).

#### Heroku Database Add-on

You can spawn free Postgres database on Heroku by adding an heroku-postgresql addon:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```
Your application needs to be restarted to know about the database:
```bash
heroku restart -a my-beautiful-app
```

Database schema can be created with the same Python script as in local environment:
```bash
heroku run python db_init.py
```

Visiting your Heroku app again should result in working home page, and `/student/` endpoint should return an empty list.


#### New Relic (optional)

If you want to see how your app is performing, where are the bottlenecks, and such, you can create a test New Relic account, and integrate their library to the application.

##### Create APM Application

Visit New Relic website, log-in, and go to APM tab. Select Python agent, and click on the button to reveal secret license key.

##### Modify Dockerfile
To run your application with APM support, you will need to add the following to the `Dockerfile`:
```bash
ENTRYPOINT ["newrelic-admin", "run-program"]
```

To apply the changes to the `Dockerfile` you need to build the image again by running:
```bash
docker-compose build
```

and push it to Heroku by running (this will not restart your app on Heroku):
```bash
heroku container:push web -a my-beautiful-app
```

##### Update Heroku config
For new relic to work, you will need to set-up some config (environmental) variables, which can be easily achieved via `heroku config:set` command:
```bash
heroku config:set NEW_RELIC_LOG=stderr
heroku config:set NEW_RELIC_LOG_LEVEL=info
heroku config:set NEW_RELIC_ENABLED=true
heroku config:set NEW_RELIC_LICENSE_KEY=<your license key>
heroku config:set NEW_RELIC_APP_NAME=pythonapi
```

Setting or changing any config variable will restart your application. Now you can visit your API, and hit your endpoints a few time. After a few minutes, you should see monitoring data in New Relic dashboard.
