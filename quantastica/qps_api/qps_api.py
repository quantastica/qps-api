import os
import configparser
import requests
import time
import csv
import json
from io import StringIO
from copy import deepcopy


def _urljoin(*args):
    return "/".join(map(lambda x: str(x).rstrip("/"), args))

class QGENAPI:
    def __init__(self, qps_api):
        self.qps_api = qps_api

        return


    def solve(self, problem, settings={}, start_job=True):
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

        create_response = self.qps_api.http_post(url = create_url, headers = headers, json = problem)

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
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        list_url = _urljoin(self.qps_api.api_url, "generator", "job", "list")
        list_data = {}
        if(status_filter is not None):
            list_data["status"] = status_filter

        list_response = self.qps_api.http_post(url = list_url, headers = headers, json = list_data)

        list_response.raise_for_status()
        list_result = list_response.json()

        return list_result


    def job_status(self, job_id):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        status_url = _urljoin(self.qps_api.api_url, "generator", "job", "status")
        status_data = { "_id": job_id }

        status_response = self.qps_api.http_post(url = status_url, headers = headers, json = status_data)

        status_response.raise_for_status()
        status_result = status_response.json()

        return status_result


    def stop_job(self, job_id):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        stop_url = _urljoin(self.qps_api.api_url, "generator", "job", "stop")
        stop_data = { "_id": job_id }

        stop_response = self.qps_api.http_post(url = stop_url, headers = headers, json = stop_data)

        stop_response.raise_for_status()
        stop_result = stop_response.json()

        return stop_result


    def stop_all_jobs(self, status_filter=None):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        stop_url = _urljoin(self.qps_api.api_url, "generator", "job", "stop_all")
        stop_data = {}
        if(status_filter is not None):
            stop_data["status"] = status_filter

        stop_response = self.qps_api.http_post(url = stop_url, headers = headers, json = stop_data)

        stop_response.raise_for_status()
        stop_result = stop_response.json()

        return stop_result


    def start_job(self, job_id):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        start_url = _urljoin(self.qps_api.api_url, "generator", "job", "start")
        start_data = { "_id": job_id }

        start_response = self.qps_api.http_post(url = start_url, headers = headers, json = start_data)

        start_response.raise_for_status()
        start_result = start_response.json()

        return start_result


    def get_job(self, job_id, wait=True):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        if(wait == True):
            #
            # Wait for status change
            #
            status_url = _urljoin(self.qps_api.api_url, "generator", "job", "status")
            status_data = { "_id": job_id }

            while True:
                status_response = self.qps_api.http_post(url = status_url, headers = headers, json = status_data)

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
        get_job_response = self.qps_api.http_post(url = get_job_url, headers = headers, json = get_job_data)

        get_job_response.raise_for_status()

        get_job_result = get_job_response.json()

        if("output" not in get_job_result):
            get_job_result["output"] = {}

        if("circuits" not in get_job_result["output"]):
            get_job_result["output"]["circuits"] = []

        return get_job_result


    def transpile(self, input_qasm, method="replace_blocks", method_options={}, job_name=None, settings={}, start_job=True):
        problem = {
            "type": "circuit",
            "source": {
                "circuit": {
                    "qasm": input_qasm,
                    "method": method
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

        for key in method_options.keys():
            if(key != "qasm" and key != "method"):
                problem["source"]["circuit"][key] = method_options[key]

        return self.solve(problem, settings, start_job)


    def circuit_from_vectors(self, vector_pairs, endianness="little", job_name=None, settings={}, start_job=True):
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


    def state_preparation(self, final_vector, endianness="little", job_name=None, settings={}, start_job=True):
        initial_vector = [0] * len(final_vector)
        initial_vector[0] = 1
        return self.circuit_from_vectors([ [initial_vector, final_vector] ], endianness, job_name, settings, start_job)


    def decompose_unitary(self, unitary, endianness="big", job_name=None, settings={}, start_job=True):
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


    def circuit_from_truth_table(self, truth_table_csv, column_defs, csv_delimiter=None, additional_qubits=1, job_name=None, settings={}, start_job=True):
        # auto-detect delimiter
        delimiter = csv_delimiter
        if(delimiter is None or delimiter == ""):
            count_commas = truth_table_csv.count(",")
            count_tabs = truth_table_csv.count("\t")
            delimiter = "," if count_commas > count_tabs else "\t"

        # parse CSV string
        f = StringIO(truth_table_csv.lstrip())
        reader = csv.reader(f, delimiter=delimiter)

        # read first line
        first_line = next(reader)

        # check if number of columns match number of column_defs
        if(len(column_defs) != len(first_line)):
            raise Exception("Number of columns (" + str(len(first_line)) + ") doesn't match number of column_defs (" + str(len(column_defs)) + ")")

        # check if first line is title
        first_line_title = False
        for cell in first_line:
            if(not cell.isdigit()):
                first_line_title = True
                break

        # build proper coldefs
        coldefs = []
        col_index = 0
        for column_def in column_defs:
            coldef = {}

            # column type
            if(type(column_def) == str):
                coldef["type"] = column_def
            else:
                coldef = deepcopy(column_def)

            if("type" not in coldef):
                raise Exception("Column " + str(col_index) + " (0-based) definition doesn't contain \"type\"")

            if(type(coldef["type"]) == str):
                if(coldef["type"] == "input"):
                    coldef["type"] = 0
                elif(coldef["type"] == "output"):
                    coldef["type"] = 1
                elif(coldef["type"] == "" or coldef["type"] == "ignore"):
                    coldef["type"] = -1
                else:
                    raise Exception("Unknown column type \"" + coldef["type"] + "\"")

            if(coldef["type"] > 1):
                raise Exception("Unknown column type \"" + str(coldef["type"]) + "\"")

            # column index
            if("index" not in coldef):
                coldef["index"] = col_index

            #
            # title
            #
            if("title" not in coldef):
                if(first_line_title):
                    coldef["title"] = first_line[col_index]
                else:
                    coldef["title"] = "Col" + str(col_index)

            coldefs.append(coldef)
            col_index += 1

        # sort coldefs by index
        coldefs.sort(key=lambda x: x["index"])

        # check if col indexes are unique
        col_indexes = list(o["index"] for o in coldefs)
        if len(col_indexes) > len(set(col_indexes)):
            raise Exception("Column indexes are not unique.")

        # create problem
        problem = {
            "type": "truth",
            "source": {
                "truth": {
                    "text": truth_table_csv,
                    "coldefs": coldefs,
                    "numNonOverlapingQubits": additional_qubits
                }
            },
            "settings": {
                "allowed_gates": "x,cx,ccx,swap",
                "max_diff": 1e-3,
                "diff_method": "distance",
                "single_solution": True,
                "pre_processing": ""
            }
        }

        if(job_name is not None):
            problem["name"] = job_name

        return self.solve(problem, settings, start_job)


class QCONVERTAPI:
    def __init__(self, qps_api):
        self.qps_api = qps_api

        return


    def convert(self, input_data, source_format, dest_format):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        input_string = ""
        if isinstance(input_data, dict):
            input_string = json.dumps(input_data)
        elif isinstance(input_data, str):
            input_string = input_data
        else:
            input_string = str(data)

        convert_url = _urljoin(self.qps_api.api_url, "qconvert")
        convert_data = {}
        convert_data["input"] = input_string
        convert_data["source"] = str(source_format)
        convert_data["dest"] = str(dest_format)

        convert_response = self.qps_api.http_post(url=convert_url, headers=headers, json=convert_data)

        convert_response.raise_for_status()
        convert_result = convert_response.text

        return convert_result


class QUTILSAPI:
    def __init__(self, qps_api):
        self.qps_api = qps_api

        return


    def random_circuit(self, num_qubits=5, output_format="quantum-circuit", options={}):
        headers = {"Authorization": "Bearer " + self.qps_api.api_token }

        random_circuit_url = _urljoin(self.qps_api.api_url, "utils", "random_circuit")

        random_circuit_data = {}

        random_circuit_data["num_qubits"] = num_qubits
        random_circuit_data["format"] = str(output_format)

        if "num_gates" in options:
            random_circuit_data["num_gates"] = options["num_gates"]
        if "instruction_set" in options:
            random_circuit_data["instruction_set"] = options["instruction_set"]
        if "mid_circuit_measurement" in options:
            random_circuit_data["mid_circuit_measurement"] = options["mid_circuit_measurement"]
        if "mid_circuit_reset" in options:
            random_circuit_data["mid_circuit_reset"] = options["mid_circuit_reset"]
        if "classic_control" in options:
            random_circuit_data["classic_control"] = options["classic_control"]


        random_circuit_response = self.qps_api.http_post(url=random_circuit_url, headers=headers, json=random_circuit_data)

        random_circuit_response.raise_for_status()
        random_circuit_result = random_circuit_response.text

        return random_circuit_result



class QPSAPI:

    def __init__(self):
        self.api_token = os.environ.get("QPS_API_KEY", "")
        self.api_url = os.environ.get("QPS_API_URL", "https://quantum-circuit.com/api")

        if(not self.api_token):
            self.load_account()

        self.http_timeout = 3
        self.http_max_retries = 3
        self.retry_delay_seconds = 1

        self.synth = QGENAPI(self)

        # self.generator is deprecated. Still here for backward compatibility. Remove in the future.
        self.generator = self.synth

        self.converter = QCONVERTAPI(self)

        self.utils = QUTILSAPI(self)

        return


    def http_post(self, url, headers, json):
        RETRYABLE_STATUS_CODES = { 500, 502, 503, 504 }

        for retry_count in range(self.http_max_retries):
            try:
                response = requests.post(
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=self.http_timeout
                )

                if response.status_code in RETRYABLE_STATUS_CODES:
                    error_message = f"Server returned {response.status_code}. Retrying..."
                    print(error_message)
                else:
                    response.raise_for_status()
                    return response

            except requests.exceptions.ConnectionError as e:
                error_message = f"Connection error occurred: {e.__class__.__name__}. Retrying..."
                print(error_message)

            except requests.exceptions.Timeout:
                error_message = "Request timed out. Retrying..."
                print(error_message)

            except requests.exceptions.HTTPError as e:
                print(f"Non-retryable HTTP Error: {e.response.status_code}. Giving up.")
                raise

            except requests.exceptions.RequestException as e:
                error_message = f"An unexpected RequestException occurred: {e.__class__.__name__}. Giving up."
                print(error_message)
                raise

            if retry_count == self.http_max_retries - 1:
                print(f"Maximum retries ({self.http_max_retries}) exceeded. Giving up.")
                raise requests.exceptions.RequestException(f"Failed after {self.http_max_retries} retries.")


            print(f"Retrying in {self.retry_delay_seconds} seconds...")
            time.sleep(self.retry_delay_seconds)

        return None


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
        self.api_token = api_token

        if api_url:
            self.api_url = api_url

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
