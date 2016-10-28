# multi-user-blog

This application has been developed as part of Udacity's Full Stack Web Developer Nanodegree. It uses Google App Engine to serve a web application that allows multiple users to make, edit, and delete blog entries as well as add, edit, and delete comments on the blog entries. A working instance can be found at https://multi-user-blog-145122.appspot.com/

## Quickstart

To run a local instance of your own, install the [Google Cloud SDK](https://cloud.google.com/appengine/docs/python/download), clone the repository to your local machine, and then use a terminal window to navigate into the multi-user-blog directory. Then you will be able to launch a local instance of the application using `dev_appserver.py app.yaml`

## Files

`app.yaml` tells the app engine what language is being used, where to locate the handlers, and what libraries are used.

`multi-user-blog.py` directs page requests to the appropriate handler.

`/handlers` contains python files for the classes that handle page requests

`/models` contains python files defining the datastore models used

`/templates` contains the HTML structures that jinga2 uses to generate the application's webpages.

`/css` contains the stylesheet used for the site

## License

**multi-user-blog** is free software, and may be redistributed under the terms specified in the [LICENSE](https://github.com/caasted/multi-user-blog/blob/master/LICENSE) file.
