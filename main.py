from aiohttp import web
import motor.motor_asyncio
import os
import random
import string

async def index_page(request):
    return web.Response(text="""
    <html>
        <head>
            <title>Redirecter</title>
            </head>
            <body>
                <h1>Redirecter</h1>
                <p>Redirects to a long URL based on a short URL.</p>
                <form action="/" method="post" >
                <input type="text" name="long_url" id="long_url" required>
                <input type="submit" valur="Subscribe!">
                </form>              
            </body>
    </html>
    """,
            content_type="text/html")

async def recieve_url(request):
    data = await request.post()
    long_url = data['long_url']
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://root:example@{os.environ.get("DB_HOST", "localhost")}:27017')
    db = client['redirecter']
    collection = db['redirects']
    generated_resource_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    document = await collection.insert_one({'long_url': long_url, 'resource_id': generated_resource_id})
    return web.Response(text=generated_resource_id, content_type='text/plain')

async def redirecter(request):
    resource_id = request.match_info['resource_id']
    client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:example@{os.environ.get("DB_HOST", "localhost")}:27017')
    db = client['redirecter']
    collection = db['redirects']
    document = await collection.find_one({'resource_id': resource_id})
    if document is None:
        return web.Response(text='Not Found', status=404)
    long_url = document['long_url']
    return web.HTTPFound(long_url)


app = web.Application()
app.add_routes([web.get('/', index_page)])
app.add_routes([web.post('/', recieve_url)])
app.add_routes([web.get('/{resource_id}', redirecter)])
web.run_app(app)