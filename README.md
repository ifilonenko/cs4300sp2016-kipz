#Project Framework Description

This is a website framework which provides a simple UI for your information system. You can simply embed your code and ideas in it, so that they can be visited and used by others from the internet. Let others be proud of yout system just like yourself!

Feel free to do any changes to the framework. You can even totally discard it and establish your own website as long as it will not be a problem for you. After all, it is your own information retrieval system not the website you have to focus on. Hope you guys enjoy it. Have fun!

Below are several useful tools and important components of the framework. 

## Git & Github
Git is a version control system designed to handle everything for your project. GitHub is a web-based Git repository hosting service where you can share your codes and ideas with your teammate and collaborate with each other. If you have never used that before, you can download Git from https://git-scm.com/downloads. 

Then, it’s time to start up! You have to use the terminal or the command line tools for this part.
- Go to the folder you want to put your project. 
```sh
e.g. $ cd ~/Document  
```
- Pull the source code of this framework from github to your computer.
```sh
$ git clone https://github.com/CornellNLP/CS4300.git
$ cd CS4300
```
- Sign in to your own github account and create a new repository for this project. 
- Push the framework to your own github repository.
```sh
$ git remote rename origin upstream
$ git remote add origin URL_TO_GITHUB_REPO
$ git push origin master
```
← you can find this URL on you github page of the new repository
- Now, everything is on your own. You can modify the code and push them to your own remote repository. 

	- Pull the code 
	```sh
	$ git pull
	```
	- Push the code 
	```sh
	($ git add -A) 
	($ git commit -m “<message about your modification>”)
	($ git push)
	```

Learn more: 
https://git-scm.com/doc

## Django
Django is a high-level Python Web framework which allows us to easily use python to develop a web application without caring about the http, TCP/IP or socket things. Our framework is developed with Django since python is the language you guys are familiar with. So, you can still use python to realize almost all the parts of your information system.

Good News! In this project, you do not have to use the database at all, which could directly reduce tons of workloads. Just like the previous assignments, your system will take some files as input and provide some result as output. You may form the input data that you will use in your system into JSON files or whatever format you like and put it anywhere your system can get access to.

You may want to run this website on your own computer everytime you make some progress, before depolying it on the remote server. You still have to use terminals to do this.
- First, you have to install django
	($ pip install django)
- Go to the project folder and start the web server server
	($ cd ~/Documents/CS4300)
	($ python manage.py runserver)
  At this moment, if the server is runing successfully, you should see something in your terminal like this:
(
Performing system checks...

System check identified no issues (0 silenced).
March 13, 2016 - 03:50:58
Django version 1.9.4, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
)
- Open your browser and you can have a look at your website at http://127.0.0.1:8000/pt
- Now, the website is running on your local machine. Everytime you change something, just simply refresh the page to check whether it works or not. Enjoy!

Learn more:
https://docs.djangoproject.com/en/1.9/

## Heroku
Heroku is a platform as a service (PaaS) that enables developers to build and run applications entirely in the cloud. We can easily deploy our python app in minutes on heroku. You still have to use terminals to do this.

- First, install heroku toolbelt from https://toolbelt.heroku.com/
- Create a heroku account.
- Login on your local machine
	($ heroku login)
- Go to the project folder and revise the requirements.txt file if you use any new packages in your python code
- Create an app on heroku.
	($ heroku create <your_website_name>)
- Push the project on heroku.
	($ git push heroku master)
- The application is now deployed. Ensure that at least one instance of the app is running.
	($ heroku ps:scale web=1)
- Now, you can visit your website at <your_website_name>.herokuapp.com/pt/.

Learn more:
https://devcenter.heroku.com/articles/getting-started-with-python#introduction

## About this framework
Have a look at the project_template/test.py file which implement the function that searching for the most similar messages to the query according to their edit difference. You can implement your system accoring to this sample code. Note that you have to make sure you import all the library or modules you need for each python file you create. For the input data, I just simply use the JSON file jsons/kardashian-transcripts.json and I push it together with the whole project to the heroku.

??  About where to put the file 
However, it is not wise to do so when your input data is very large. (Really?) You can put those file on somewhere else (e.g. github) and change the read_file function accordingly. 

Then have a look at the project_template/views.py. You will find out how your code and functions interact with the webpages. When django get a valid query, it will call the find_similar function in project_template/test.py and render another webpage to show the results.
