from .constant import *
import subprocess, threading, psutil, os


class CodeRunner:
    class Result:
        def __init__(
            self,
            timeOut: bool,
            memoryOut: bool,
            returnCode: int | None,
            stdout: bytes | None,
            stderr: bytes | None,
        ) -> None:
            self.timeOut = timeOut
            self.memoryOut = memoryOut
            self.returnCode = returnCode
            self.stdout = stdout
            self.stderr = stderr

    def __init__(self):
        self.memoryOut = False

    def memoryMonitor(self, pid: int, memoryLimit: int) -> None:
        try:
            psutilProcess = psutil.Process(pid)
        except psutil.NoSuchProcess:
            # 跑的太他妈快了，没测到
            return
        while True:
            try:
                # 测出来是资源监视器内存中提交那栏 *1024
                if psutilProcess.memory_info().vms > memoryLimit:
                    self.memoryOut = True
                    psutilProcess.kill()
                    return
            except psutil.NoSuchProcess:
                return

    def run(
        self,
        *popenargs,
        inputContent: bytes | None = None,
        timeLimit: int | None = None,
        memoryLimit: int | None = None,
        **kwargs,
    ) -> Result:
        timeOut = False
        returnCode = 0
        stdout = None
        stderr = None
        with subprocess.Popen(*popenargs, **kwargs) as process:
            if memoryLimit is not None:
                monitor = threading.Thread(
                    target=self.memoryMonitor,
                    args=(
                        process.pid,
                        memoryLimit,
                    ),
                )
                monitor.start()
            try:
                stdout, stderr = process.communicate(inputContent, timeout=timeLimit)
            except subprocess.TimeoutExpired:
                process.kill()
                if mswindows():
                    stdout, stderr = process.communicate()
                else:
                    process.wait()
                timeOut = True
            returnCode = process.poll()
        return self.Result(timeOut, self.memoryOut, returnCode, stdout, stderr)


def checkDirectoryExists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def getTempInputFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "input")


def getTempAnswerFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "answer")


def getHackDataStorageFolderPath(clientID: str) -> str:
    return os.path.join(HACK_DATA_STORAGE_FOLDER_PATH, clientID)


def getHackDataFolderPath(dataID: int) -> str:
    return os.path.join(CURRENT_HACK_DATA_FOLDER_PATH, str(dataID))


def getInputFilePath(dataID: int) -> str:
    return os.path.join(getHackDataFolderPath(dataID), "input")


def getAnswerFilePath(dataID: int) -> str:
    return os.path.join(getHackDataFolderPath(dataID), "answer")


def getOutputFilePath(dataID: int) -> str:
    return os.path.join(getHackDataFolderPath(dataID), "output")


def mswindows() -> bool:
    try:
        import msvcrt
    except ModuleNotFoundError:
        return False
    else:
        return True
