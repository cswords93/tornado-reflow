
class Form(object):
	
	def __init__(self, fields):
		self.fields = fields
		self.errors = {}

	def validate(self):
		self.errors = {}
		success = True
			
		for field in self.fields:
			field.validate()
			if field.errors:
				self.errors[field.name] = field.errors
				success = False
				
		return success
		
class Field(object):
	
	def __init__(self, name, data, conditions):
		self.name = name
		self.data = data
		self.conditions = conditions
		self.errors = []
		
	def validate(self):
		for condition in self.conditions:
			try:
				condition(self.data)
			except ValidationException as inst:
				error_msg = inst.message
				self.errors.append(error_msg)


class FieldList(Field):
	
	def __init__(self, name, data, conditions):
		super().__init__(name, data, conditions)
	
	def validate(self):
		for d in self.data:
			
			for condition in self.conditions:
					
				try:
					condition(d)
					
				except ValidationException as inst:
					error_msg = inst.message
					
					if error_msg not in self.errors:
						self.errors.append(error_msg)
					#self.conditions.remove(condition)
					#remove condition because already found atleast one
					#error - don't need to check anymore
					

					

	
def data_required(data):
	if data == None or data == "":
		raise ValidationException("Data required")

def is_integer(data):
	try:
		int(data)
	except ValueError:
		raise ValidationException("Not an integer")
		
			
class ValidationException(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)
		self.message = message
		
		
if __name__ == "__main__":
	conditions = [data_required,]
	fields = (Field("First Name", "bob", conditions), FieldList("Middle Name", ["",""],conditions))
	
	form = Form(fields)
	form.validate()
	print(form.errors)
