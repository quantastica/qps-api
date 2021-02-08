import os
import configparser
import requests
import time


def _urljoin(*args):
	return "/".join(map(lambda x: str(x).rstrip("/"), args))

class QGENAPI:
	def __init__(self, qps_api):
		self.qps_api = qps_api

		return

	def solve(self, problem, settings = {}, start_job=True):
		if("settings" not in problem):
			problem["settings"] = {}

		for key in settings.keys():
			if(key == "instruction_set"):
				problem["settings"]["allowed_gates"] = ",".join(settings["instruction_set"])
			else:
				problem["settings"][key] = settings[key]

		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		#
		# Create a job
		#
		create_url = _urljoin(self.qps_api.api_url, "generator", "job", "create")

		create_response = requests.post(url = create_url, headers = headers, json = problem)
		
		create_response.raise_for_status()
		create_result = create_response.json()
		
		job_id = create_result["_id"]

		if(start_job == True):
			#
			# Start a job
			#
			self.start_job(job_id)

		return job_id


	def list_jobs(self, status_filter=None):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		list_url = _urljoin(self.qps_api.api_url, "generator", "job", "list")
		list_data = {}
		if(status_filter is not None):
			list_data["status"] = status_filter

		list_response = requests.post(url = list_url, headers = headers, json = list_data)
		
		list_response.raise_for_status()
		list_result = list_response.json()

		return list_result


	def job_status(self, job_id):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		status_url = _urljoin(self.qps_api.api_url, "generator", "job", "status")
		status_data = { "_id": job_id }
		
		status_response = requests.post(url = status_url, headers = headers, json = status_data)

		status_response.raise_for_status()
		status_result = status_response.json()

		return status_result


	def stop_job(self, job_id):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		stop_url = _urljoin(self.qps_api.api_url, "generator", "job", "stop")
		stop_data = { "_id": job_id }
		
		stop_response = requests.post(url = stop_url, headers = headers, json = stop_data)

		stop_response.raise_for_status()
		stop_result = stop_response.json()

		return stop_result


	def stop_all_jobs(self, status_filter=None):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		stop_url = _urljoin(self.qps_api.api_url, "generator", "job", "stop_all")
		stop_data = {}
		if(status_filter is not None):
			stop_data["status"] = status_filter

		stop_response = requests.post(url = stop_url, headers = headers, json = stop_data)
		
		stop_response.raise_for_status()
		stop_result = stop_response.json()

		return stop_result


	def start_job(self, job_id):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		start_url = _urljoin(self.qps_api.api_url, "generator", "job", "start")
		start_data = { "_id": job_id }
		
		start_response = requests.post(url = start_url, headers = headers, json = start_data)

		start_response.raise_for_status()
		start_result = start_response.json()

		return start_result


	def get_job(self, job_id, wait=True):
		#
		# HTTP headers
		#
		headers = {"Authorization": "Bearer " + self.qps_api.api_token }

		if(wait == True):
			#
			# Wait for status change
			#
			status_url = _urljoin(self.qps_api.api_url, "generator", "job", "status")
			status_data = { "_id": job_id }
			
			while True:
				status_response = requests.post(url = status_url, headers = headers, json = status_data)

				status_response.raise_for_status()

				status_result = status_response.json()
				if(status_result["status"] == "done"):
					break
				if(status_result["status"] == "draft"):
					break
				if(status_result["status"] == "error"):
					message = status_result["message"]
					if(message is None or message == ""):
						message = "Unknown error"
					break
					
				time.sleep(1)

		#
		# Get output
		#
		get_job_url = _urljoin(self.qps_api.api_url, "generator", "job", "get")
		get_job_data = { "_id": job_id }
		get_job_response = requests.post(url = get_job_url, headers = headers, json = get_job_data)

		get_job_response.raise_for_status()

		get_job_result = get_job_response.json()

		if("output" not in get_job_result):
			get_job_result["output"] = {}

		if("circuits" not in get_job_result["output"]):
			get_job_result["output"]["circuits"] = []

		return get_job_result


	def transpile(self, input_qasm, job_name=None, settings = {}, start_job=True):
		problem = {
			"type": "circuit",
			"source": {
				"circuit": {
					"qasm": input_qasm,
					"method": "replace_blocks",
					"two_pass": True
				}
			},
			"settings": {
				"allowed_gates": "u3,cx",
				"max_diff": 1e-3,
				"diff_method": "distance",
				"single_solution": True,
				"pre_processing": "experimental1"
			}
		}

		if(job_name is not None):
			problem["name"] = job_name
		
		return self.solve(problem, settings, start_job)


	def circuit_from_vectors(self, vector_pairs, endianness = "little", job_name=None, settings = {}, start_job=True):
		text1 = ""
		text2 = ""
		for vector_pair in vector_pairs:
			if(len(text1) > 0):
				text1 += "\n"
			if(len(text2) > 0):
				text2 += "\n"
			text1 += str(vector_pair[0])
			text2 += str(vector_pair[1])

		problem = {
			"type": "vectors",
			"source": {
				"vectors": {
					"text1": text1,
					"text2": text2,
					"endianness1": endianness,
					"endianness2": endianness
				}
			},
			"settings": {
				"allowed_gates": "u3,cx",
				"max_diff": 1e-3,
				"diff_method": "distance",
				"single_solution": True,
				"pre_processing": ""
			}
		}

		if(job_name is not None):
			problem["name"] = job_name

		return self.solve(problem, settings, start_job)


	def state_preparation(self, final_vector, endianness = "little", job_name=None, settings = {}, start_job=True):
		initial_vector = [0] * len(final_vector)
		initial_vector[0] = 1
		return self.circuit_from_vectors([ [initial_vector, final_vector] ], endianness, job_name, settings, start_job)


	def decompose_unitary(self, unitary, endianness = "big", job_name=None, settings = {}, start_job=True):
		text = str(unitary)

		problem = {
			"type": "unitary",
			"source": {
				"unitary": {
					"text": text,
					"endianness": endianness
				}
			},
			"settings": {
				"allowed_gates": "u3,cx",
				"max_diff": 1e-3,
				"diff_method": "distance",
				"single_solution": True,
				"pre_processing": ""
			}
		}

		if(job_name is not None):
			problem["name"] = job_name

		return self.solve(problem, settings, start_job)


	def circuit_from_truth_table(self, truth_table, column_defs, additional_qubits=1, job_name=None, settings={}, start_job=True):
		# !!! TODO
		return


class QPSAPI:

	def __init__(self):
		self.api_token = ""
		self.api_url = "https://quantum-circuit.com/api"
		self.load_account()

		self.generator = QGENAPI(self)

		return


	def config_path(self):
		config_path = os.path.join(os.path.expanduser("~"), ".quantastica", ".quantasticarc")

		return config_path


	def load_account(self):
		config_path = self.config_path()

		config = configparser.ConfigParser()
		config.read(config_path)

		api_token = config.get("QPSAPI", "api_token", fallback=self.api_token)
		api_url = config.get("QPSAPI", "api_url", fallback=self.api_url)

		self.use_account(api_token, api_url)

		return


	def use_account(self, api_token, api_url=None):
		if(api_url is not None and len(api_url) > 0):
			self.api_url = api_url

		self.api_token = api_token

		return


	def save_account(self, api_token, api_url=None):
		self.use_account(api_token, api_url)

		config_path = self.config_path()
		config = configparser.ConfigParser()

		config["QPSAPI"] = {}
		config.set("QPSAPI", "api_token", self.api_token)
		config.set("QPSAPI", "api_url", self.api_url)

		os.makedirs(os.path.dirname(config_path), exist_ok=True)
		with open(config_path, "w") as configfile:
			config.write(configfile)

		return
