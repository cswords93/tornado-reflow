from os import path, listdir, rename
import json
		
def profile_to_json(name, times, temperatures, preheat):
	profile = {"name" : name, "preheat": int(preheat), "data": []}
	profile["data"].append([0,25])
	
	for i in range(len(times)):
		profile["data"].append([int(times[i]), int(temperatures[i])])
		
	return json.dumps(profile)

def save_profile(name, json_prof):
	proj_dir = path.dirname(path.abspath(__file__))
	profiles_dir = path.join(proj_dir,"savedprofiles")
	profile_file = path.join(profiles_dir, name)

	f = open(profile_file,'w')
	f.write(json_prof)
	f.close()

def read_profile_names():
	proj_dir = path.dirname(path.abspath(__file__))
	profiles_path = path.join(proj_dir,"savedprofiles")
	profiles_dir = listdir(profiles_path)
	return profiles_dir
	
def rename_profile(name):
	proj_dir = path.dirname(path.abspath(__file__))
	profiles_path = path.join(proj_dir,"savedprofiles")
	profile_file = path.join(profiles_dir, name)
	
def read_profile(name):
	proj_dir = path.dirname(path.abspath(__file__))
	profiles_dir = path.join(proj_dir,"savedprofiles")
	profile_file = path.join(profiles_dir, name)

	f = open(profile_file,'r')
	content = f.read()
	f.close()
	return content

