Running
-
docker-compose could be used to run all together. Environment variables from config.env must be provided for every
service if you want to build them separately. For local build in virtual environment you may need content from ./base
directory as dependencies.

Summary
-

It seems to me I have done it :) 

Things I did like:
* I had some dirty hacks in my pocket like database connector and base test class
* I have spent plenty of time exploring the whole framework - there are nice points for dependency injections, 
which are quite comfortable to use while testing
* Testing framework pytest-sanic is handy, but there are some issues with pytest-asyncio collaborations:)

Things I did not like:
* docker-compose is not working correctly on my pc because of any networking issues OR I have wrong connection way
in services - they cannot connect the database while running in containers:(( But they are working nice while running 
locally
* I do not like sanic-openapi - comparing with FastAPI features it provides not so powerful tool as I wish.
* Serialization models could possibly be used together with Swagger models, but I had no motivation to do that by
my own, so it looks weird))
* Overall, I do not really like sanic - FastAPI provides more useful features just out of the box.

Anyway, it made me more experienced:)  
