import filecmp
import os
import shutil
import stat
from pathlib import Path
from abc import ABC
from os.path import exists

from cumulusci.core.tasks import BaseTask

from qbrix.tools.shared.qbrix_cci_tasks import run_cci_task
from qbrix.tools.shared.qbrix_project_tasks import (download_and_unzip,
                                                    replace_file_text)


class QBrixUpdater(BaseTask, ABC):

    """Updates Q Brix Scripts along with any optional, custom updates"""

    q_branch_location = "https://qbrix-core.herokuapp.com/qbrix/q_update_package.zip"

    task_docs = """
    Updated the Q brix Extension Library and other Q Brix related bundles like GitHub Actions and VSCode Extensions in line with the XDO-Template (main branch). 

    Can also be used to update custom scripts and other custom directories from a .zip file which needs to be hosted somewhere (by setting the URL of the .zip file as the UpdateLocation option), in addition the .zip files can also have a password set and you can specify the password using the ArchivePassword option when running the task.
    """

    task_options = {
        "UpdateLocation": {
            "description": "String URL for the location where the update package .zip file is located",
            "required": False
        },
        "ArchivePassword": {
            "description": "String password for the .zip file",
            "required": False
        },
        "IgnoreOptionalUpdates": {
            "description": "When set to True, will ignore updates defined as 'Optional' from the Q Branch Updates. Default is False.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(QBrixUpdater, self)._init_options(kwargs)
        self.ArchivePassword = self.options["ArchivePassword"] if "ArchivePassword" in self.options else None
        self.UpdateLocation = self.options["UpdateLocation"] if "UpdateLocation" in self.options else None
        self.IgnoreOptionalUpdates = self.options["IgnoreOptionalUpdates"] if "IgnoreOptionalUpdates" in self.options else False

    def _check_and_deploy_class(self, tasks: dict):

        with open("cumulusci.yml", "r", encoding="utf-8") as cci_file:
            cci_file.seek(0)
            cci_data = cci_file.read()

        # Check for Placeholder
        if cci_data.find("# CUSTOM TASKS ADDED FOR Q BRIX DEVELOPMENT") == -1:
            self.logger.error("Unable to update cumulusci.yml file. Missing placeholder for Q Brix Tasks.")
        else:
            # Check and update custom tasks
            for key, value in tasks.items():
                self.logger.info(" -> Checking Q Brix Task: %s / %s", key, value)

                key_index = cci_data.find(f"{key}:")
                value_index = cci_data.find(value)

                if key_index < 0 and value_index < 0:
                    replacement_text = f"# CUSTOM TASKS ADDED FOR Q BRIX DEVELOPMENT\n\n  {key}:\n    class_path: {value}"
                    replace_file_text("cumulusci.yml", "# CUSTOM TASKS ADDED FOR Q BRIX DEVELOPMENT", replacement_text)

    def _update_folder(self, folder_path, update_dir, remove_existing):

        """Copies Files and Directories from the downloaded update to the corresponding location within the project"""

        if exists(folder_path) and remove_existing:
                shutil.rmtree(folder_path)
        update_path = os.path.join(update_dir, folder_path)
        shutil.copytree(src=update_path, dst=folder_path, dirs_exist_ok=True)
        
    def _update_folder_indirect_source(self, folder_path, update_dir, remove_existing):

        """Copies content from an different source root to target"""
        

        if exists(folder_path) and remove_existing:
                shutil.rmtree(folder_path)
                
        shutil.copytree(src=update_dir, dst=folder_path, dirs_exist_ok=True)

    def _ensure_required_dirs(self):

        """Ensures that required directories are created"""

        os.makedirs(".qbrix", exist_ok=True)
        os.makedirs("qbrix", exist_ok=True)


    def _run_task(self):

        """" Updates the Q brix Project with the latest files from xDO-Template main branch """

        self.logger.info("Starting Q Brix Update")

        self._ensure_required_dirs()

        if os.path.exists("qbrix/tools/utils/qbrix_update.py"):
            shutil.copyfile("qbrix/tools/utils/qbrix_update.py", ".qbrix/qbrix_update.py")

        self.logger.info(" -> Downloading Latest version...")
        if download_and_unzip(self.q_branch_location, self.ArchivePassword, False, True):
            # ADD FOLDERS HERE WHICH YOU WANT TO UPDATE IN PROJECT DIRECTORIES
            # PARAM1 = The folder as if it was from the root path
            # PARAM2 = The location where the source files should be located
            # PARAM3 = If True, it will delete the whole directory in project before updating
            self._update_folder("qbrix", ".qbrix/Update/xDO-Template-main", False)
            self._update_folder(".vscode", ".qbrix/Update/xDO-Template-main", False)
            self._update_folder(".github", ".qbrix/Update/xDO-Template-main", False)
            self._update_folder_indirect_source(".git/hooks", ".qbrix/Update/xDO-Template-main/qbrix/git/hooks", False)
            
            #we are injecting pre-commit to use our cci extension but we need to make executeable
            f = Path(".git/hooks/pre-commit")
            f.chmod(f.stat().st_mode | stat.S_IEXEC)
            
            

            # Finally Clean Up Cached Folder
            self.logger.info(" -> Cleaning up temp files...")
            shutil.rmtree(".qbrix/Update")

        self.logger.info(" -> Checking cumulusci.yml file...")
        
        # ADD CUSTOM TASKS HERE
        # PARAM1 = The name of the task
        # PARAM2 = The class path of the task

        tasks_to_update = {}
        tasks_to_update.update({'qbrix_preflight': 'qbrix.tools.utils.qbrix_preflight.RunPreflight'})
        tasks_to_update.update({'qbrix_landing': 'qbrix.tools.utils.qbrix_landing.RunLanding'})
        tasks_to_update.update({'analytics_manager': 'qbrix.tools.data.qbrix_analytics.AnalyticsManager'})
        tasks_to_update.update({'user_manager': 'qbrix.salesforce.qbrix_salesforce_tasks.CreateUser'})
        tasks_to_update.update({'qbrix_installer_tracking': 'qbrix.tools.utils.qbrix_installtracking.InstallRecorder'})
        tasks_to_update.update({'qbrix_metadata_checker': 'qbrix.tools.utils.qbrix_metadata_checker.MetadataChecker'})
        tasks_to_update.update({'dustpan': 'qbrix.tools.utils.qbrix_orgconfig_hydrate.NGBroom'})
        tasks_to_update.update({'flow_wrapper': 'qbrix.tools.utils.qbrix_deploy.Deploy'})
        tasks_to_update.update({'qbrix_sfdx': 'cumulusci.tasks.sfdx.SFDXOrgTask'})
        tasks_to_update.update({'deploy_dx': 'cumulusci.tasks.sfdx.SFDXOrgTask'})
        tasks_to_update.update({'qbrix_cache_add': 'qbrix.tools.utils.qbrix_orgconfig_hydrate.NGCacheAdd'})
        tasks_to_update.update({'abort_install': 'qbrix.tools.utils.qbrix_orgconfig_hydrate.NGAbort'})
        tasks_to_update.update({'qbrix_shell_deploy_metadeploy': 'qbrix.tools.utils.qbrix_deploy.Deploy'})
        tasks_to_update.update({'health_check': 'qbrix.tools.utils.qbrix_health_check.HealthChecker'})
        tasks_to_update.update({'update_qbrix': 'qbrix.tools.utils.qbrix_update.QBrixUpdater'})
        tasks_to_update.update({'setup_qbrix': 'qbrix.tools.utils.qbrix_project_setup.InitProject'})
        tasks_to_update.update({'list_qbrix': 'qbrix.salesforce.qbrix_salesforce_tasks.ListQBrix'})
        tasks_to_update.update({'q_update_dependencies': 'qbrix.salesforce.qbrix_salesforce_tasks.QUpdateDependencies'})
        tasks_to_update.update({'mass_qbrix_update': 'qbrix.tools.utils.qbrix_mass_ops.MassFileOps'})
        tasks_to_update.update({'precommit_check': 'qbrix.git.hooks_ext.pre_commit.PreCommit'})

        self._check_and_deploy_class(tasks_to_update)

        self.logger.info(" -> Checking for additional tasks to run...")

        if not filecmp.cmp(".qbrix/qbrix_update.py", "qbrix/tools/utils/qbrix_update.py"):
            self.logger.info(" -> Update Task has been upgraded, running update again...")
            run_cci_task("update_qbrix", self.org_config.name)

        if os.path.exists("qbrix/qbrix_update.py"):
            os.remove("qbrix/qbrix_update.py")

        if self.UpdateLocation:
            self.logger.info(" -> Running custom update from %s...", self.UpdateLocation)
            download_and_unzip(
                self.UpdateLocation,
                self.ArchivePassword,
                self.IgnoreOptionalUpdates)
            self.logger.info(" -> Custom update complete")

        # Fixes for CumulusCI.yml
        self.logger.info(" -> Updating robot references in CumulusCI.yml...")
        replace_file_text("cumulusci.yml", "qbrix/robot/tests", "qbrix/robot", False)
        if os.path.exists("qbrix/robot/tests"):
            shutil.rmtree("qbrix/robot/tests")
        self.logger.info("Update Complete!")
