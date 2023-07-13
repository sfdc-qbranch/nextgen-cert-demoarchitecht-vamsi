import json
import os
import time
from time import sleep
from Browser import ElementState, SelectAttribute
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask

@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixCMS(QbrixRobotTask):

    """Qbrix CMS Library"""

    def go_to_digital_experiences(self):
        """Go to the Digital Experiences App"""
        self.shared.go_to_app("Digital Experiences")

    def download_all_content(self):

        # Get Workspace Names
        results = self.salesforceapi.soql_query("SELECT Name FROM ManagedContentSpace WHERE IsDeleted=False")
        if results["totalSize"] == 0:
            return

        # Download content from each workspace
        for workspace in results["records"]:
            self.download_cms_content(workspace["Name"])

    def upload_cms_import_file(self, file_path, workspace):

        """
        Uploads the Content from the CMS import .zip file
        @return:
        @param file_path: Relative path to the .zip file containing the export
        @param workspace: Name of the workspace to upload the content to
        """

        self.go_to_digital_experiences()
        sleep(5)

        # Go To Workspace Page
        if workspace:

            # Get the Application ID
            results = self.salesforceapi.soql_query(
                f"SELECT Id FROM ManagedContentSpace where Name = '{workspace}' LIMIT 1")

            if results["totalSize"] == 1:
                app_id = results["records"][0]["Id"]

                # Go to the app
                self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/spaces/{app_id}", timeout='30s')

                # Open Import Menu
                iframe_handler = self.shared.iframe_handler()
                drop_down_menu_selector = f"{iframe_handler} div.slds-page-header__row >> button.slds-button:has-text('Show menu')"
                import_button_selector = f"{iframe_handler} div.slds-page-header__row >> lightning-menu-item.slds-dropdown__item:has-text('Import Content')"

                self.browser.click(drop_down_menu_selector)
                sleep(1)

                # Upload CMS File
                upload_promise = self.browser.promise_to_upload_file(file_path)
                self.browser.click(import_button_selector)
                self.browser.wait_for_all_promises()

                start_time = time.time()
                timeout = 30

                while True:

                    error_message_selector = "div.modal-body >> div.slds-p-around_medium:has-text('Error encountered during import')"
                    confirm_checkbox_selector = "div.modal-body >> span.slds-checkbox >> span.slds-checkbox_faux"
                    import_button_selector = "button.slds-button:has-text('Import')"

                    if self.browser.get_element_count(error_message_selector) > 0:
                        print("Error Occurred During File Upload. CMS Import Failed")
                        return
                    
                    if self.browser.get_element_count(confirm_checkbox_selector) > 0 or self.browser.get_element_count(import_button_selector) > 0:
                        print("File Imported OK!")
                        break

                    # Check if the timeout has been reached
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= timeout:
                        break

                    time.sleep(1)
                    
                self.browser.click("div.modal-body >> span.slds-checkbox >> span.slds-checkbox_faux")
                sleep(1)
                self.browser.click("button.slds-button:has-text('Import')")
                sleep(5)
                self.browser.click("button.slds-button:text('ok')")
                sleep(2)

        else:
            print("Workspace cannot be None. Skipping")
            return

    def download_cms_content(self, workspace):

        """
        Initiate the export of a workspace to a content .zip file (which is emailed to the admin)
        @param workspace: Name of workspace
        @return:
        """

        self.go_to_digital_experiences()
        sleep(5)

        # Go To Workspace Page
        if workspace:

            # Get the Application ID
            results = self.salesforceapi.soql_query(f"SELECT Id FROM ManagedContentSpace where Name = '{workspace}' LIMIT 1")

            if results["totalSize"] == 1:
                app_id = results["records"][0]["Id"]

                # Go to the app
                self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/spaces/{app_id}", timeout='30s')
                iframe_handler = self.shared.iframe_handler()

                # Enhanced workspace handler
                if self.browser.get_element_count(f"{iframe_handler} lightning-badge.slds-badge:has-text('Enhanced'):visible") > 0:
                    return

                # Select all checkboxes
                no_items = False 
                while True:

                    total_cms_elements = self.browser.get_element(f"{iframe_handler} p.slds-page-header__meta-text")

                    if total_cms_elements:

                        innertext_for_total = self.browser.get_property(f"{iframe_handler} p.slds-page-header__meta-text", "innerText")

                        if innertext_for_total == "0 item(s)":
                            no_items = True
                            break

                        if innertext_for_total and "+" not in str(innertext_for_total):
                            break

                        if innertext_for_total and "+" in str(innertext_for_total):
                            elements = self.browser.get_elements(f"{iframe_handler} table.slds-table >> sfdc_cms-content-check-box-button")
                            for elem in elements:
                                self.browser.scroll_to_element(elem)

                    else:
                        break
                
                if no_items:
                    return

                elements = self.browser.get_elements(f"{iframe_handler} table.slds-table >> sfdc_cms-content-check-box-button")
                for elem in elements:
                    self.browser.scroll_to_element(elem)
                    self.browser.click(elem)

                # Open Export Menu

                drop_down_menu_selector = f"{iframe_handler} div.slds-page-header__row >> button.slds-button:has-text('Show menu')"
                import_button_selector = f"{iframe_handler} div.slds-page-header__row >> lightning-menu-item.slds-dropdown__item:has-text('Export Content')"

                self.browser.click(drop_down_menu_selector)
                sleep(1)

                self.browser.click(import_button_selector)
                sleep(2)
                self.browser.click(f"{iframe_handler} button.slds-button:has-text('Export')")
                sleep(5)

    def create_workspace(self, workspace_name, channels=[], enhanced_workspace=True):

        """
        Create a new workspace
        @param workspace_name: Name of the workspace. This must be unique from other workspaces
        @param channels: Optional channels you want to target. Defaults to all available channels
        @param enhanced_workspace: Set to True if you are creating an Enhanced workspace, otherwise set to False. Defaults to True.
        @return:
        """

        # Check for existing workspace
        results = self.salesforceapi.soql_query(f"SELECT Id FROM ManagedContentSpace where Name = '{workspace_name}' LIMIT 1")

        if results["totalSize"] == 1:
            print("Workspace exists already, skipping.")
            return

        # Go to Digital Experience Home and initiate Workspace creation
        self.go_to_digital_experiences()
        sleep(3)
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/home/", timeout='30s')
        sleep(3)
        self.browser.click(f"{self.shared.iframe_handler()} span.label:text-is('Create a CMS Workspace'):visible")

        # Enter initial information
        sleep(2)
        self.browser.click("lightning-input:has-text('Name') >> input.slds-input")
        self.browser.fill_text("lightning-input:has-text('Name') >> input.slds-input", workspace_name)

        # Handle enhanced workspace option
        if enhanced_workspace:
            self.browser.click("span.slds-text-heading_medium:text-is('Enhanced CMS Workspace')")

        # Handle Channel Selection
        self.browser.click("button.nextButton:visible")
        sleep(2)
        if len(channels) > 0:
            for channel in channels:
                if self.browser.get_element_count(f"tr.slds-hint-parent:has-text('{channel}')"):
                    self.browser.click(f"tr.slds-hint-parent:has-text('{channel}') >> div.slds-checkbox_add-button")
        else:
            for checkbox_add_button in self.browser.get_elements("div.slds-checkbox_add-button"):
                self.browser.click(checkbox_add_button)

        # Handle Contributors
        self.browser.click("button.nextButton:visible")
        sleep(2)
        for checkbox_add_button in self.browser.get_elements("div.forceSelectableListViewSelectionColumn"):
            self.browser.click(checkbox_add_button)

        # Handle Contributor Access Levels
        self.browser.click("button.nextButton:visible")
        sleep(2)
        for combo_box in self.browser.get_elements("lightning-picklist:visible"):
            self.browser.click(combo_box)
            sleep(1)
            self.browser.click("span.slds-listbox__option-text:has-text('Content Admin'):visible")

        # Handle Language
        self.browser.click("button.nextButton:visible")
        sleep(2)

        if not enhanced_workspace:
            self.browser.click("button.slds-button:has-text('Move selection to Selected'):visible")
            self.browser.click("lightning-combobox.slds-form-element:has-text('Default Language'):visible")
            self.browser.click("lightning-base-combobox-item:has-text('English (United States)'):visible")

        # Complete Screen
        self.browser.click("button.nextButton:visible")
        sleep(1)
        self.browser.click("button.nextButton:visible")

    def generate_product_media_file(self):

        """
        Generates a Product Media Mapping File, which stores information about Product List Images, Product Detail Images and Attachments related to the products.
        @return: .json file is created within the project and stored at this path: cms_data/product_images.json
        """

        # Get All Active Products which have attached ElectronicMedia
        results = self.salesforceapi.soql_query(f"SELECT Id, External_ID__c, Name from Product2 WHERE Id IN (Select ProductId from ProductMedia)")

        if results["totalSize"] == 0:
            print("No Products found with attached media")
            return

        result_dict = {}
        self.shared.go_to_app("Commerce - Admin")

        for product in results["records"]:

            product_dict = {}

            # Set External ID
            product_dict.update({"External_ID__c": product["External_ID__c"]})

            self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/r/Product2/{product['Id']}/view", timeout='30s')
            sleep(4)

            self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")
            sleep(10)

            # Get Product Detail Images (Max. 8)
            if self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") > 0:
                product_detail_image_list = []
                product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible")
                if product_detail_images:
                    for prod in product_detail_images:
                        prod_property = self.browser.get_property(prod, "alt")
                        if prod_property:
                            print(prod_property)
                            product_detail_image_list.append(prod_property)

                if len(product_detail_image_list) > 0:
                    product_dict.update({"ProductDetailImages": product_detail_image_list})

            # Get Product List Image (Max. 1)
            if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") > 0:
                product_image_list = []
                product_images = self.browser.get_elements(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible")
                if product_images:
                    for prod in product_images:
                        prod_property = self.browser.get_property(prod, "alt")
                        if prod_property:
                            print(prod_property)
                            product_image_list.append(prod_property)

                if len(product_image_list) > 0:
                    product_dict.update({"ProductImages": product_image_list})

            # Get Attachments (Max. 5)
            if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") > 0:
                attachment_list = []
                attachment_images = self.browser.get_elements(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text")
                if attachment_images:
                    for prod in attachment_images:
                        prod_property = self.browser.get_property(prod, "title")
                        if prod_property:
                            print(prod_property)
                            attachment_list.append(prod_property)

                if len(attachment_list) > 0:
                    product_dict.update({"Attachments": attachment_list})

            self.browser.click(f"li.oneConsoleTabItem:has-text('{product['Name']}'):visible >> div.close")

            result_dict.update({f"Product_{product['External_ID__c']}": product_dict})

        # Save dict to file
        if not os.path.exists("cms_data"):
            os.makedirs("cms_data", exist_ok=True)

        with open("cms_data/product_images.json", "w") as save_file:
            json.dump(result_dict, save_file, indent=2)

    def reassign_product_media_files(self):

        """
        Assigns Media Files stored in Salesforce CMS to the relevant Products in the target org.
        """

        # Check for default file
        if not os.path.exists("cms_data/product_images.json"):
            print("Missing CMS Definition File. Location: cms_data/product_images.json")
            raise Exception("Required file for robot is missing: cms_data/product_images.json. Please check the file and try again.")

        # Process Mapping File
        with open("cms_data/product_images.json", "r") as cms_file:
            product_dict = json.load(cms_file)

        if product_dict:

            # Go to Admin Console
            self.shared.go_to_app("Commerce - Admin")

            # Setup Selectors
            media_tab_selector = "div.uiTabBar >> span.title:text-is('Media')"

            # Process Product Records
            for product in dict(product_dict).items():

                results = self.salesforceapi.soql_query(f"SELECT Id, External_ID__c, Name from Product2 WHERE External_ID__c = '{product[1]['External_ID__c']}' LIMIT 1")

                if results["totalSize"] == 0:
                    print(f"No Products found for the External ID Provided {product[1]['External_ID__c']}. Skipping...")
                    continue

                try:
                    # Go To Record Page for Product and select Media tab
                    self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/r/Product2/{results['records'][0]['Id']}/view", timeout='30s')
                    self.browser.wait_for_elements_state(media_tab_selector, ElementState.visible, timeout="10s")
                    self.browser.click(media_tab_selector)
                    sleep(8)
                except TimeoutError:
                    print(f"Unable to access the Media tab for the current Product record with Id ({results['records'][0]['Id']}). Skipping...")
                    continue
                except Exception as e:
                    raise e

                # Process Product Detail Images
                if "ProductDetailImages" in dict(product[1]).keys() and self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") < 8:

                    for product_detail_image in list(product[1]["ProductDetailImages"]):

                        # Check Max. Number of Product Detail Images has not been reached
                        if self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") == 8:
                            print("The maximum number of images have already been assigned to the Product. Skipping...")
                            continue

                        # Check that CMS content has not already been assigned
                        skip = False
                        if self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") > 0:
                            product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible")
                            if product_detail_images:
                                for prod in product_detail_images:
                                    prod_property = self.browser.get_property(prod, "alt")
                                    print(f"Found alt text: {prod_property}")
                                    if prod_property:
                                        if prod_property in list(product[1]["ProductDetailImages"]):
                                            print("Skipping duplicate...")
                                            skip = True
                        if skip:
                            continue

                        # Assign New Image

                        self.browser.click("article.slds-card:has-text('Product Detail Images'):visible >> :nth-match(button.slds-button:text-is('Add Image'), 1)")
                        self.browser.wait_for_elements_state("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", ElementState.visible, timeout="10s")
                        self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", product_detail_image)

                        # Handle Search Results
                        try:
                            sleep(2)
                            search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{product_detail_image}'):visible")
                            if len(search_results) == 0:
                                self.browser.click(f"button.slds-button:text-is('Cancel')")
                                continue
                            if len(search_results) > 0:
                                self.browser.click("tr:has(span:text-matches('^{}$')) >> th >> span.slds-checkbox_faux".format(product_detail_image))
                                self.browser.click(f"button.slds-button:text-is('Save')")
                                self.browser.wait_for_elements_state(media_tab_selector, ElementState.visible, timeout="15s")
                                self.browser.click(media_tab_selector)
                        except TimeoutError:
                            print("Unable to find any matches for search results. Skipping...")
                            self.browser.click(f"button.slds-button:text-is('Cancel')")
                            continue
                else:
                    print("The maximum number of images have already been assigned to the Product or there are no Product Detail Images to process. Skipping...")

                # Process Product List Image

                if "ProductImages" in dict(product[1]).keys() and self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") < 1:

                    for product_image in list(product[1]["ProductImages"]):

                        # Check Max. Number of Product List Images has not been reached
                        if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") == 1:
                            print("The maximum number of images have already been assigned to the Product. Skipping...")
                            continue

                        # Check that CMS content has not already been assigned
                        skip = False
                        if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") > 0:
                            product_images = self.browser.get_elements(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible")
                            if product_images:
                                for prod in product_images:
                                    prod_property = self.browser.get_property(prod, "alt")
                                    print(f"Found alt text: {prod_property}")
                                    if prod_property:
                                        if prod_property in list(product[1]["ProductImages"]):
                                            print("Skipping duplicate...")
                                            skip = True
                        if skip:
                            continue

                        # Assign New Image

                        self.browser.click("article.slds-card:has-text('Product List Image'):visible >> :nth-match(button.slds-button:text-is('Add Image'), 1)")
                        self.browser.wait_for_elements_state("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", ElementState.visible, timeout="10s")
                        self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", product_image)

                        # Handle Search Results
                        try:
                            sleep(2)
                            search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{product_image}'):visible")
                            if len(search_results) == 0:
                                self.browser.click(f"button.slds-button:text-is('Cancel')")
                                continue
                            if len(search_results) > 0:
                                self.browser.click("tr:has(span:text-matches('^{}$')) >> td >> span.slds-radio".format(product_image))
                                self.browser.click(f"button.slds-button:text-is('Save')")
                                self.browser.wait_for_elements_state(media_tab_selector, ElementState.visible, timeout="15s")
                                self.browser.click(media_tab_selector)
                        except TimeoutError:
                            print("Unable to find any matches for search results. Skipping...")
                            self.browser.click(f"button.slds-button:text-is('Cancel')")
                            continue
                else:
                    print("The maximum number of images have already been assigned to the Product or there are no Product List Images to process. Skipping...")

                # Process Attachments

                if "Attachments" in dict(product[1]).keys() and self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") < 5:

                    for product_attachment in list(product[1]["Attachments"]):

                        # Check Max. Number of Attachments has not been reached
                        if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") == 5:
                            print("The maximum number of attachments have already been assigned to the Product. Skipping...")
                            continue

                        # Check that CMS content has not already been assigned
                        skip = False
                        if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") > 0:
                            product_attachments = self.browser.get_elements(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text")
                            if product_attachments:
                                for prod in product_attachments:
                                    prod_property = self.browser.get_property(prod, "title")
                                    print(f"Found title text: {prod_property}")
                                    if prod_property:
                                        if prod_property in list(product[1]["Attachments"]):
                                            print("Skipping duplicate...")
                                            skip = True
                        if skip:
                            continue

                        # Assign New Attachment

                        self.browser.click("article.slds-card:has-text('Attachments'):visible >> :nth-match(button.slds-button:text-is('Add Attachment'), 1)")
                        self.browser.wait_for_elements_state("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", ElementState.visible, timeout="10s")
                        self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", product_attachment)

                        # Handle Search Results
                        try:
                            sleep(2)
                            search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{product_attachment}'):visible")
                            if len(search_results) == 0:
                                self.browser.click(f"button.slds-button:text-is('Cancel')")
                                continue
                            if len(search_results) > 0:
                                self.browser.click("tr:has(span:text-matches('^{}$')) >> th >> span.slds-checkbox_faux".format(product_attachment))
                                self.browser.click(f"button.slds-button:text-is('Save')")
                                self.browser.wait_for_elements_state(media_tab_selector, ElementState.visible, timeout="15s")
                                self.browser.click(media_tab_selector)
                        except TimeoutError:
                            print("Unable to find any matches for search results. Skipping...")
                            self.browser.click(f"button.slds-button:text-is('Cancel')")
                            continue
                else:
                    print("The maximum number of attachments have already been assigned to the Product or there are no Product Attachments to process. Skipping...")

                # Close Tab
                try:
                    self.browser.click(f"li.oneConsoleTabItem:has-text('{results['records'][0]['Name']}'):visible >> div.close")
                except:
                    continue

    def open_experience_cloud_collections_page(self, experience_cloud_name):
        """Browses to the Collections Page of an Experience Cloud Site"""
        self.shared.go_to_setup_admin_page('SetupNetworks/home', 2)
        self.browser.wait_for_elements_state("iframe >>> table.zen-data", ElementState.visible, "15s")
        if self.browser.get_element_count(f"{self.shared.iframe_handler()} div.pbBody >> table.zen-data >> tr.dataRow:has-text('{experience_cloud_name}')") > 0:
            self.browser.click(f"{self.shared.iframe_handler()} div.pbBody >> table.zen-data >> tr.dataRow:has-text('{experience_cloud_name}') >> a.networkManageLink")
            sleep(2)
            self.browser.switch_page('NEW')
            self.browser.wait_for_elements_state("a.js-workspace-contentManager", ElementState.visible, "15s")
            self.browser.click("a.js-workspace-contentManager")
            self.browser.wait_for_elements_state("a[id=cmcNodeItem-managedContentCollections]", ElementState.visible, "15s")
            self.browser.click("a[id=cmcNodeItem-managedContentCollections]")
            sleep(1)

    def generate_managed_content_collection_file(self, experience_cloud_name):
        """Generate json file with details of collections"""
        self.open_experience_cloud_collections_page(experience_cloud_name)
        self.browser.wait_for_elements_state("table.slds-table", ElementState.visible, "15s")

        collection_data_dict = dict({})

        # Gather Current Details
        tr_elements = self.browser.get_elements("table.slds-table >> tr:has(a)")

        for elem in tr_elements:
            self.browser.new_page(self.browser.get_property(f"{elem} >> a", "href"))
            self.browser.wait_for_elements_state("h1.slds-page-header__title", ElementState.visible, "15s")

            # Scrape Details
            collection_name = self.browser.get_property("h1.slds-page-header__title", "innerText")
            content_type = self.browser.get_property("li:has(p[title='Content Type']) >> :nth-match(p, 2)", "innerText")

            listview_name = ""
            collection_type = ""
            collection_content_name_list = []

            if self.browser.get_element_count("li:has(p[title='Content Source']):visible") > 0:
                collection_type = "SALESFORCE"
                listview_name = self.browser.get_property("li:has(p[title='List View']) >> :nth-match(p, 2)", "innerText")
            else:
                collection_type = "CMS"
                for table_row in self.browser.get_elements("table.slds-table >> tr:has(a)"):
                    collection_content_name_list.append(self.browser.get_property(f"{table_row} >> a", "innerText"))
            
            # Add Details to Dict
            collection_data_dict.update({
                collection_name: {
                    "collection_type": collection_type,
                    "content_type": content_type,
                    "related_cms_content": collection_content_name_list,
                    "object_name": content_type,
                    "listview": listview_name
                }
            }
            )

            self.browser.close_page()

        if collection_data_dict and len(collection_data_dict):
            save_location = os.path.join("datasets", "cms_collection_data")
            os.makedirs(save_location, exist_ok=True)

            with open(os.path.join(save_location, "cms_collection_dataset.json"), "w", encoding="utf-8") as save_file:
                save_file.write(json.dumps(collection_data_dict, indent=4))

    def upload_cms_collections(self, site_name, upload_file_location=os.path.join("datasets", "cms_collection_data", "cms_collection_dataset.json"), ):

        if not os.path.exists(upload_file_location):
            raise Exception("No CMS Collection Data Found. Unable to upload.")
        
        with open(upload_file_location, 'r', encoding="utf-8") as dataset_file:
            file_data = json.load(dataset_file)

        if file_data:

            self.open_experience_cloud_collections_page(site_name)
            
            # Wait for Collections to Load
            no_collection_mode = False
            found_element = False
            counter = 1
            while counter < 10:
                sleep(1)
                create_button_count = self.browser.get_element_count("button.newcollection:has-text('Create Collection')")
                table_count = self.browser.get_element_count("table.slds-table")

                if create_button_count > 0:
                    no_collection_mode = True
                    found_element = True
                    print("Found Create Collection button...")
                    break

                if table_count > 0:
                    no_collection_mode = False
                    found_element = True
                    print("Found Table button...")
                    break 

                counter += 1

            if not found_element:
                print("No Supported Elements Found")
                return 
            
            # Set Defaults for Robot

            modal_next_button = "div.modal-footer >> button.nextButton"
            collections_to_add = set()

            # Add Content

            if no_collection_mode:
                print(">>> Adding All Collections")

            for collection, collection_details in file_data.items():

                # Check if Collection Exists
                if no_collection_mode:
                    collections_to_add.add(collection)
                else:
                    print(f">>> Checking Collection {collection}")
                    collection_found = False
                    for table_row in self.browser.get_elements("table.slds-table >> tr:has(a)"):
                        selection_text = self.browser.get_property(f"{table_row} >> a", "innerText")
                        if selection_text == collection:
                            collection_found = True
                            break
                    
                    if collection_found:
                        print(f">>> {collection} Found. Skipping")
                    else:
                        print(f">>> {collection} will be created")
                        collections_to_add.add(collection)

            if len(collections_to_add) > 0:

                # Check That Salesforce CRM Connections Have Approved Objects
                salesforce_objects = set()
                for key, collection_detail in file_data.items():
                    if collection_detail.get("collection_type") == "SALESFORCE":
                        salesforce_objects.add(collection_detail.get("content_type"))

                if len(salesforce_objects) > 0:
                    # Check Object is Approved
                    self.browser.click("a[id=cmcNodeItem-content]")
                    sleep(1)
                    self.browser.click("a[id=cmcNodeItem-managedContentTypes]")
                    sleep(2)

                    for obj in salesforce_objects:
                        object_exists = False
                        if self.browser.get_element_count("table.slds-table:visible") > 0:
                            if self.browser.get_element_count(f"table.slds-table:visible >> tbody >> tr >> th:has-text('{obj}')") > 0:
                                object_exists = True
                        
                        if not object_exists:
                            # Add Object
                            self.browser.click("button:has-text('Add CRM Connections')")
                            self.browser.fill_text("div.communitySetupManagedContentMultiSelectTable >> input.slds-input", obj)
                            sleep(5)
                            if self.browser.get_element_count(f"div.listContainer >> table >> tbody >> tr:has-text('{obj}')") < 1:
                                    print(f"Unable to find Object called '{obj}'. Skipping")
                                    continue
                            self.browser.click(f"div.listContainer >> table >> tbody >> :nth-match(tr:has-text('{obj}'), 1) >> th >> div.slds-truncate")
                            self.browser.click("button.saveButton:visible")
                            sleep(1)

                    self.browser.click("a[id=cmcNodeItem-managedContentCollections]")
                    sleep(1)

                for collection_add in collections_to_add:

                    # Create Collection
                    if no_collection_mode:
                        self.browser.click("button.slds-button:has-text('Create Collection')")
                    else:
                        self.browser.click("button.slds-button:text('New')")

                    self.browser.wait_for_elements_state("div.stepContainer", ElementState.visible, "15s")

                    # Add Collection Details
                    collection_data = file_data.get(collection_add)

                    collection_type = collection_data.get("collection_type")
                    content_type = collection_data.get("content_type")
                    cms_collection_content = collection_data.get("related_cms_content")
                    sf_list_view = collection_data.get("listview")

                    # Set Name
                    self.browser.fill_text("div.stepContainer >> div.slds-form-element__control >> input.slds-input:visible", collection_add)
                    self.browser.press_keys("div.stepContainer >> div.slds-form-element__control >> input.slds-input:visible", "Enter")

                    # Set Type
                    if collection_type == "SALESFORCE":

                        # Add Salesforce Details
                        self.browser.click("div.stepContainer >> div.slds-visual-picker >> label.crm")
                        self.browser.click(modal_next_button)
                        sleep(1)
                        self.browser.click("div.stepContainer >> button.slds-combobox__input:visible")
                        sleep(1)
                        self.browser.click(f"div.activeStep >> div.slds-listbox >> lightning-base-combobox-item:has-text('{content_type}')")
                        sleep(5)
                        if self.browser.get_element_count(f"div.activeStep >> table >> tbody >> tr:has-text('{sf_list_view}')") < 1:
                            print(f"Unable to Find List View '{sf_list_view}'")
                            continue
                        self.browser.click(f"div.activeStep >> table >> tbody >> tr:has-text('{sf_list_view}') >> span.slds-radio")
                        self.browser.click(modal_next_button)
                        sleep(2)
                        

                    elif collection_type == "CMS":
                        # Add CMS Content
                        self.browser.click("div.stepContainer >> div.slds-visual-picker >> label.cms")
                        self.browser.click(modal_next_button)
                        sleep(1)
                        self.browser.select_options_by("div.slds-select_container >> select.slds-select", SelectAttribute.label, content_type)
                        self.browser.click("div.activeStep >> div.slds-visual-picker >> label.manual")
                        self.browser.click(modal_next_button)
                        sleep(2)
                        for cms_content in cms_collection_content:
                            self.browser.fill_text("div.activeStep >> input.slds-input", cms_content)
                            sleep(3)
                            if self.browser.get_element_count(f"div.listContainer >> table >> tbody >> tr:has-text('{cms_content}')") < 1:
                                print(f"Unable to find CMS Content called '{cms_content}'. Skipping")
                                continue
                            self.browser.click(f"div.listContainer >> table >> tbody >> tr:has-text('{cms_content}') >> th >> div.slds-truncate")
                        self.browser.click(modal_next_button)
                        sleep(2)

                    else:
                        print("TYPE NOT FOUND")

                    self.browser.wait_for_elements_state("a[id=cmcNodeItem-managedContentCollections]", ElementState.visible, "15s")
                    self.browser.click("a[id=cmcNodeItem-managedContentCollections]")
                    sleep(2)

