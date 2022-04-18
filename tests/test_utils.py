##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##

from typing import List


def _find_line(qir: List[str], prefix: str, err: str) -> str:
    for line in qir:
        l = line.strip()
        if l.startswith(prefix):
            return l
    assert err


def _qubit_string(qubit: int) -> str:
    if qubit == 0:
        return "%Qubit* null"
    else:
        return f"%Qubit* inttoptr (i64 {qubit} to %Qubit*)"


def _result_string(res: int) -> str:
    if res == 0:
        return "%Result* null"
    else:
        return f"%Result* inttoptr (i64 {res} to %Result*)"


def single_op_call_string(name: str, qb: int) -> str:
    return f"call void @__quantum__qis__{name}__body({_qubit_string(qb)})"


def adj_op_call_string(name: str, qb: int) -> str:
    return f"call void @__quantum__qis__{name}__adj({_qubit_string(qb)})"


def double_op_call_string(name: str, qb1: int, qb2: int) -> str:
    return f"call void @__quantum__qis__{name}__body({_qubit_string(qb1)}, {_qubit_string(qb2)})"


def rotation_call_string(name: str, theta: float, qb: int) -> str:
    return f"call void @__quantum__qis__{name}__body(double {theta:#e}, {_qubit_string(qb)})"


def measure_call_string(name: str, res: str, qb: int) -> str:
    return f"call void @__quantum__qis__{name}__body({_qubit_string(qb)}, {_result_string(res)})"


def return_string() -> str:
    return "ret void"


def array_start_record_output_string() -> str:
    return f"call void @__quantum__rt__array_start_record_output()"


def array_end_record_output_string() -> str:
    return f"call void @__quantum__rt__array_end_record_output()"


def result_record_output_string(res: str) -> str:
    return f"call void @__quantum__rt__result_record_output({_result_string(res)})"


def find_function(qir: List[str]) -> List[str]:
    result = []
    state = 0
    for line in qir:
        l = line.strip()
        if state == 0 and l == "define void @main() #0 {":
            state = 1
        elif state == 1 and l == "entry:":
            state = 2
        elif state == 2 and l == "}":
            return result
        elif state == 2:
            result.append(l)
    assert "No main function found"


def check_attributes(qir: List[str],
                     expected_qubits: int = -1,
                     expected_results: int = -1) -> None:
    attr_string = 'attributes #0 = { "EntryPoint"'
    attr_line = _find_line(qir, attr_string, "Missing entry point attribute")
    chunks = attr_line.split(' ')
    actual_qubits = -1
    actual_results = -1
    for chunk in chunks:
        potential_pair = chunk.split('=')
        if len(potential_pair) == 2:
            (name, value) = potential_pair
            if str(name) == '"requiredQubits"':
                actual_qubits = int(value.strip('"'))
            if str(name) == '"requiredResults"':
                actual_results = int(value.strip('"'))

    assert expected_qubits == actual_qubits, \
        f"Incorrect qubit count: {expected_qubits} expected, {actual_qubits} actual"

    assert expected_results == actual_results, \
        f"Incorrect result count: {expected_results} expected, {actual_results} actual"
