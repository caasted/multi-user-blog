# multi-user-blog

This application has been written for Google App Engine. A working instance can be found at https://multi-user-blog-145122.appspot.com/

To run a local instance of your own, install the Google Cloud SDK and then use a terminal window to navigate into the multi-user-blog directory. Then you will be able to launch a local instance of the application using ```dev_appserver.py app.yaml```

## Files

```app.yaml``` tells the app engine what language is being used, where to locate the handlers, and what libraries are used.
```multi-user-blog.py``` directs page requests to the appropriate handler.
```/handlers``` contains python files for the classes that handle page requests
```/models``` contains python files defining the datastore models used
```/templates``` contains the HTML structures that jinga2 uses to generate the application's webpages.
