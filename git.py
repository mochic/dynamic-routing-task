import os
import uuid
import subprocess


def get_task_script(output_dir):
    # p = subprocess.Popen([
    #     "git",
    #     "clone",
    #     "https://github.com/mochic/dynamic-routing-task.git",
    #     "&&",
    #     "git",
    #     "checkout",
    #     "production",
    #     output_dir,
    # ], shell=True)
    p = subprocess.Popen([
        "git clone https://github.com/mochic/dynamic-routing-task.git",
        "&&",
        "git checkout production {}".format(output_dir),
    ], shell=True)
    status_code = p.wait()
    
    if status_code != 0:
        raise Exception("Non-zero exit for checkout: %s" % status_code)
    
    task_script_path = os.path.join(output_dir, "taskScript.py")
    if not os.path.exists(task_script_path):
        raise Exception("Task script not found at expected path: %s" % task_script_path)
    
    return task_script_path


if __name__ == "__main__":
    import argparse
    import uuid
    import shutil

    parser = argparse.ArgumentParser()
    parser.add_argument("root_dir", type=str)

    args = parser.parse_args()

    output_dir = os.path.join(args.root_dir, uuid.uuid4().hex)
    path = get_task_script(output_dir)
    print(path)
    shutil.rmtree(path, ignore_errors=False, onerror=None)