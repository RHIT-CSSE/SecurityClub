# Author: Ishank Tandon
# Date: January 29, 2017

import tornado.ioloop
import tornado.web
import tornado.httpserver
import hashlib
import base64
import json
import mysql.connector as sql

dbuser = 'csse'

# Register a new user
class UserHandler(tornado.web.RequestHandler):
  def set_default_headers(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    self.set_header('Access-Control-Allow-Methods', 'POST, GET')
    self.set_header('Cache-Control', 'max-age=0,must-revalidate')

  def post(self, username, password, person_name):
    db = sql.connect(user=dbuser, database='wireshark', host='127.0.0.1')

    cursor = db.cursor(buffered=True)

    checkquery = "SELECT * FROM userinfo  WHERE username = '" + username + "'"
    insertquery = "INSERT INTO userinfo(username, password, person_name) VALUES('" + username + "', '" + password + "', '" + person_name + "')"
    selectquery = "SELECT id FROM userinfo  WHERE username = '" + username + "'"

    try:
      # import pdb; pdb.set_trace()
      cursor.execute(checkquery)
      res = cursor.fetchone()
      if res is None:
        cursor.execute(insertquery)
        db.commit()
        cursor.execute(selectquery)
        idd = cursor.fetchone()[0]
        print(idd)
        resobj = {'id': idd}
        db.commit()
        self.write({ 'result': True, 'messsage': 'Successfully created user', 'data' : resobj})
      else:
        db.commit()
        resobj = {'id': -1 }
        self.write({ 'result': False, 'messsage': 'User already exists', 'data' : resobj})
        
    except sql.Error as err:
      db.rollback()
      self.write({'result': False, 'message': 'Some weird error occured' })

    db.close()


  def get(self, username, password):
    db = sql.connect(user=dbuser, database='wireshark', host='127.0.0.1')

    cursor = db.cursor(buffered=True)

    query = "SELECT * FROM userinfo WHERE username='" + username + "' " + "AND password='" + password + "'"
    print(query)

    try:
      cursor.execute(query)
      res = cursor.fetchone()
      db.commit()
      if res != None:
        resobj = {'id': res[3]}
        self.write({ 'result': True, 'message': 'Successfully logged in', 'data': resobj })
      else:
        resobj = {'id': -1 }
        self.write({ 'result': False, 'message': 'Couldnt logged in. error.', 'data': resobj })
    except sql.Error as err:
      db.rollback()
      self.write({'result': False, 'message': 'Some weird error occured' })

    db.close()



# Post a new message
class MessageHandler(tornado.web.RequestHandler):
  def set_default_headers(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    self.set_header('Access-Control-Allow-Methods', 'POST, GET') 
    self.set_header('Cache-Control', 'max-age=0,must-revalidate')

  def post(self, uid, message):
    db = sql.connect(user=dbuser, database='wireshark', host='127.0.0.1')

    cursor = db.cursor(buffered=True)
    selectquery = "SELECT username, password, person_name FROM userinfo  WHERE id = '" + uid + "'"

    print(selectquery)

    try:
      cursor.execute(selectquery)
      name = cursor.fetchone()
      print(name)

      if name is not None:
        insertquery = "INSERT INTO posts(person_name, id, message) VALUES('" + name[2] + "', '" + uid + "', '" + message + "')"
        cursor.execute(insertquery)
        db.commit()
        resobj = { 'username': name[0], 'password': name[1] }
        self.write({ 'result': True, 'messsage': 'Successfully created post', 'data': resobj })
      else:
        db.commit()
        self.write({ 'result': False, 'messsage': 'wrong id breh!!' })

    except sql.Error as err:
      db.rollback()
      self.write({'result': False, 'message': 'Some weird error occured'  })

    db.close()


  def get(self):
    # print(username)
    # print(uid)
    db = sql.connect(user=dbuser, database='wireshark', host='127.0.0.1')

    cursor = db.cursor(buffered=True)

    query = "SELECT * FROM posts LIMIT 20"
    print(query)

    try:
      cursor.execute(query)
      res = cursor.fetchall()
      
      retobj = []
      for item in res:
        data = { 'person_name': item[0], 'post': item[2] }
        retobj.append(data)

      # resobj = {'username': res[0], 'id': res[3]}
      db.commit()
      if res != None:
        self.write({ 'result': True, 'message': 'Got these posts.', 'data': retobj })
      else:
        self.write({ 'result': False, 'message': 'Couldnt logged in. error.' })
    except sql.Error as err:
      db.rollback()
      self.write({'result': False, 'message': 'Some weird error occured' })

    db.close()


class ProxyMainHandler(tornado.web.RequestHandler):
  def set_default_headers(self):
    self.set_header("Access-Control-Allow-Origin", "*")
    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    self.set_header('Access-Control-Allow-Methods', 'POST, GET')

  def get(self, numb):
    print('input was: ' + numb)
    num = int(numb)
    if num == 47:
            decodedmsg = 'It is a period of civil war. Rebel spaceships, striking from a hidden base, have won their first victory against the evil Galactic Empire.\nDuring the battle, Rebel spies managed to steal secret plans to the Empire\'s ultimate weapon, the DEATH STAR, an armored space station with enough power to destroy an entire planet.\nPursued by the Empire\'s sinister agents, Princess Leia races home aboard her starship, custodian of the stolen plans that can save her people and restore freedom to the galaxy....'
            msg = base64.b64encode(decodedmsg)
            self.write({ "result": True, "key": msg })
    else:
            msg = base64.b64encode('Not the secret buddy! Haha try again!')
            self.write({ "result": False, "key": msg })


class SharkHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('sharkclient.html')

class ProxyHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('client.html')

class ClubHandler(tornado.web.RequestHandler):
  def get(self):
    self.add_header('CSSE290_CLASS', 'Nu! Lbh znqr vg guvf sne. Jryy, gurerf abguvat zber. Gur frperg vf: v nz njrfbzr.')
    self.render('webactivity.html')

def make_app():
  return tornado.web.Application([
      (r"/shark", SharkHandler),
      (r"/shark/signup/username/([^/]*)/password/([^/]*)/person_name/([^/]*)", UserHandler),
      (r"/shark/login/username/([^/]*)/password/([^/]*)", UserHandler),
      (r"/shark/message/id/([^/]*)/message/([^/]*)", MessageHandler),
      (r"/shark/message/get20", MessageHandler),

      (r"/proxy", ProxyHandler),
      (r"/webactivity", ClubHandler),
      (r"/proxy/([^/]*)", ProxyMainHandler),
  ])

if __name__ == "__main__":
  app = tornado.httpserver.HTTPServer(make_app())
  app.listen(8888)
  tornado.ioloop.IOLoop.current().start()

