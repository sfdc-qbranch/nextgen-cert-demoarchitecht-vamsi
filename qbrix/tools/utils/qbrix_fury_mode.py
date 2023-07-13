import datetime
import multiprocessing
from abc import ABC
import time

from cumulusci.core.tasks import BaseTask

from qbrix.tools.shared.qbrix_cci_tasks import run_cci_flow, run_cci_task

def execute_tasks_and_flows(tasks_and_flows, org_name, **options):

    """
    Runner for Tasks and Flows using multiprocessing
    """

    processes = []
    for item in tasks_and_flows:
        if item[1] == "task":
            process = multiprocessing.Process(target=run_cci_task_wrapper, args=(item[0], org_name,))
        elif item[1] == "flow":
            process = multiprocessing.Process(target=run_cci_flow_wrapper, args=(item[0], org_name, options,))
        else:
            print("Invalid item type:", item)
            continue

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

def run_cci_flow_wrapper(flow_name, org_name, options):
    try:
        print(f"{flow_name} | STARTED")
        run_cci_flow(flow_name, org_name, **options)
    except Exception as e:
        print(f"{flow_name} | ERROR | {e}")
    else:
        print(f"{flow_name} | COMPLETE!")

def run_cci_task_wrapper(task_name, org_name):
    try:
        print(f"{task_name} | STARTED")
        run_cci_task(task_name, org_name)
    except Exception as e:
        print(f"{task_name} | ERROR | {e}")
    else:
        print(f"{task_name} | COMPLETE")



class RunFuryMode(BaseTask, ABC):
    task_docs = """
    Parallel Task, Flow and Script Runner for Q Brix. Use with caution.
    """

    task_options = {
        "org": {
            "description": "Org Alias for the target org",
            "required": False
        },
        "flows": {
            "description": "List of flows to execute. These must already be defined in the flows area.",
            "required": False
        },
        "tasks": {
            "description": "List of Tasks to execute. These must already be defined with options in the tasks area.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(RunFuryMode, self)._init_options(kwargs)
        self.flows = self.options["flows"] if "flows" in self.options else None
        self.tasks = self.options["tasks"] if "tasks" in self.options else None

    def _run_task(self):

        self.logger.info("""                      
        ______  _   _ ______ __   __    ___  ___ _____ ______  _____ 
        |  ___|| | | || ___ \\ \ / /    |  \/  ||  _  ||  _  \|  ___|
        | |_   | | | || |_/ / \ V /     | .  . || | | || | | || |__  
        |  _|  | | | ||    /   \ /      | |\/| || | | || | | ||  __| 
        | |    | |_| || |\ \   | |      | |  | |\ \_/ /| |/ / | |___ 
        \_|     \___/ \_| \_|  \_/      \_|  |_/ \___/ |___/  \____/
        
        """)

        if not self.flows and not self.tasks:
            self.logger.info("Skipping Fury Mode as there are no requests to process.")
            return
        
        process_request_list = []
        flow_count = 0
        task_count = 0

        if self.flows:
            for flow in self.flows:
                process_request_list.append((flow, "flow"))
                flow_count += 1
        if self.tasks:
            for task in self.tasks:
                process_request_list.append((task, "task"))
                task_count += 1

        self.logger.info(f"\nStarting Fury Mode\nRunning {flow_count} flow(s) and {task_count} task(s)\n")
        start_time = time.time()
        execute_tasks_and_flows(tasks_and_flows=process_request_list, org_name=self.org_config.name, options=self.options)
        end_time = time.time()
        execution_time = end_time - start_time
        formatted_time = str(datetime.timedelta(seconds=execution_time))
        self.logger.info(f"\n{task_count + flow_count} requests completed in {formatted_time}\nNormal Mode Restored. Tasks and Flows have completed.")
