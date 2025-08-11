from qsg.detect import detect_language_and_provider


def test_detect_qiskit(tmp_path):
    src = tmp_path / 'test.py'
    src.write_text('from qiskit import QuantumCircuit')
    lang, provider = detect_language_and_provider(str(src))
    assert (lang, provider) == ('python', 'ibm')


def test_detect_cirq(tmp_path):
    src = tmp_path / 'test.py'
    src.write_text('import cirq')
    lang, provider = detect_language_and_provider(str(src))
    assert (lang, provider) == ('python', 'google')


def test_detect_qsharp(tmp_path):
    src = tmp_path / 'program.qs'
    src.write_text('operation Foo() : Unit {}')
    lang, provider = detect_language_and_provider(str(src))
    assert (lang, provider) == ('qsharp', 'azure')


def test_detect_unknown(tmp_path):
    src = tmp_path / 'test.py'
    src.write_text('print(42)')
    lang, provider = detect_language_and_provider(str(src))
    assert lang is None and provider is None
