"""
BigData Exam Simulator - Code Runner
사용자가 작성한 파이썬 코드를 실행하고 표준 출력, 에러, 생성 파일 및 반환값을 안전하게 캡처합니다.
"""

import sys
import io
import os
import traceback
import contextlib
import multiprocessing
import pandas as pd
import numpy as np


class ExecutionResult:
    def __init__(self, stdout: str = "", stderr: str = "", success: bool = True, exception: str = None, last_output: str = None):
        self.stdout = stdout
        self.stderr = stderr
        self.success = success
        self.exception = exception
        self.last_output = last_output

    def to_dict(self):
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "success": self.success,
            "exception": self.exception,
            "last_output": self.last_output
        }


def run_user_code(code_str: str, working_dir: str = None, timeout_seconds: int = 20) -> ExecutionResult:
    """
    사용자가 작성한 코드를 실행하고 stdout과 발생 예외를 캡처합니다.
    """
    if working_dir is None:
        working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    old_cwd = os.getcwd()
    try:
        os.chdir(working_dir)
    except Exception:
        pass

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    # Pre-populate global context with standard data analysis libraries
    exec_globals = {
        "__name__": "__main__",
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
    }

    success = True
    exc_message = None
    last_line = ""

    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            exec(code_str, exec_globals)
        stdout_val = stdout_capture.getvalue()
        stderr_val = stderr_capture.getvalue()
        
        # Extract last non-empty line of stdout
        lines = [line.strip() for line in stdout_val.splitlines() if line.strip()]
        if lines:
            last_line = lines[-1]
            
    except Exception as e:
        success = False
        exc_message = traceback.format_exc()
        stdout_val = stdout_capture.getvalue()
        stderr_val = stderr_capture.getvalue()
        if not stderr_val:
            stderr_val = exc_message
    finally:
        try:
            os.chdir(old_cwd)
        except Exception:
            pass

    return ExecutionResult(
        stdout=stdout_val,
        stderr=stderr_val,
        success=success,
        exception=exc_message,
        last_output=last_line
    )
