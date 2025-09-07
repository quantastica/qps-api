# Quantum Programming Studio API

Python wrapper for [Quantum Programming Studio](https://quantum-circuit.com/) HTTP API.


## Install and configure

**1. Install QPS API package:**

```bash
pip install quantastica-qps-api
```

**2. Find your QPS API token:**

[Login](https://quantum-circuit.com/login) to Quantum Programming Studio, go to [Profile -> API Access](https://quantum-circuit.com/user_settings/api) and copy your API token.

**3. Configure QPS API package with your API token:**

Make sure that environment variable `QPS_API_KEY` contains your API token.

**Now you are ready to use QPS API.**


Alternativelly, you can temporary set your API token:

```python
from quantastica.qps_api import QPS

QPS.use_account("YOUR_API_TOKEN")
```


You can also save your API token to local configuration file for future use:

```python
from quantastica.qps_api import QPS

QPS.save_account("YOUR_API_TOKEN")
```

*Note: saving API token in local configuration file is not recommented and we advise you to use environment variable instead.*


## Account management

**QPS.use_account(api_token, api_url=None)**

Method will temporary set provided API token to be used. This will not store your token.

*Note: it is not recommended to expose your API token in source code. Please use environment variable instead*


**QPS.save_account(api_token, api_url=None)**

Method will create configuration file and your api token will be stored there for future use.

If needed, you can clear your token by running `QPS.save_account("")` (or by deleting a configuration file).

*Note: it is not recommended to store your API token in configuration file. Please use environment variable instead*


**QPS.load_account()**

Method will load previously stored API token from local configuration file.

*Note: it is not recommended to keep your API token in configuration file. Please use environment variable instead*


**QPS.config_path()**

You can get config file path by running `QPS.config_path()`.

Default configuration file path:

- On Unix, directory is obtained from environment variable HOME if it is set; otherwise the current user’s home directory is looked up in the password directory through the built-in module pwd.

- On Windows, USERPROFILE will be used if set, otherwise a combination of HOMEPATH and HOMEDRIVE will be used.



## Synthesis and transpilation API

Synthesis and transpilation tool can be used to:

- create quantum circuit from state vectors

- create quantum circuit from truth table

- create quantum circuit from unitary matrix (decompose unitary matrix)

- transpile circuits (change instruction set)


### Circuit from vectors

Find quantum circuit from pairs of initial & final state vectors (wave functions).

**QPS.synth.circuit_from_vectors(vector_pairs, endianness = "little", job_name=None, settings = {}, start_job=True)**

- `vector_pairs` is list containing vector pairs. Each vector pair is list with 2 elements: initial vector and final vector. All vectors in all pairs must be of same length (same number of qubits).

- `endianness` string. Orientation of bits in state vector (most significant bit/first qubit or least significant bit/first qubit). Can be `little` (like Qiskit) or `big`. Default is `little`.

- `job_name` string is optional. You can give it a human readable name.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.

- `settings` object is optional. Default is:

```python
{
	"strategy": "strategy_a",
	"pre_processing": "",
	"allowed_gates": "u3,cx",
	"min_gates": 0,
	"max_gates": 0,
	"max_diff": 0.001,
	"diff_method": "ignorephase",
	"max_duration": 0,
	"single_solution": True
}
```

**Settings**

- `strategy` string. Can be one of: `strategy_a` (brute force or heuristics) and `strategy_b` OptigenQ+QSD (OptigenQ is Quantastica's method to find unitary matrix from pairs of vectors, and QSD is used to decompose matrix and return circuit). Default is `strategy_a`.

- `pre_processing` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `stable`, `experimental_1`, `experimental_2`, `experimental_3`, `experimental_5`. Default is empty string (Empty string means "use default" which is currently `stable`).

- `allowed_gates` string. Used only with `strategy_a` (brute force or heuristics). Comma delimited gate names (instruction set) to use. Default is `u3,cx`. With `strategy_b` instruction set is fixed to `u3,cx` (you can transpile returned circuit later using `QPS.synth.transpile()` method.

- `min_gates` and `max_gates` integer. Used only with `strategy_a` (brute force or heuristics). Default is `0` (no limits).

- `max_diff` float. Used only with `strategy_a` (brute force or heuristics). Default is `0.001` (1e-3).

- `diff_method` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `distance` (exact match), `ignorephase` (match up to a global phase) and `abs` (match absolute values). Default is `ignorephase`.

- `max_duration` integer. Timeout in seconds. Solver will stop after specified number of seconds and error will be returned. Useful with brute force algorithm which has high computational complexity and can run for a very long time. You can decide when to stop (and for example proceed with the next job which is using different method and is waiting in a queue - if you prepared it). Default is `0` which means "maximum allowed by your subscription plan". Free plan has limit of a few seconds (subject to change).

- `single_solution` boolean. Used only with `strategy_a` (brute force or heuristics). When `True`, solver will stop when first solution was found. When `False` solver will return all possible configurations of a circuit.

Note: if `settings` argument is provided, it will overwrite default settings, but only provided keys will be overwritten - not entire default settings object.


**Example:**

```python
from quantastica.qps_api import QPS

vector_pairs = [
[ [1, 0, 0, 0], [ 0.5+0j,  0.5+0j,  0.5+0j,  0.5+0j ] ],
[ [0, 1, 0, 0], [ 0.5+0j,  0+0.5j, -0.5+0j,  0-0.5j ] ],
[ [0, 0, 1, 0], [ 0.5+0j, -0.5+0j,  0.5+0j, -0.5+0j ] ],
[ [0, 0, 0, 1], [ 0.5+0j,  0-0.5j, -0.5+0j,  0+0.5j ] ]
]

job_id = QPS.synth.circuit_from_vectors(vector_pairs, settings = { "instruction_set": ["h", "cu1", "swap"], "single_solution": False })

job = QPS.synth.get_job(job_id, wait=True)

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

### State preparation

Get circuit which prepares provided state.

**QPS.synth.state_preparation(final_vector, endianness = "little", job_name=None, settings = {}, start_job=True)**

- `final_vector` is target vector.

- `endianness` string. Orientation of bits in state vector (most significant bit/first qubit or least significant bit/first qubit). Can be `little` (like Qiskit) or `big`. Default is `little`.

- `job_name` string is optional. You can give it a human readable name.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.

- `settings` object is optional. Default is:

```python
{
	"strategy": "strategy_a",
	"pre_processing": "",
	"allowed_gates": "u3,cx",
	"min_gates": 0,
	"max_gates": 0,
	"max_diff": 0.001,
	"diff_method": "ignorephase",
	"max_duration": 0,
	"single_solution": True
}

```

**Settings**

- `strategy` string. Can be one of: `strategy_a` (brute force or heuristics) and `strategy_b` OptigenQ+QSD (OptigenQ is Quantastica's method to find unitary matrix from pairs of vectors, after which QSD is used to decompose matrix and return circuit). Default is `strategy_a`.

- `pre_processing` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `stable`, `experimental_1`, `experimental_2`, `experimental_3`, `experimental_5`. Default is empty string (Empty string means "use default" which is currently `stable`).

- `allowed_gates` string. Used only with `strategy_a` (brute force or heuristics). Comma delimited gate names (instruction set) to use. Default is `u3,cx`. With `strategy_b` instruction set is fixed to `u3,cx` (you can transpile returned circuit later using `QPS.synth.transpile()` method.

- `min_gates` and `max_gates` integer. Used only with `strategy_a` (brute force or heuristics). Default is `0` (no limits).

- `max_diff` float. Used only with `strategy_a` (brute force or heuristics). Default is `0.001` (1e-3).

- `diff_method` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `distance` (exact match), `ignorephase` (match up to a global phase) and `abs` (match absolute values). Default is `ignorephase`.

- `max_duration` integer. Timeout in seconds. Solver will stop after specified number of seconds and error will be returned. Useful with brute force algorithm which has high computational complexity and can run for a very long time. You can decide when to stop (and for example proceed with the next job which is using different method and is waiting in a queue - if you prepared it). Default is `0` which means "maximum allowed by your subscription plan". Free plan has limit of a few seconds (subject to change).

- `single_solution` boolean. Used only with `strategy_a` (brute force or heuristics). When `True`, solver will stop when first solution was found. When `False` solver will return all possible configurations of a circuit.

Note: if `settings` argument is provided, it will overwrite default settings, but only provided keys will be overwritten - not entire default settings object.


**Example:**

```python
from quantastica.qps_api import QPS

desired_state = [0.5, 0.5, 0.5, 0.5]

job_id = QPS.synth.state_preparation(desired_state, settings = { "instruction_set": ["u3", "cx"] })

job = QPS.synth.get_job(job_id, wait=True)

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


### Transpile

Transpile circuit (change instruction set).

**QPS.synth.transpile(input_qasm, method="replace_blocks", method_options={}, job_name=None, settings = {}, start_job=True)**

- `input_qasm` is string containing OpenQASM 2.0 code.

- `method` is method name string. Can be one of: "replace_circuit", "replace_blocks", "replace_gates". Default: "replace_blocks".

- `method_options` dict with following structure:

	- If method is `replace_blocks` then: `{ "block_size": 2, "two_pass": False }` (maximum block size is 4).

	- For other methods: no options (`method_options` is ignored)

- `job_name` string is optional. You can give it a human readable name.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.

- `settings` object is optional. Default is:

```python
{
	"pre_processing": "experimental1",
	"allowed_gates": "u3,cx",
	"max_diff": 0.001,
	"diff_method": "ignorephase",
	"max_duration": 0
}

```

**Settings**

- `pre_processing` string. Can be one of: `stable`, `experimental_1`, `experimental_2`, `experimental_3`, `experimental_5`. Default is empty string (Empty string means "use default" which is currently `stable`).

- `allowed_gates` string. Comma delimited gate names (instruction set) to use. Default is `u3,cx`.

- `max_diff` float. Default is `0.001` (1e-3).

- `diff_method` string. Can be one of: `distance` (exact match), `ignorephase` (match up to a global phase) and `abs` (match absolute values). Default is `ignorephase`.

- `max_duration` integer. Timeout in seconds. Solver will stop after specified number of seconds and error will be returned. Default is `0` which means "maximum allowed by your subscription plan". Free plan has limit of a few seconds (subject to change).

Note: if `settings` argument is provided, it will overwrite default settings, but only provided keys will be overwritten - not entire default settings object.


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

job_id = QPS.synth.transpile(input_qasm, settings = { "instruction_set": ["id", "x", "sx", "rz", "cx"], "diff_method": "ignorephase" })

job = QPS.synth.get_job(job_id, wait=True)

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

### Decompose matrix

Decompose unitary matrix (find circuit from matrix).

**QPS.synth.decompose_unitary(unitary, endianness="big", job_name=None, settings = {}, start_job=True)**

- `unitary` matrix operator.

- `endianness` - orientation of the matrix. Can be `little` endian (like Qiskit) or `big` endian. Default is `big`. Note that default endianness of the matrix differs from default endianness of vectors in other methods. That's to be aligned with QPS. In Qiskit, both matrices and vectors are `little` endian. So, if you are solving unitary from Qiskit then provide `endianness = "little"` argument.

- `job_name` string is optional. You can give it a human readable name.

- `start_job` if this argument is `True` (default) the job will be immediatelly sent to execution queue. If `start_job` is `False` then it will stay in `draft` state and you will be able to start it later by calling `start_job()` method.

- `settings` object is optional. Default is:

```python
{
	"strategy": "strategy_a",
	"pre_processing": "",
	"allowed_gates": "u3,cx",
	"coupling_map": [],
	"min_gates": 0,
	"max_gates": 0,
	"max_diff": 0.001,
	"diff_method": "ignorephase",
	"max_duration": 0,
	"single_solution": True
}

```

**Settings**

- `strategy` string. Can be one of: `strategy_a` (brute force or heuristics) and `strategy_b` QSD. Default is `strategy_a`. Note that `strategy_a` (brute force or heuristics) returns circuit with optimal or near optimal depth, but this method has very high computational complexity and can run for a very long time (depending on number of qubits and total number of gates in the resulting circuit).

- `pre_processing` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `stable`, `experimental_1` and `experimental_5`. Default is empty string (Empty string means "use default" which is currently `stable`). Experimental methods have lower computational complexity and should finish sooner, but that depends on many factors, so you should try all methods and see what works best for your particular problem.

- `allowed_gates` string. Used only with `strategy_a` (brute force or heuristics). Comma delimited gate names (instruction set) to use. Default is `u3,cx`. With `strategy_b` instruction set is fixed to `u3,cx` (you can transpile returned circuit later using `QPS.synth.transpile()` method.

- `min_gates` and `max_gates` integer. Used only with `strategy_a` (brute force or heuristics). Default is `0` (no limits).

- `max_diff` float. Used only with `strategy_a` (brute force or heuristics). Default is `0.001` (1e-3).

- `diff_method` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `distance` (exact match), `ignorephase` (match up to a global phase) `hs` (match up to a global phase using faster method) and `abs` (match absolute values). Default is `ignorephase`.

- `max_duration` integer. Timeout in seconds. Solver will stop after specified number of seconds and error will be returned. Useful with brute force algorithm which has high computational complexity and can run for a very long time. You can decide when to stop (and for example proceed with the next job which is using different method and is waiting in a queue - if you prepared it). Default is `0` which means "maximum allowed by your subscription plan". Free plan has limit of a few seconds (subject to change).

- `single_solution` boolean. Used only with `strategy_a` (brute force or heuristics). When `True`, solver will stop when first solution was found. When `False` solver will return all possible configurations of a circuit.

Note: if `settings` argument is provided, it will overwrite default settings, but only provided keys will be overwritten - not entire default settings object.


**Example:**

```python
from quantastica.qps_api import QPS

unitary = [
[ 0.5+0.0j,  0.5+0.0j,  0.5+0.0j,  0.5+0.0j],
[ 0.5+0.0j,  0.5+0.0j, -0.5+0.0j, -0.5+0.0j],
[ 0.5+0.0j, -0.5+0.0j,  0.0+0.5j,  0.0-0.5j],
[ 0.5+0.0j, -0.5+0.0j,  0.0-0.5j,  0.0+0.5j]
]

job_id = QPS.synth.decompose_unitary(unitary, settings = { "instruction_set": ["h", "cu1", "swap"], "single_solution": False })

job = QPS.synth.get_job(job_id, wait=True)

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


### Create circuit from truth table

Create circuit which implements logical expression whose truth table is given.

**QPS.synth.circuit_from_truth_table(truth_table_csv, column_defs, csv_delimiter=None, additional_qubits=1, job_name=None, settings={}, start_job=True)**

- `truth_table_csv` is string containing truth table in CSV format

- `column_defs` list of strings describing each column from truth table: `"input"`, `"output"` or `"ignore"`

- `csv_delimiter` CSV column delimiter char: `None`, `","` (comma) or `"\t"` (tab). If delimiter is `None` (default) it will be automatically detected.

- `additional_qubits` number of qubits to add (to displace input and output qubits).

- `job_name` string is optional. You can give it a human readable name.

- `settings` object is optional. Default is:

```python
{
	"pre_processing": "",
	"allowed_gates": "x,cx,ccx,swap",
	"coupling_map": [],
	"min_gates": 0,
	"max_gates": 0,
	"max_diff": 0.001,
	"diff_method": "ignorephase",
	"max_duration": 0,
	"single_solution": True
}

```

**Settings**

- `pre_processing` string. Can be one of: `stable`, `experimental_1` and `experimental_5`. Default is empty string (Empty string means "use default" which is currently `stable`).

- `allowed_gates` string. Comma delimited gate names (instruction set) to use. Default is `x,cx,ccx,swap`.

- `min_gates` and `max_gates` integer. Default is `0` (no limits).

- `max_diff` float. Used only with `strategy_a` (brute force or heuristics). Default is `0.001` (1e-3).

- `diff_method` string. Used only with `strategy_a` (brute force or heuristics). Can be one of: `distance` (exact match), `ignorephase` (match up to a global phase) and `abs` (match absolute values). Default is `ignorephase`.

- `max_duration` integer. Timeout in seconds. Solver will stop after specified number of seconds and error will be returned. Useful with brute force algorithm which has high computational complexity and can run for a very long time. You can decide when to stop (and for example proceed with the next job which is using different method and is waiting in a queue - if you prepared it). Default is `0` which means "maximum allowed by your subscription plan". Free plan has limit of a few seconds (subject to change).

- `single_solution` boolean. Used only with `strategy_a` (brute force or heuristics). When `True`, solver will stop when first solution was found. When `False` solver will return all possible configurations of a circuit.

Note: if `settings` argument is provided, it will overwrite default settings, but only provided keys will be overwritten - not entire default settings object.


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

job_id = QPS.synth.circuit_from_truth_table(truth_table, ["input", "input", "output"])

job = QPS.synth.get_job(job_id, wait=True)

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


### Run synthesizer or transpiler job defined in JSON file

Solve problem provided in JSON format used by synthesizer and transpiler.

**QPS.synth.solve(problem, settings = {}, start_job=True)**

- `problem` object (e.g. job exported to json from Quantum Programming studio).

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
		"strategy": "strategy_a",
		"pre_processing": "",
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0,
		"max_diff": 0.001,
		"diff_method": "distance",
		"max_duration": 0,
		"single_solution": False
	}
}

job_id = QPS.synth.solve(problem)

job = QPS.synth.get_job(job_id, wait=True)

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


### Synthesizer/transpiler output format

Finished job object has following structure:

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

- `version` String: solver version

- `circuits` Array: resulting circuits. Each is object with following structure:

```javascript
{
	"qubits"  : Integer,
	"cregs"   : Array,
	"program" : Array,
	"diff"    : Float,
	"index"   : Integer,
	"qasm"    : String,
	"qasmExt" : String
}
```

Keys important to user are:

- `qasm` OpenQASM 2.0 source code of the resulting circuit.

- `qasmExt` OpenQASM 2.0 with extended instruction set (all gates supported by Quantum Programming Studio).

Difference between `qasm` and `qasmExt`: if circuit contains gate supported by QPS but not directly supported by OpenQASM 2.0 then `qasm` will contain equivalent circuit transpiled to OpenQASM 2.0 instruction set, but `qasmExt` will contain gates as is.

For example if circuit contains IONQ native gate `gpi2(2.51678906856393)` on first qubit:

`qasm` will be:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
u3 (1.5707963267948966, 0.9459927417690333, -0.9459927417690333) q[0];
```

`qasmExt` will contain:
```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
gpi2 (2.51678906856393) q[0];
```


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
		"strategy": "strategy_a",
		"pre_processing": "",
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0,
		"max_diff": 0.001,
		"diff_method": "distance",
		"max_duration": 0,
		"single_solution": False
	},
	"output": {
		"circuits": [
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [
							0
						],
						"options": {
							"params": {
								"theta": 1.570796326794896,
								"phi": 0,
								"lambda": 1.456034103897321
							}
						}
					},
					{
						"name": "cx",
						"wires": [
							0,
							1
						],
						"options": {}
					}
				],
				"index": 0
			},
			{
				"qubits": 2,
				"cregs": [],
				"diff": 0,
				"program": [
					{
						"name": "u3",
						"wires": [
							1
						],
						"options": {
							"params": {
								"theta": 1.570796326794896,
								"phi": 0,
								"lambda": 1.456034103897321
							}
						}
					},
					{
						"name": "cx",
						"wires": [
							1,
							0
						],
						"options": {}
					}
				],
				"index": 1
			}
		],
		"error_code": 0,
		"message": "",
		"time_taken": 0.008,
		"version": "0.1.0",
		"stats": {
			"result_count": 2
		}
	},
	"createdAt": "2021-02-06T23:39:29.108Z",
	"modifiedAt": "2021-02-06T23:39:30.383Z",
	"queuedAt": "2021-02-06T23:39:29.676Z",
	"startedAt": "2021-02-06T23:39:29.926Z",
	"finishedAt": "2021-02-06T23:39:30.383Z",
	"status": "done"
}

```


### Using synthesizer and transpiler with Qiskit

Format used for input and output is OpenQASM 2.0, so integration with Qiskit (and other frameworks that support OpenQASM) is easy.

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

# Transpile with QPS
job_id = QPS.synth.transpile(input_qasm, settings = { "instruction_set": ["id", "u3", "cx"], "diff_method": "ignorephase" })
job = QPS.synth.get_job(job_id, wait=True)
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


### Job management

Problem sent to solver (synthesizer or transpiler) is called a "job". Each job has unique ID. Solver is resource intensive tool, so it is configured to execute only one job at a time. While solver is processing a job, other jobs are queued. When solver finishes a job, it takes the next one from the queue.

API provides functions for job manipulation: you can list all jobs (filtered by status), stop running job, cancel queued jobs, stop/cancel all jobs, start previously canceled (draft) job, etc.

**QPS.synth.list_jobs(status_filter=None)**

List all jobs, optionally filtered by status.

- `status_filter` String, optional. Can be: `draft`, `queued`, `running`, `error`, `done`.


**Example 1** - list all (unfiltered) jobs:

```python
from quantastica.qps_api import QPS

jobs = QPS.synth.list_jobs()

print(jobs)

```

Example output:

```python
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

jobs = QPS.synth.list_jobs(status_filter="running")

print(jobs)

```

Example output:

```python
{
	"list": [
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary", "status": "running" }
	]
}
```


**QPS.synth.job_status(job_id)**

Get job status.

**Example:**

```python
from quantastica.qps_api import QPS

status = QPS.synth.job_status("PC5PNXiGqhh2HmkX8")

print(status)

```

Example output:

```python
{ "_id": "PC5PNXiGqhh2HmkX8", "name": "Experiment", "type": "vectors", "status": "error", "message": "connect ECONNREFUSED" }
```


**QPS.synth.get_job(job_id, wait=True)**

Get job referenced by ID. If `wait` argument is `True` (default), then function will wait for a job to finish (or fail) before returning. If `wait` is `False`, then job will be immediatelly returned even if it is still running (in which case it will not contain a solution).

**Example:**

```python
from quantastica.qps_api import QPS

job = QPS.synth.get_job("r9LskFoLPQW5w7HTp")

print(job)

```

Example output:

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
		"max_duration": 0,
		"allowed_gates": "u3,cx",
		"coupling_map": [],
		"min_gates": 0,
		"max_gates": 0,
		"pre_processing": "",
		"strategy": "strategy_a",
		"max_diff": 0.001,
		"diff_method": "distance",
		"single_solution": False
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
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[0];\ncx q[0], q[1];\n",
				"qasmExt": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[0];\ncx q[0], q[1];\n"
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
				"qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[1];\ncx q[1], q[0];\n",
				"qasmExt": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\nu3 (-1.570796370506287, -3.141592741012573, -5.327113628387451) q[1];\ncx q[1], q[0];\n"				
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

**QPS.synth.stop_job(job_id)**

Stop running or cancel queued job. Job will be put into `draft` state, and you can start it again later by calling `start_job()`.

**Example:**

```python
from quantastica.qps_api import QPS

response = QPS.synth.stop_job("SNhiCqSCT2WwRWKCd")

print(response)

```

Example output:

```python
{ "_id": "SNhiCqSCT2WwRWKCd", "message": "OK" }
```


**QPS.synth.stop_all_jobs(status_filter=None)**

Stop running job / cancel all queued jobs.

- `status_filter` - you can stop only a running job by providing `status_filter="running"` (after this, next job from the queue will be executed). Or, you can cancel all queued jobs by providing `status_filter="queued"` (running job will not be affected - it will continue running).

**Example 1** - stop running job and remove all jobs from queue:

```python
from quantastica.qps_api import QPS

stopped = QPS.synth.stop_all_jobs()

print(stopped)

```

Example output:

```python
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

stopped = QPS.synth.stop_all_jobs(status_filter="running")

print(stopped)

```

Example output:

```python
{
	"stopped": [
		{ "_id": "SNhiCqSCT2WwRWKCd", "name": "Decompose", "type": "unitary" }
	]
}
```

**Example 3** - cancel all queued jobs. Running job will not be affected:

```python
from quantastica.qps_api import QPS

stopped = QPS.synth.stop_all_jobs(status_filter="queued")

print(stopped)

```

Example output:

```python
{
	"stopped": [
		{ "_id": "R8tJH7XoZ233oTREy", "name": "4Q Gauss", "type": "vectors" }
	]
}
```


**QPS.synth.start_job(job_id)**

Start previously stopped/canceled job (can be any job with status `draft`).

**Example:**

```python
from quantastica.qps_api import QPS

response = QPS.synth.start_job("SNhiCqSCT2WwRWKCd")

print(response)

```

Example output:

```python
{ "_id": "SNhiCqSCT2WwRWKCd", "message": "OK" }
```


## Quantum Language Converter API

[Quantum Language Converter](https://quantastica.com/#converters) is a tool which converts quantum program between different quantum programming languages and frameworks. It is also available as a [q-convert](https://www.npmjs.com/package/q-convert) command line tool and as a web UI at [https://quantum-circuit.com/qconvert](https://quantum-circuit.com/qconvert).

QPS has integrated quantum language converter API which you can access directly from python code:


**QPS.converter.convert(input, source, dest)**

Converts `input` quantum program given as string from `source` format into `dest` format.

- `input` String. Program source code

- `source` String. Input format:

	- `qasm` [OpenQASM 2.0](https://github.com/Qiskit/openqasm) source code
	- `quil` [Quil](https://arxiv.org/abs/1608.03355) source code
	- `qobj` [QObj](https://arxiv.org/abs/1809.03452)
	- `ionq` [IONQ](https://docs.ionq.com/) (json)
	- `quantum-circuit` [quantum-circuit](https://www.npmjs.com/package/quantum-circuit) object (json)
	- `toaster` [Qubit Toaster](https://quantastica.com/#toaster) object (json)

- `dest` String. Output format:

	- `qiskit` [Qiskit](https://qiskit.org/documentation/)
	- `qasm` [OpenQASM 2.0](https://github.com/Qiskit/openqasm)
	- `qasm-ext` OpenQASM 2.0 with complete instruction set supported by QPS (and other Quantastica tools)
	- `qobj` [QObj](https://arxiv.org/abs/1809.03452)
	- `quil` [Quil](https://arxiv.org/abs/1608.03355)
	- `pyquil` [pyQuil](http://docs.rigetti.com/en/latest/index.html)
	- `cudaq` [CudaQ](https://nvidia.github.io/cuda-quantum/latest/index.html)
	- `braket` [Braket](https://docs.aws.amazon.com/braket/)
	- `cirq` [Cirq](https://github.com/quantumlib/Cirq)
	- `tfq` [TensorFlow Quantum](https://www.tensorflow.org/quantum)
	- `qsharp` [QSharp](https://docs.microsoft.com/en-us/quantum/language/index?view=qsharp-preview)
	- `quest` [QuEST](https://quest.qtechtheory.org/)
	- `js` [quantum-circuit](https://www.npmjs.com/package/quantum-circuit) (javascript)
	- `quantum-circuit` [quantum-circuit](https://www.npmjs.com/package/quantum-circuit) (json)
	- `toaster` [Qubit Toaster](https://quantastica.com/toaster/)
	- `svg` [SVG (standalone)](https://www.w3.org/Graphics/SVG/)
	- `svg-inline` [SVG (inline)](https://www.w3.org/Graphics/SVG/)



**Example 1** - convert QASM 2.0 program to QUIL:

```python
from quantastica.qps_api import QPS

input_program = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

output_program = QPS.converter.convert(input_program, "qasm", "quil")

print(output_program)

```

Output:

```
DECLARE ro BIT[2]
H 0
CNOT 0 1
MEASURE 0 ro[0]
MEASURE 1 ro[1]
```


**Example 2** - convert QASM 2.0 program to circuit drawing (vector image):

```python
from quantastica.qps_api import QPS

input_program = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

output_svg = QPS.converter.convert(input_program, "qasm", "svg")

# Do something with returned vector image...
open("output.svg", "w").write(output_svg)

```


## Utils API

**QPS.utils.random_circuit(num_qubits=5, output_format="quantum-circuit", options=None)**

Returns random quantum circuit.

- `num_qubits` Integer. Number of qubits. Default: `5`.

- `format` String. Output format. The same as `QPS.converter.convert()` function's `dest` argument. Example: `"qasm"`. Default: `"quantum-circuit"`.

- `options` Dict. Optional. Can contain following keys:

	- `instruction_set` List of gates to use. Example: `["u3", "cx"]`. Default: `[ "u3", "rx", "ry", "rz", "cx", "cz" ]`.
	- `num_gates` Integer. Number of gates in the circuit. Default is `num_qubits * 8`.
	- `mid_circuit_measurement` Bool. Default: `False`.
	- `mid_circuit_reset` Bool. Default: `False`.
	- `classic_control` Bool. Default: `False`.

