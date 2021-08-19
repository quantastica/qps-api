# Quantum Programming Studio API

Python wrapper for [Quantum Programming Studio](https://quantum-circuit.com/) HTTP API.


# Quick start

**1. Install QPS API package:**

```bash
pip install quantastica-qps-api
```

**2. Find your QPS API token:**

[Login](https://quantum-circuit.com/login) to Quantum Programming Studio, go to [Profile -> API Access](https://quantum-circuit.com/user_settings/api) and copy your API token.

**3. Configure QPS API package with your API token:**

```python

from quantastica.qps_api import QPS

QPS.save_account("YOUR_API_TOKEN")

```

That will create a local configuration file where your API token will be stored for future use.

**Now you are ready to use QPS API.**

**Quick start example:** find circuit from initial/final vector pairs using Quantum Algorithm Generator

```python

from quantastica.qps_api import QPS

vector_pairs = [
[ [1, 0, 0, 0], [ 0.5+0j,  0.5+0j,  0.5+0j,  0.5+0j ] ],
[ [0, 1, 0, 0], [ 0.5+0j,  0+0.5j, -0.5+0j,  0-0.5j ] ],
[ [0, 0, 1, 0], [ 0.5+0j, -0.5+0j,  0.5+0j, -0.5+0j ] ],
[ [0, 0, 0, 1], [ 0.5+0j,  0-0.5j, -0.5+0j,  0+0.5j ] ]
]

job_id = QPS.generator.circuit_from_vectors(vector_pairs, settings = { "instruction_set": ["h", "cu1", "swap"] })

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```


# Account management

### QPS.save_account(api_token, api_url=None)

**Run this once** to setup your QPS REST API account. Method will create configuration file and your api token will be stored there for future use.

If needed, you can clear your token by running `QPS.save_account("")` (or by deleting a configuration file).

If `api_url` is not provided then `https://quantum-circuit.com/api/` will be set as default.


### QPS.config_path()

You can get config file path by running `QPS.config_path()`.

Default configuration file path:

- On Unix, directory is obtained from environment variable HOME if it is set; otherwise the current user’s home directory is looked up in the password directory through the built-in module pwd.

- On Windows, USERPROFILE will be used if set, otherwise a combination of HOMEPATH and HOMEDRIVE will be used.


# Quantum Algorithm Generator API

[Quantum Algorithm Generator](https://quantastica.com/#generator) is a tool based on machine learning which reverse engineers quantum circuits from state vectors (wave functions). Additionally, it can be used to find quantum algorithm for boolean function from truth table, to transpile circuits and to decompose unitary matrices.


## Generator job management

Problem sent to generator is called a "job". Each job has unique ID. As generator is resource intensive tool, it is configured to execute only one job at a time. While generator is solving a job, other jobs are queued. When generator finishes executing a job, it takes the next one from the queue.

API provides functions for job manipulation: you can list all jobs (filtered by status), stop running job, cancel queued jobs, stop/cancel all jobs, start previously canceled (draft) job, etc.

### QPS.generator.list_jobs(status_filter=None)

List all jobs, optionally filtered by status.

- `status_filter` String, optional. Can be: `draft`, `queued`, `running`, `error`, `done`.


**Example 1** - list all (unfiltered) generator jobs:

```python

from quantastica.qps_api import QPS

jobs = QPS.generator.list_jobs()

print(jobs)

```

Example output:

```
{
	"list": [
		{ "_id": "r9LskFoLPQW5w7HTp", "name": "Bell state", "type": "vectors", "status": "done" },
		{ "_id": "R8tJH7XoZ233oTREy", "name": "4Q Gauss", "type": "vectors", "status": "queued" },
		{ "_id": "h7fzYbFz8MJvkNhiX", "name": "Challenge", "type": "unitary", "status": "draft" },
		{ "_id": "PC5PNXiGqhh2HmkX8", "name": "Experiment", "type": "vectors", "status": "error"},
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary", "status": "running" }
	]
}
```

**Example 2** - list `running` jobs:

```python

from quantastica.qps_api import QPS

jobs = QPS.generator.list_jobs(status_filter="running")

print(jobs)

```

Example output:

```
{
	"list": [
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary", "status": "running" }
	]
}
```


### QPS.generator.job_status(job_id)

Get job status.

**Example:**

```python

from quantastica.qps_api import QPS

status = QPS.generator.job_status("PC5PNXiGqhh2HmkX8")

print(status)

```

Example output:

```
{ "_id": "PC5PNXiGqhh2HmkX8", "name": "Experiment", "type": "vectors", "status": "error", "message": "connect ECONNREFUSED" }
```


### QPS.generator.get_job(job_id, wait=True)

Get generator job referenced by ID. If `wait` argument is `True` (default), then function will wait for a job to finish (or fail) before returning. If `wait` is `False`, then job will be immediatelly returned even if it is still running (in which case it will not contain a solution).

**Example:**

```python

from quantastica.qps_api import QPS

job = QPS.generator.get_job("r9LskFoLPQW5w7HTp")

print(job)

```

Example output:

```
{
	"_id": "r9LskFoLPQW5w7HTp",
	"name": "Bell",
	"type": "vectors",
	"source": {
		"vectors": {
			"text1": "[ 1, 0, 0, 0 ]",
			"text2": "[ 1/sqrt(2), 0, 0, 1/sqrt(2) ]",
			"endianness1": "little",
			"endianness2": "little"
		}
	},
	"problem": [
		{
			"input": [ 1, 0, 0, 0 ],
			"output": [ 0.7071067811865475, 0, 0, 0.7071067811865475 ]
		}
	],
	"settings": {
		"max_diff": 0.001,
		"diff_method": "distance",
		"single_solution": False,
		"pre_processing": "",
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0
	},
	"status": "done",
	"output": {
		"circuits": [
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [ 0 ],
						"options": {
							"params": {
								"theta": -1.570796370506287,
								"phi": -3.141592741012573,
								"lambda": -5.327113628387451
							}
						}
					},
					{
						"name": "cx",
						"wires": [ 0, 1 ],
						"options": {}
					}
				],
				"index": 0,
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[0];\ncx q[0], q[1];\n"
			},
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [ 1 ],
						"options": {
							"params": {
								"theta": -1.570796370506287,
								"phi": -3.141592741012573,
								"lambda": -5.327113628387451
							}
						}
					},
					{
						"name": "cx",
						"wires": [ 1, 0 ],
						"options": {}
					}
				],
				"index": 1,
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[1];\ncx q[1], q[0];\n"
			}
		],
		"error_code": 0,
		"message": "",
		"time_taken": 0.002,
		"version": "0.1.0"
	},
	"queuedAt": "2021-02-06T23:39:29.676Z",
	"startedAt": "2021-02-06T23:39:29.926Z",
	"finishedAt": "2021-02-06T23:39:30.383Z"
}
```

### QPS.generator.stop_job(job_id)

Stop running or cancel queued job. Job will be put into `draft` state, and you can start it again later by calling `start_job()`.

**Example:**

```python

from quantastica.qps_api import QPS

response = QPS.generator.stop_job("SNhiCqSCT2WwRWKCd")

print(response)

```

Example output:

```
{ _id: "SNhiCqSCT2WwRWKCd", message: "OK" }
```


### QPS.generator.stop_all_jobs(status_filter=None)

Stop running job / cancel all queued jobs.

- `status_filter` - you can stop only a running job by providing `status_filter="running"` (after this, next job from the queue will be executed). Or, you can cancel all queued jobs by providing `status_filter="queued"` (running job will not be affected - it will continue running).

**Example 1** - stop running job and remove all jobs from queue:

```python

from quantastica.qps_api import QPS

stopped = QPS.generator.stop_all_jobs()

print(stopped)

```

Example output:

```
{
	"stopped": [ 
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary" },
		{ "_id": "R8tJH7XoZ233oTREy", "name": "4Q Gauss", "type": "vectors" }
	]
}
```

**Example 2** - stop only a running job. Next job from queue, if any, will start:

```python

from quantastica.qps_api import QPS

stopped = QPS.generator.stop_all_jobs(status_filter="running")

print(stopped)

```

Example output:

```
{
	"stopped": [
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary" }
	]
}
```

**Example 3** - cancel all queued jobs. Running job will not be affected:

```python

from quantastica.qps_api import QPS

stopped = QPS.generator.stop_all_jobs(status_filter="queued")

print(stopped)

```

Example output:

```
{
	"stopped": [
		{ "_id": "R8tJH7XoZ233oTREy", "name": "4Q Gauss", "type": "vectors" }
	]
}
```


### QPS.generator.start_job(job_id)

Start previously stopped/canceled job (can be any job with status `draft`).

**Example:**

```python

from quantastica.qps_api import QPS

response = QPS.generator.start_job("SNhiCqSCT2WwRWKCd")

print(response)

```

Example output:

```
{ _id: "SNhiCqSCT2WwRWKCd", message: "OK" }
```


## Circuit from vectors

Find quantum circuit from pairs of initial & final state vectors (wave functions).

### QPS.generator.circuit_from_vectors(vector_pairs, endianness = "little", job_name=None, settings = {}, start_job=True)

- `vector_pairs` is list containing vector pairs. Each vector pair is list with 2 elements: initial vector and final vector. All vectors in all pairs must be of same length (same number of qubits).

- `endianness` string. Orientation of bits in state vector (most significant bit/first qubit or least significant bit/first qubit). Can be `little` (like Qiskit) or `big`. Default is `little`.

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default is:

```python

{
	"allowed_gates": "u3,cx",
	"max_diff": 1e-3,
	"diff_method": "distance",
	"single_solution": True,
	"pre_processing": ""
}

```

Note: if `settings` argument is provided, it will overwrite default values, but only provided keys will be overwritten - not entire default settings object.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.


**Example:**

```python

from quantastica.qps_api import QPS

vector_pairs = [
[ [1, 0, 0, 0], [ 0.5+0j,  0.5+0j,  0.5+0j,  0.5+0j ] ],
[ [0, 1, 0, 0], [ 0.5+0j,  0+0.5j, -0.5+0j,  0-0.5j ] ],
[ [0, 0, 1, 0], [ 0.5+0j, -0.5+0j,  0.5+0j, -0.5+0j ] ],
[ [0, 0, 0, 1], [ 0.5+0j,  0-0.5j, -0.5+0j,  0+0.5j ] ]
]

job_id = QPS.generator.circuit_from_vectors(vector_pairs, settings = { "instruction_set": ["h", "cu1", "swap"], "single_solution": False })

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
swap q[0], q[1];
cu1 (2.356194496154785) q[0], q[1];
h q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
cu1 (2.356194496154785) q[0], q[1];
h q[0];
swap q[0], q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
cu1 (2.356194496154785) q[0], q[1];
swap q[0], q[1];
h q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
swap q[0], q[1];
h q[0];
cu1 (2.356194496154785) q[0], q[1];
h q[1];
```

## State preparation

Get circuit which will transform ground state (all qubits reset) to desired final state vector.

### QPS.generator.state_preparation(final_vector, endianness = "little", job_name=None, settings = {}, start_job=True)

- `final_vector` is target vector.

- `endianness` string. Orientation of bits in state vector (most significant bit/first qubit or least significant bit/first qubit). Can be `little` (like Qiskit) or `big`. Default is `little`.

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default: see `QPS.generator.circuit_from_vectors()`.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.


**Example:**

```python

from quantastica.qps_api import QPS

desired_state = [0.5, 0.5, 0.5, 0.5]

job_id = QPS.generator.state_preparation(desired_state, settings = { "instruction_set": ["u3", "cx"] })

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
u3 (1.570796370506287, 0, 1.217840194702148) q[0];
u3 (1.570796370506287, 0, 0.621559917926788) q[1];
```


## Transpile

Transpile circuit (change instruction set).

### QPS.generator.transpile(input_qasm, method="replace_blocks", method_options={}, job_name=None, settings = {}, start_job=True):

- `input_qasm` is string containing OpenQASM 2.0 code.

- `method` is method name string. Can be one of: "replace_circuit", "replace_blocks", "replace_gates". Default: "replace_blocks".

- `method_options` dict with following structure:

	- If method is `replace_blocks` then: `{ "block_size": 2, "two_pass": False }` (maximum block size is 4).

	- For other methods: no options (`method_options` is ignored)

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default is:

```python

{
	"allowed_gates": "u3,cx",
	"max_diff": 1e-3,
	"diff_method": "distance",
	"single_solution": True,
	"pre_processing": "experimental1"
}

```

Default `diff_method` is `distance`, which means that input and output circuit's global phase will match. That also means longer running time and possibly deeper output circuit (especially with new IBM's instruction set `id, x, sx, rz, cx`). If you are relaxed about global phase (like Qiskit's transpile method), then provide `"diff_method": "ignorephase"` in `settings`.

Note: if `settings` argument is provided, it will overwrite default values, but only provided keys will be overwritten - not entire default settings object.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.


**Example:**

```python

from quantastica.qps_api import QPS

input_qasm = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0], q[1];
"""

job_id = QPS.generator.transpile(input_qasm, settings = { "instruction_set": ["id", "x", "sx", "rz", "cx"], "diff_method": "ignorephase" })

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
sx q[0];
rz (1.570796370506287) q[0];
sx q[0];
cx q[0], q[1];
```

## Decompose matrix

Decompose unitary matrix (find circuit from matrix).

### QPS.generator.decompose_unitary(unitary, endianness = "big", job_name=None, settings = {}, start_job=True)

- `unitary` matrix operator.

- `endianness` - orientation of the matrix. Can be `little` endian (like Qiskit) or `big` endian. Default is `big`. Note that default endianness of the matrix differs from default endianness of vectors in other methods. That's to be aligned with QPS. In Qiskit, both matrices and vectors are `little` endian. So, if you are solving unitary from Qiskit then provide `endianness = "little"` argument.

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default is:

```python
{
	"allowed_gates": "u3,cx",
	"max_diff": 1e-3,
	"diff_method": "distance",
	"single_solution": True,
	"pre_processing": ""
}
```

Note: if `settings` argument is provided, it will overwrite default values, but only provided keys will be overwritten - not entire default settings object.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.


**Example:**

```python

from quantastica.qps_api import QPS

unitary = [
[ 0.5+0.0j,  0.5+0.0j,  0.5+0.0j,  0.5+0.0j],
[ 0.5+0.0j,  0.5+0.0j, -0.5+0.0j, -0.5+0.0j],
[ 0.5+0.0j, -0.5+0.0j,  0.0+0.5j,  0.0-0.5j],
[ 0.5+0.0j, -0.5+0.0j,  0.0-0.5j,  0.0+0.5j]
]

job_id = QPS.generator.decompose_unitary(unitary, settings = { "instruction_set": ["h", "cu1", "swap"], "single_solution": False })

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
swap q[0], q[1];
cu1 (1.570796370506287) q[0], q[1];
h q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
cu1 (1.570796370506287) q[0], q[1];
h q[0];
swap q[0], q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];
cu1 (1.570796370506287) q[0], q[1];
swap q[0], q[1];
h q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
swap q[0], q[1];
h q[0];
cu1 (1.570796370506287) q[0], q[1];
h q[1];
```


## Create algorithm from truth table

Create circuit which implements logical expression whose truth table is given.

### QPS.generator.circuit_from_truth_table(truth_table_csv, column_defs, csv_delimiter=None, additional_qubits=1, job_name=None, settings={}, start_job=True):

- `truth_table_csv` is string containing truth table in CSV format

- `column_defs` list of strings describing each column from truth table: `"input"`, `"output"` or `"ignore"`

- `csv_delimiter` CSV column delimiter char: `None`, `","` (comma) or `"\t"` (tab). If delimiter is `None` (default) it will be automatically detected.

- `additional_qubits` number of qubits to add (to displace input and output qubits).

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default is:

```python
{
	"allowed_gates": "x,cx,ccx,swap",
	"max_diff": 1e-3,
	"diff_method": "distance",
	"single_solution": True,
	"pre_processing": ""
}
```

**Example:**

```python

from quantastica.qps_api import QPS

truth_table = """
A,B,A_NAND_B
0,0,1
0,1,1
1,0,1
1,1,0
"""

job_id = QPS.generator.circuit_from_truth_table(truth_table, ["input", "input", "output"])

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	raise Exception(job_output["message"])
else:
	if(len(job_output["circuits"]) == 0):
		raise Exception("No results.")
	else:
		for circuit in job_output["circuits"]:
			print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
x q[2];
ccx q[0], q[1], q[2];
```


## Run problem file

Solve problem provided in internal format used by generator.

### QPS.generator.solve(problem, settings = {}, start_job=True)

- `problem` object - generator job exported to json from QPS.

- `settings` argument is optional. If provided, it will overwrite keys in `problem.settings`. Note that only provided keys will be overwritten - not entire `problem.settings` object.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.


**Example:**

```python

from quantastica.qps_api import QPS

problem = {
	"name": "Bell",
	"type": "vectors",
	"source": {
		"vectors": {
			"text1": "[ 1, 0, 0, 0 ]",
			"text2": "[ 1/sqrt(2), 0, 0, 1/sqrt(2) ]",
			"endianness1": "little",
			"endianness2": "little"
		}
	},
	"problem": [
		{
			"input": [
				1,
				0,
				0,
				0
			],
			"output": [
				0.7071067811865475,
				0,
				0,
				0.7071067811865475
			]
		}
	],
	"settings": {
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0,
		"max_diff": 0.001,
		"diff_method": "distance",
		"single_solution": False,
		"pre_processing": ""
	}
}

job_id = QPS.generator.solve(problem)

job = QPS.generator.get_job(job_id, wait=True)

job_status = job["status"]
job_output = job["output"]

if(job_status == "error"):
	print(job_output["message"])
else:
	for circuit in job_output["circuits"]:
		print(circuit["qasm"])

```

Example output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
u3 (-1.570796370506287, -3.141592741012573, -2.675650835037231) q[0];
cx q[0], q[1];

OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
u3 (-1.570796370506287, -3.141592741012573, -2.675650835037231) q[1];
cx q[1], q[0];
```


## Generator output format

Generator job object has following structure:

```javascript
{
	"name"       : String,
	"type"       : String,
	"source"     : Object,
	"problem"    : Array,
	"settings"   : Object,
	"status"     : String,
	"output"     : Object,
	"queuedAt"   : String,
	"startedAt"  : String,
	"finishedAt" : String
}
```

Keys important to user are:

- `name` String: name of the job

- `status` String: can be `draft`, `queued`, `running`, `error`, `done`.

- `output` Object with following structure:

```javascript
{
	"error_code" : Integer,
	"message"    : String,
	"time_taken" : Float,
	"version"    : String,
	"circuits"   : Array of Object
}
```

- `error_code` Integer: 0 on success, non-zero on error

- `message` String: error message if error code is non-zero

- `time_taken` Float: number of seconds

- `version` String: generator version

- `circuits` Array: resulting circuits. Each is object with following structure:

```javascript
{
	"qubits"  : Integer,
	"cregs"   : Array,
	"program" : Array,
	"diff"    : Float,
	"index"   : Integer,
	"qasm"    : String
}
```

Key important to user is:

- `qasm` OpenQASM 2.0 source code of the resulting circuit.


**Example job object with output:**

```python
{
	"_id": "r9LskFoLPQW5w7HTp",
	"name": "Bell",
	"type": "vectors",
	"source": {
		"vectors": {
			"text1": "[ 1, 0, 0, 0 ]",
			"text2": "[ 1/sqrt(2), 0, 0, 1/sqrt(2) ]",
			"endianness1": "little",
			"endianness2": "little"
		}
	},
	"problem": [
		{
			"input": [ 1, 0, 0, 0 ],
			"output": [ 0.7071067811865475, 0, 0, 0.7071067811865475 ]
		}
	],
	"settings": {
		"max_diff": 0.001,
		"diff_method": "distance",
		"single_solution": False,
		"pre_processing": "",
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0
	},
	"status": "done",
	"output": {
		"circuits": [
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [ 0 ],
						"options": {
							"params": {
								"theta": -1.570796370506287,
								"phi": -3.141592741012573,
								"lambda": -5.327113628387451
							}
						}
					},
					{
						"name": "cx",
						"wires": [ 0, 1 ],
						"options": {}
					}
				],
				"index": 0,
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[0];\ncx q[0], q[1];\n"
			},
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [ 1 ],
						"options": {
							"params": {
								"theta": -1.570796370506287,
								"phi": -3.141592741012573,
								"lambda": -5.327113628387451
							}
						}
					},
					{
						"name": "cx",
						"wires": [ 1, 0 ],
						"options": {}
					}
				],
				"index": 1,
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[1];\ncx q[1], q[0];\n"
			}
		],
		"error_code": 0,
		"message": "",
		"time_taken": 0.002,
		"version": "0.1.0"
	},
	"createdAt": "2021-02-06T23:39:29.108Z",
	"modifiedAt": "2021-02-06T23:39:30.383Z",
	"queuedAt": "2021-02-06T23:39:29.676Z",
	"startedAt": "2021-02-06T23:39:29.926Z",
	"finishedAt": "2021-02-06T23:39:30.383Z"
}
```


## Using Generator with Qiskit

Generator is using OpenQASM 2.0 format for input and output, so integration with Qiskit (and other frameworks that support QASM) is easy.

**Example** transpile Qiskit circuit:

```python

from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import Operator

from quantastica.qps_api import QPS

# Generate random Qiskit circuit
qc = random_circuit(5, 5, measure=False)

# Get QASM code
input_qasm = qc.qasm()

# Transpile with generator
job_id = QPS.generator.transpile(input_qasm, settings = { "instruction_set": ["id", "u3", "cx"], "diff_method": "ignorephase" })
job = QPS.generator.get_job(job_id, wait=True)
job_status = job["status"]
job_output = job["output"]
if(job_status == "error"):
    raise Exception(job_output["message"])

transpiled_circuit = job_output["circuits"][0]

# Get QASM code
transpiled_qasm = transpiled_circuit["qasm"]

# Create Qiskit circuit
transpiled_qc = QuantumCircuit.from_qasm_str(transpiled_qasm)

# Show circuit
print("Depth:", transpiled_qc.depth())
print("Ops:", sum(j for i, j in transpiled_qc.count_ops().items()))
display(transpiled_qc.draw(output="mpl"))

```

