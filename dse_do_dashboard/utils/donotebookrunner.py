from nbformat import read, NO_CONVERT
from io import StringIO
from contextlib import redirect_stdout
import sys
import traceback
from typing import Dict


class InterpreterError(Exception):
    pass


def my_exec(cmd, globals=None, locals=None, description='source string'):
    """Does an `exec()` with exception handling to get the line-number where the exception has occurred in the extracted code (cmd)."""
    try:
        exec(cmd, globals, locals)
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]
    else:
        return
    raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))


class NotebookRunner():
    """Runs the code from a notebook.
    Extracts code from notebook.
    Runs the code. Returns the log (i.e. stdoutput).

    Usage::

        runner = NotebookRunner(notebook_path)
        log = runner.run(globals(), locals())
        print(log)

    """

    def __init__(self, notebook_path: str, exec_globals: Dict = {}, exec_locals: Dict  = {}):
        """Instantiate a NotebookRunner.
        :param (str): file_path of notebook
        :param exec_globals (Dict): set of global variables we want to expose to the exec code. E.g. `{'inputs':inputs}`
        Typically, for a DO model, it should include the inputs dictionary.
        :param exec_locals (Dict): typically nothing/empty dict. Any local variable that gets assigned will become available in self.exec_locals
        """
        self.notebook_path = notebook_path
        self.code = ""
        self.log = ""
        self.exec_globals = exec_globals
        self.exec_locals = exec_locals

    def run(self) -> str:
        """Extracts and runs the notebook.
        Returns the log.
        """
        self.code = self._get_nb_code()
        self.log = self._run_code(self.code)
        return self.log

    def _get_nb_code(self):
        """
        WEIRD: for some crazy unknown reason, typing (lowercase) 'CELLS' causes CPD to fail writing a .py file!
        Anywhere in the file, including comments!
        So below I try to avoid this term, which is why I have to do the:
        * 'cellz'
        * 'lower()' operation on 'CELLS'.
        """
        with open(self.notebook_path) as fp:
            notebook = read(fp, NO_CONVERT)
            cellz = notebook['CELLS'.lower()]
            code_cellz = [c for c in cellz if c['cell_type'] == 'code']
            code = ""
            for cell in code_cellz:
                cell_source = cell['source']
                if self.include_code_cell(cell_source):
                    code += cell_source + "\n"
        return code

    def include_code_cell(self, cell_source):
        """Default implementation always returns True.
        To be overridden for custom cell filtering."""
        return True

    def _run_code(self, code):
        ccode = compile(code, "somefile.py", 'exec')  # Compile the code
        f = StringIO()  # For grabbing the log
        with redirect_stdout(f):
            # exec(ccode)
            my_exec(ccode, self.exec_globals, self.exec_locals)  # Execute the compiled Python code
        s = f.getvalue()  # get the log
        return s


class DoNotebookRunner(NotebookRunner):
    """Runs the code extracted from a 'DO solver' notebook designed to work with a DO Experiment.
    Ignores any code cell starting with `#dd-ignore`.
    A DoNotebookRunner assumes an input dictionary is passed-in as the only 'globals'.
    And all outputs are added to the dictionary 'outputs'.
    An empty `outputs` dictionary is part of the globals, so the code can either add output DataFrames to the existing outputs,
    or re-create a new outputs dictionary.

    For now, add globals() and locals() in constructor, otherwise there are issues with importing certain packages.
    The `inputs` and an empty `outputs` will be added in each run.

    Usage::

        runner = DoNotebookRunner(notebook_path, globals(), locals())
        outputs = runner.run(inputs)

    """

    #     def __init__(self, notebook_path):
    #         super().__init__(notebook_path)

    def run(self, inputs: Dict = {}) -> Dict:
        """Runs the notebook.
        Passes-in the inputs as part of the exec_globals.
        And adds an empty `outputs` to the globals, so that the notebook can add output DataFrames, e.g. `outputs["a"] = xxx`.
        Notebook is also allowed to re-create the outputs Dict, e.g. `outputs = {"a": xxx}`
        """
        self.exec_globals['inputs'] = inputs
        self.exec_globals['outputs'] = {}
        super().run()
        return self._get_outputs()

    def include_code_cell(self, cell_source):
        return not cell_source.startswith("#dd-ignore")

    def _get_outputs(self):
        """Get the outputs dictionary.
        If the code has re-assigned the outputs (i.e. `outputs = xxxxx`), then the outputs will be in the exec_locals.
        An empty outputs has also been passed in the globals, so the code could also just have added key-value pairs, e.g. `outputs["a"] = xxxx`.
        Then the outputs will be available in the exec_globals.
        """
        if 'outputs' in self.exec_locals:
            outputs = self.exec_locals['outputs']
        elif 'outputs' in self.exec_globals:
            outputs = self.exec_globals['outputs']
        else:
            outputs = {}
        return outputs