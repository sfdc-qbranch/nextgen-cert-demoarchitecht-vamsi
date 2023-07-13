import os
import shutil
from abc import ABC
import sys
from time import sleep

from cumulusci.core.tasks import BaseTask

from qbrix.tools.bundled.sam.main import migrate
from qbrix.tools.shared.qbrix_project_tasks import (
    assign_prefix_to_files,
    compare_metadata,
    create_external_id_field,
    create_permission_set_file,
    delete_standard_fields,
    generate_stack_view,
    push_changes,
    update_file_api_versions,
)


class MassFileOps(BaseTask, ABC):
    """Q Brix Mass Operations Utility has a number of helpful methods to save time when developing projects which store Salesforce metadata."""

    task_docs = """
    Q Brix Mass Operations Utility has a number of helpful methods to save time when developing projects which store Salesforce metadata.
    """

    def _show_menu(self):
        """Display Menu"""

        os.system("clear")
        self.logger.info(
            """\nQ BRIX - MASS OPERATIONS UTILITIES\n\n
            OPTION  DESCRIPTION\n
            [1]     Update File APIs : Updates Apex Classes and LWC/Aura Components with Q Brix API Version\n
            [2]     Delete Standard Fields : Removes standard fields within object folders\n
            [3]     Prefix Generator : Assign Prefix to all Custom Entities (Folders and References) in Project\n
            [4]     External ID Field Generator : Generate External ID Fields for a list of Object names\n
            [5]     Push Upgrade Tool (BETA) : Compare changes in metadata between the target org and your project, then push changes to the org.\n
            [6]     Permission Set Generator : Generate Permission Set for Objects, Fields, Tabs and Classes in your project.\n
            [7]     Q Brix Stack Viewer (BETA): Generates a view of the metadata deployed by the whole stack of Q Brix.\n
            [8]     SAM CRM Analytics Migration Tool (v0.4.1 - BETA): Can be used to migrate CRMA Assets from one Salesforce Org to Another\n
            [r]     Reset Menu 
            [e]     Exit   
            """
        )

        # Process Menu Selection
        return input("\n\nWhich task you like to run? (Enter the option number) : ")

    def _run_api_update_utility(self):
        """Run Update File APIs Utility"""
        self.logger.info(
            "\n\nRunning Update File APIs Utility\nWARNING: This will update ALL Apex Classes, Aura Component's and LWC Component's metadata files with the project API Version."
        )
        update_file_api_versions(self.project_config.project__package__api_version)
        self.logger.info("Update Complete. Please Check Your Code Deploys!")

    def _run_remove_standard_fields_utility(self):
        """Run Core Field Removal Utility"""
        self.logger.info(
            "\n\nRunning Core Field Removal Utility\nWARNING: This will DELETE all Standard/Core Salesforce fields from all object folders within force-app/main/default/objects."
        )
        delete_standard_fields()
        self.logger.info("Removal Complete. Please Check Your Code Deploys!")

    def _run_mass_prefixing_utility(self):
        """Run Mass Rename Utility"""
        self.logger.info(
            "\n\nRunning Mass Rename Utility\nWARNING: This tool is still new so please review all changes which is makes.\nWARNING: The following Prefixes are Ignored - sdo_, xdo_, db_\nThe following directories are ignored within force-app/main/default: settings,quickActions,layouts,corswhitelistorigins,roles and standardValueSets"
        )
        set_interactive_mode = False
        prefix = input(
            "What prefix do you want to assign to custom files and folders? (e.g. FINS) : "
        )
        interactive_mode = (
            input("Do you want to be prompted about any potential changes? (Y/n) : ")
            or "y"
        )
        if interactive_mode and interactive_mode.lower() == "y":
            set_interactive_mode = True
        if not prefix:
            self.logger.info("No Prefix Provided")
            sleep(2)
            self._run_task()
        assign_prefix_to_files(
            prefix=prefix.upper(), interactive_mode=set_interactive_mode
        )

    def _run_external_id_field_generator(self):
        """Run External ID Field Generator Utility"""
        self.logger.info("\n\nRunning External ID Field Generator Utility")
        mode = input(
            "Do you want to generate fields from current objects (p) in the Q Brix or a list within a file (f)? (p/f)"
        )
        if mode.lower() == "project":
            create_external_id_field()
        else:
            file_input = input(
                "\n\nPlease provide the relevant path to the txt file within the project, which holds the names of the objects. (There should be one object api name per line.) : "
            )
            if file_input and os.path.exists(file_input):
                create_external_id_field(file_input)
            else:
                self.logger.info("File Path does not exist. Skipping.")
                sleep(2)
                self._run_task()

    def _run_push_upgrade_utility(self):
        """Run Upgrade Utility"""
        self.logger.info(
            "TOOL HAS NOT BEEN FULLY TESTED YET. PLEASE DO NOT USE. TESTING ONLY."
        )
        target_org_alias = input("Please enter the alias of the connected org: ")
        metadata_diff = compare_metadata(target_org_alias)
        if metadata_diff:
            print("Differences found:")
            print(metadata_diff)
            if input("\nWould you like to push these changes? (y/n) ").lower() == "y":
                push_result = push_changes(target_org_alias)
                print("Push result:")
                print(push_result)
        else:
            print("No differences found")

        if os.path.exists("src"):
            shutil.rmtree("src")

        if os.path.exists("mdapipkg"):
            shutil.rmtree("mdapipkg")

        if os.path.exists("upgrade_src"):
            shutil.rmtree("upgrade_src")

    def _run_permission_set_generator(self):
        """Run Permission Set Generator"""
        self.logger.info("\n\nRunning Permission Set Generator")

        perm_set_name = input(
            "\nWhat name would you like to give to the permission set? "
        )

        perm_set_location = input(
            "\nWhere shall the Permission Set File be stored? (If no path is provided the default will be used) "
        )

        perm_set_upsert = (
            input(
                "\nIf there is an existing file with the same name, do you want to upsert entries? Y/n (Default = y) "
            )
            or "y"
        )

        if perm_set_name:
            if not perm_set_location:
                perm_set_location = os.path.join(
                    "force-app", "main", "default", "permissionsets"
                )

            if perm_set_upsert.lower() == "y":
                upsert_mode = True
            else:
                upsert_mode = False

            perm_set_name = perm_set_name.replace(" ", "_")

            self.logger.info(
                " -> Generating Permission Set File in %s with file name %s.permissionset-meta.xml",
                perm_set_location,
                perm_set_name,
            )
            create_permission_set_file(
                perm_set_name.replace(" ", "_"),
                perm_set_name,
                perm_set_location,
                upsert_mode,
            )
            self.logger.info(" -> Permission Set Generated!")

    def _run_stack_viewer(self):
        """Run Stack Viewer"""
        output_method = (
            input(
                "\n Would you like to output to terminal or to a text file? (terminal/file) : "
            )
            or "file"
        )

        if output_method and (
            output_method.lower() == "terminal" or output_method.lower() == "file"
        ):
            generate_stack_view(output=output_method.lower())
        else:
            self.logger.info("Invalid Output Method. Skipping")
            sleep(2)
            self._run_task()

    def _run_task(self):
        option = self._show_menu()

        if option.lower() == "1":
            self._run_api_update_utility()

        elif option.lower() == "2":
            self._run_remove_standard_fields_utility()

        elif option.lower() == "3":
            self._run_mass_prefixing_utility()

        elif option.lower() == "4":
            self._run_external_id_field_generator()

        elif option.lower() == "5":
            self._run_push_upgrade_utility()

        elif option.lower() == "6":
            self._run_permission_set_generator()

        elif option.lower() == "7":
            self._run_stack_viewer()

        elif option.lower() == "8":
            migrate()

        elif option.lower() == "e":
            self.logger.info("Exiting Q Brix Mass Operations Utility")
            sys.exit()

        elif option == "r":
            option = self._show_menu()

        else:
            self.logger.info(
                "Invalid Menu Option Entered. Please choose a valid option from the list above."
            )
            self._run_task()
