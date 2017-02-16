import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.websocket
import os.path
import storage
import validation
import oven
import json

class MainHandler(tornado.web.RequestHandler):
	
	def get(self):
		profile_names = storage.read_profile_names()
		self.render("tempchart.html", profiles = profile_names)
		
class ProfileReadHandler(tornado.web.RequestHandler):
	
	def get(self):
		profile_name = self.get_query_argument("profile")
		content = storage.read_profile(profile_name)
		self.write(content)
				
class ProfileHandler(tornado.web.RequestHandler):
	
	def get(self):
		self.render("profiles.html")
		
	def post(self):
		form = self._make_form()
		form.validate()
		
		if form.errors:		
			self.render("profiles.html", errors = form.errors)
		
		else:
			name_data = self.get_argument("name")
			time_data = self.get_arguments("time")
			temperature_data = self.get_arguments("temperature")
			preheat_data = self.get_argument("preheat")
			
			json_prof = storage.profile_to_json(name_data, time_data, 
			temperature_data, preheat_data)
			
			storage.save_profile(name_data,json_prof)
			
			self.redirect(r"/")
	
	def _make_form(self):
		name_data = self.get_argument("name")
		time_data = self.get_arguments("time")
		temperature_data = self.get_arguments("temperature")
		
		name_conditions = [validation.data_required,]
		plot_conditions = [validation.data_required, 
		validation.is_integer]
		
		fields = [validation.Field("name", name_data, name_conditions), 
		validation.FieldList("time", time_data, plot_conditions),
		validation.FieldList("temperature", temperature_data, 
		plot_conditions)]
		
		form = validation.Form(fields)
		return form
		

class SocketHandler(tornado.websocket.WebSocketHandler):
	
	def initialize(self):
		self.my_oven = oven.Oven()
		self.my_oven_watcher = oven.OvenWatcher(self.my_oven)
		self.my_oven_watcher.add_socket(self)
		
	def open(self):
		oven.setup_GPIO()
		
	def on_close(self):
		if self.my_oven.state == oven.Oven.RUNNING:
			self.my_oven.state = oven.Oven.COOLING
		else:
			oven.cleanup_GPIO()
		
	def on_message(self, message):
		
		j = json.loads(message) #dict
		if j["CMD"] == "START":
			profile = storage.read_profile(j["PROFILE"])
			self.my_oven.load_profile(profile)
			self.my_oven.start()
			self.my_oven_watcher.start()
			
		elif j["CMD"] == "STOP":
			self.my_oven.state = oven.Oven.COOLING

def make_app():
	application = tornado.web.Application(
		[
			(r"/", MainHandler),
			(r"/profiles", ProfileHandler),
			(r"/socket", SocketHandler,),
			(r"/load_profile", ProfileReadHandler),
		],
		
		template_path = os.path.join(os.path.dirname(__file__),"templates"),
		static_path = os.path.join(os.path.dirname(__file__),"static"),
		autoreload = True
	)
	return application
	
if __name__ == "__main__":
	
	application = make_app()
	application.listen(5000)
	tornado.ioloop.IOLoop.current().start()
	
