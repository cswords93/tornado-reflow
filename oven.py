import MAX31855 as MAX31855
from RPi import GPIO
from time import sleep, time
from threading import Thread
from datetime import datetime
import config

def setup_GPIO():
	print("Setting up GPIO")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(config.LAMPS,GPIO.OUT)
	GPIO.setup(config.FANS,GPIO.OUT)
	
def cleanup_GPIO():
	print("Cleaning up GPIO")
	GPIO.output(config.LAMPS, False)
	GPIO.output(config.FANS, False)
	GPIO.cleanup()

class TempSensor(Thread):
	
	def __init__(self, time_step = 0.5):
		super().__init__()
		self.thermocouple = MAX31855.MAX31855(config.CLK,config.CS,
		config.DO)
		self.temperature = 0
		self.time_step = time_step
		self.running = False
		
	def read_temperature(self):
		self.temperature = self.thermocouple.readTempC()
		return self.temperature	
	
	def run(self):
		self.running = True
		
		while self.running:
			self.read_temperature()
			sleep(self.time_step)
		
		print("stopping sensor")

class Oven(Thread):
	IDLE = "IDLE"
	PREHEATING = "PREHEATING"
	RUNNING = "RUNNING"
	COOLING = "COOLING"
	STOPPED = "STOPPED"
	
	def __init__(self, time_step = 0.5):
		super().__init__()
		self.daemon = True
		self.time_step = time_step
		self.pid = PIDController()
		self.sensor = TempSensor(time_step)
		self.profile = None
		self.state = Oven.IDLE
		self.run_time = 0
		self.end_time = 0
		self.target_temp = 0
		
	def load_profile(self, js):
		self.profile = Profile(js)
		self.end_time = self.profile.get_duration()
		
	def preheat_oven(self):
		if self.profile.preheat > 0:
			self.state = Oven.PREHEATING
			self.set_lamps(True)
			preheating = True
			print("preheating")
			
			while preheating:
				if self.sensor.read_temperature() >= self.profile.preheat:
					preheating = False
				sleep(self.time_step)
			
	def cooldown_oven(self):
		self.set_lamps(False)
		self.set_fans(True)
		
		while self.sensor.read_temperature() > 30:
			sleep(self.time_step)
			
		
	def stop_oven(self):
		self.state = Oven.STOPPED		
		self.sensor.running = False	
		self.set_lamps(False) 
		self.set_fans(False)
		GPIO.cleanup()
		print("oven stopped")
	
		
	def run(self):
		
		self.sensor.start()
		self.preheat_oven()
		self.state = Oven.RUNNING
		
		start_time = time()
		
		while self.state == Oven.RUNNING:
			self.run_time = time() - start_time
			current_temp = self.sensor.read_temperature()
			
			if self.run_time >= self.end_time:
				self.state = Oven.COOLING
				break
			
			print("The temperature is: {0:0.3F}\u2103".format(current_temp))
			
			self.target_temp = self.profile.get_target(self.run_time)
			
			p = self.pid.compute(self.target_temp, current_temp)
			print("The PID output: {}".format(p))
			value = p > 0

			self.set_lamps(value)
			self.set_fans(not value)
				
			sleep(self.time_step)
		
		#Cool down until 30 degrees c
		self.cooldown_oven()
		self.stop_oven()

			
	def set_lamps(self,value):
		GPIO.output(config.LAMPS, value)
	
	def set_fans(self,value):
		GPIO.output(config.FANS, value)
	
	def get_state(self):
		oven_state = {
			"run_time": self.run_time,
			"temperature": self.sensor.read_temperature(),
			"target_temperature": self.target_temp,
			"oven_state": self.state}
			
		return oven_state

class OvenWatcher(Thread):
	
	def __init__(self, my_oven, time_step = 5):
		super().__init__()
		self.my_oven = my_oven
		self.time_step = time_step
		self.sockets = []
		
	def add_socket(self, socket):
		self.sockets.append(socket)
		
	def send_message(self, message):
		for socket in self.sockets:
			socket.write_message(message)
			
	def run(self):
		
		while self.my_oven.state == Oven.RUNNING:
			message = self.my_oven.get_state()
			self.send_message(message)
			sleep(self.time_step)
		


class Profile(object):
	
	def __init__(self,profile_json):
		import json
		profile_data = json.loads(profile_json)
		self.name = profile_data["name"]
		self.data = profile_data["data"]
		self.preheat = profile_data["preheat"]
		
	def is_rising(self,current_time):
		(prev_point, next_point) = self.get_neighbor_points(current_time)
		return next_point > prev_point
		
	def get_target(self,current_time):
		(prev_point,next_point) = self.get_neighbor_points(current_time)
		print( prev_point, next_point)
		m = (next_point[1] - prev_point[1]) / (next_point[0] - prev_point[0])
		
		y = m * (current_time - prev_point[0])
		y = y + prev_point[1]
		return y
		
	def get_neighbor_points(self,current_time):
			
		prev_point = None
		next_point = None
		
		for i in range(len(self.data)):
			if current_time < self.data[i][0]:
				prev_point = self.data[i-1]
				next_point = self.data[i]
				break
				
		return (prev_point,next_point)
			
	def get_duration(self):
		return max(t[0] for t in self.data)
		
class PIDController(object):
	
	def __init__(self,kp = 0.5, ki = 0.5, kd = 0.5):
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self.accumulation_of_error = 0
		self.lastError = 0
		self.lastTemp = 0
		self.lastNow = datetime.now()
		
	def compute(self,setpoint, current_point):
		now = datetime.now()
		delta = (now - self.lastNow).total_seconds()
		error = float(setpoint - current_point)
		
		self.accumulation_of_error += error * delta
		self.accumulation_of_error = sorted([-1, self.accumulation_of_error, 1])[1]
		
		derivative_of_error = 0
		if delta > 0.5:
			derivative_of_error = (error - self.lastError) / delta
		
		output = (error * self.kp) + (self.accumulation_of_error * 
		self.ki) + (derivative_of_error * self.kd)
		
		self.lastTemp = current_point
		self.lastError = error
		return output
