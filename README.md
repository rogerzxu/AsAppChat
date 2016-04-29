# AsAppChat

Take home exercise for ASAPP interview process. Write a chat service that supports the following operations:
* Connect with web-sockets
* Authenticate by username
* Send message which is to be persisted in a database
* Receive messages in real-time
* Fetch chat history

## Tech Stack

AsAppChat uses the following packages/libraries to achieve these goals:
* Python 2.7
* Flask 0.10.1
* Flask-Login 0.3.2
* Flask-SocketIO 2.2
* eventlet 0.18.4
* Jinja2 2.8
* Sqlite (Xerial)
* JQuery 1.11.1
* Bootstrap 3.3.6

## Usage
Assuming you have all dependencies have been installed, simply

```
$ python AsAppChat.py
  (18404) wsgi starting up on http://127.0.0.1:5000
```

## Follow-up questions
1. How will you implement picture messages? Where is image data stored? How/when are thumbs generated? How are URLs decided on?

  I would probably cap the maximum image size to reduce bandwith. Full-size images would be stored in an S3 bucket, or some similar storage utility. Thumbnails are generated on the point of upload, and only thumbnails would be sent to the receiving users, unless they choose to download the full-size image. Thumbnails can also be stored in a separate bucket. URL's for thumbnails and pictures should either be obfuscated so they are for temporary use, or they could be public but with an auth system in place to decide who is able to see specific images.
  
2. How will you support a typical "home" screen which lists all conversations along with their most recent message? Some things to consider:
  * All conversations need to be up to date at all times.
  * What if a device is offline for a day and comes back online?
  * What if a user has multiple devices?
  * What if a user has a total of ~1000 conversations and goes online/offline frequently?
  
  The home screen currently has a list of users (no friend system in place yet). Chat histories are not automatically fetched on the home screen, but rather they are fetched when you click on a username via an AJAX call. This helps to keep bandwith low. The biggest weakness currently is that once you log in, there is no indicator as to which messages are new since your last log-in. At some point though, given enough conversations and messages, it would be ideal to split the database into a read_messages and unread_messages table, which could easily be sync'd across devices. Then, even if you have thousands of conversations, you would know which conversations have been updated recently.
  
3. How will you deploy new versions of your code without any downtime? How does the client handle losing its websocket connection? What happens if a deploy fails or there's a regression?

  Currently, socket state is mostly held in memory, which means there will be some downtime during a deployment (even with a load-balancer). Steps must be made to move the state to an external source (like redis), that way even if the sockets have to reconnect, state information would be preserved. If a deployment fails... that's what backups are for. Ideally only the web servers need to be rolled back and not the databases.
  
4. How will you scale your server beyond a single machine? Keep in mind that all messages need to be delivered in realtime, and that communicating users may be connected to different machines. Also consider that a user may have multiple devices that could be connected to different machines.

  If the state is stored externally from the server, then multiple instances of the server should be fine. It would get tricky once the databases reach capacity because then you might have to do some sharding. This version supports multiple device connection okay in my opinion (at least when I tried from two different browsers concurrently). Right now, clients are kept track of on the server by their username, and when a user receives or sends a message, all of the clients with that username logged in get the same updates.
  
5. Imagine that Comcast will start directing their customer support traffic at your system a month from now. They see roughly 1M conversations per day. How do you prepare?

  There are some changes that can be immediately that wouldn't require too much code change. First of all, ditch Sqlite for something heavier. Secondly, make sure that your web application server and hardware is as good possible for the moment. Third, export socket states to redis and use multiple instances with a load balancer. After that is done, I would move towards making the application multi-threaded.
