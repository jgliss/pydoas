from traceback import format_exc
import importlib.util
import pathlib
import sys


def get_all_script_paths(script_dir: pathlib.Path, pattern: str, exclude: list[str]) -> list[pathlib.Path]:
    """
    Get all script paths in a directory matching a pattern, excluding specified files.
    
    Parameters
    ----------
    script_dir : pathlib.Path
        The directory to search for scripts.
    pattern : str
        The glob pattern to match script files.
    exclude : list of str
        List of filenames to exclude from the results.
    
    Returns
    -------
    list of pathlib.Path
        List of paths to the scripts that match the pattern and are not excluded.
    """
    
    return [x for x in script_dir.glob(pattern) if not x.name in exclude]

def run_all_scripts(all_intro_scripts: list[pathlib.Path]) -> tuple[list[str], list[str], list[str]]:
    """
    Executes a list of introductory scripts and categorizes their outcomes.

    Parameters
    ----------
    all_intro_scripts : list of pathlib.Path
        A list of paths to the introductory scripts to be executed.

    Returns
    -------
    test_err_messages : list of str
        Messages indicating which scripts failed due to assertion errors and their tracebacks.
    passed_messages : list of str
        Messages indicating which scripts passed all tests.
    crashed_messages : list of str
        Messages indicating which scripts encountered unexpected errors.
    """

    test_err_messages: list[str] = []
    passed_messages: list[str] = []
    crashed_messages: list[str] = []
    for script_path in all_intro_scripts:
        try:
            print(f"Running {script_path.name}")
            run_script(script_path=script_path)
            passed_messages.append(f"All tests passed in script: {script_path.name}")
        except AssertionError as e:
            msg = (f"\n\n"
                f"--------------------------------------------------------\n"
                f"Tests in script {script_path.name} failed.\n"
                f"Error traceback:\n {format_exc(e)}\n"
                f"--------------------------------------------------------"
                f"\n\n"
                )
            test_err_messages.append(msg)
        except Exception as e:
            crashed_messages.append(f"Unexpected error in {script_path.name}: {e}")
    return test_err_messages,passed_messages,crashed_messages

def print_output_runall(options, test_err_messages, passed_messages, crashed_messages):
    """
    Print the results of running all tests and scripts.

    This function prints the results of tests and script executions, including
    test failures, test successes, and crashed messages. The test results are
    printed only if the test mode is active.
    
    Parameters
    ----------
    options : object
        An object containing various options, including the test mode flag.
    test_err_messages : list of str
        A list of error messages from failed tests.
    passed_messages : list of str
        A list of messages from passed tests.
    crashed_messages : list of str
        A list of messages from crashed scripts.
    
    Returns
    -------
    None
    """

    # If applicable, do some tests. This is done only if TESTMODE is active:
    # testmode can be activated globally (see SETTINGS.py) or can also be
    # activated from the command line when executing the script using the
    # option --test 1
    if int(options.test):
        print("\n----------------------------\n"
            "T E S T  F A I L U R E S"
            "\n----------------------------\n")
        if test_err_messages:
            for msg in test_err_messages:
                print(msg)
        else:
            print("None")
        print("\n----------------------------\n"
            "T E S T  S U C C E S S"
            "\n----------------------------\n")
        if passed_messages:
            for msg in passed_messages:
                print(msg)
        else:
            print("None")

    print("\n----------------------------\n"
        "C R A S H E D"
        "\n----------------------------\n")
    if crashed_messages:
        for msg in crashed_messages:
            print(msg)
    else:
        print("None")

def run_script(script_path: pathlib.Path):
    module_name = script_path.stem  # Use filename as module name

    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # Add module to sys.modules
    spec.loader.exec_module(module)  # Execute module
    if hasattr(module, "main"):
        module.main()
    else:
        raise ValueError(f"Please move content of __main__ to main() in {script_path.name}")
    
IGNORE_SCRIPTS = []
SCRIPT_PATTERN = "ex[0-9]*.py"

if __name__ == "__main__":
    from SETTINGS import ARGPARSER, SCRIPTS_DIR
    from time import time

    options = ARGPARSER.parse_args()

    t0 = time()
    all_example_scripts = get_all_script_paths(SCRIPTS_DIR, SCRIPT_PATTERN, IGNORE_SCRIPTS)
    test_err_messages, passed_messages, crashed_messages = run_all_scripts(all_example_scripts)
    t1 = time()    
    print_output_runall(options, test_err_messages, passed_messages, crashed_messages)
    print(f"Total runtime: {t1 - t0:.2f} s")