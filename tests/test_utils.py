##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##

from typing import List
from pyqir import is_entry_point, Module, Function

def _qubit_string(qubit: int, static_alloc=True) -> str:
    if static_alloc == False:
        return f"%Qubit* %qubit{qubit}"

    if qubit == 0:
        return "%Qubit* null"
    else:
        return f"%Qubit* inttoptr (i64 {qubit} to %Qubit*)"


def _result_string(res: int, static_alloc=True) -> str:
    if static_alloc == False:
        return f"%Result* %result{res}"

    if res == 0:
        return "%Result* null"
    else:
        return f"%Result* inttoptr (i64 {res} to %Result*)"


def single_op_call_string(name: str, qb: int, static_alloc=True) -> str:
    return f"call void @__quantum__qis__{name}__body({_qubit_string(qb, static_alloc)})"


def adj_op_call_string(name: str, qb: int, static_alloc=True) -> str:
    return f"call void @__quantum__qis__{name}__adj({_qubit_string(qb, static_alloc)})"


def double_op_call_string(name: str, qb1: int, qb2: int, static_alloc=True) -> str:
    return f"call void @__quantum__qis__{name}__body({_qubit_string(qb1, static_alloc)}, {_qubit_string(qb2, static_alloc)})"


def rotation_call_string(name: str, theta: float, qb: int, static_alloc=True) -> str:
    return f"call void @__quantum__qis__{name}__body(double {theta:#e}, {_qubit_string(qb, static_alloc)})"


def measure_call_string(
    name: str, res: str, qb: int, static_qubit_alloc=True, static_result_alloc=True
) -> str:
    if static_result_alloc:
        return f"call void @__quantum__qis__{name}__body({_qubit_string(qb, static_qubit_alloc)}, {_result_string(res, static_result_alloc)})"
    else:
        return f"%result{res} = call %Result* @__quantum__qis__{name}__body({_qubit_string(qb, static_qubit_alloc)})"


def equal(var: str, res: str):
    return f"%{var} = call i1 @__quantum__qis__read_result__body({_result_string(res)})"


def generic_op_call_string(name: str, qbs: List[int], static_alloc=True) -> str:
    args = ", ".join(_qubit_string(qb, static_alloc) for qb in qbs)
    return f"call void @__quantum__qis__{name}__body({args})"


def return_string() -> str:
    return "ret void"


def array_start_record_output_string() -> str:
    return f"call void @__quantum__rt__array_start_record_output()"


def array_end_record_output_string() -> str:
    return f"call void @__quantum__rt__array_end_record_output()"


def result_record_output_string(res: str, static_alloc=True) -> str:
    return f"call void @__quantum__rt__result_record_output({_result_string(res, static_alloc)})"


def find_function_old(qir: List[str], name = "main") -> List[str]:
    result = []
    state = 0
    for line in qir:
        l = line.strip()
        if state == 0 and l == f"define void @{name}() #0 {{":
            state = 1
        elif state == 1 and l == "entry:":
            state = 2
        elif state == 2 and l == "}":
            return result
        elif state == 2:
            result.append(l)
    assert "No main function found"

def find_function(qir: List[str]) -> List[str]:
    x = "\n".join(qir)
    mod = Module.from_ir(x)
    func = next(filter(is_entry_point, mod.functions))
    assert func is not None, "No main function found"
    body = []
    for block in func.basic_blocks:
        for inst in block.instructions:
            body.append(str(inst).strip())

    return body


def get_entry_point(mod: Module) -> Function:
    func = next(filter(is_entry_point, mod.functions))
    assert func is not None, "No main function found"
    return func

def check_attributes(
    qir: List[str], expected_qubits: int = -1, expected_results: int = -1
) -> None:
    x = "\n".join(qir)
    mod = Module.from_ir(x)
    func = next(filter(is_entry_point, mod.functions))

    actual_qubits = -1
    actual_results = -1
    actual_qubits_attr = func.attribute("requiredQubits")
    if actual_qubits_attr is not None:
        actual_qubits = int(actual_qubits_attr.value)
    actual_results_attr = func.attribute("requiredResults")
    if actual_results_attr is not None:
        actual_results = int(actual_results_attr.value)
    assert (
        expected_qubits == actual_qubits
    ), f"Incorrect qubit count: {expected_qubits} expected, {actual_qubits} actual"

    assert (
        expected_results == actual_results
    ), f"Incorrect result count: {expected_results} expected, {actual_results} actual"
