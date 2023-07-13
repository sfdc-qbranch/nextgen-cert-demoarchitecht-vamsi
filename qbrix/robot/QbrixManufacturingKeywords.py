from time import sleep
from Browser import ElementState
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixManufacturingKeywords(QbrixRobotTask):

    """Shared Keywords for Manufacturing"""

    def enable_manufacturing_service_console(self):
        """
        Enables Service Console for Manufacturing Setting in Salesforce Setup
        """
        enable_mfgservice_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("MfgServiceExcellenceSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Service Console for Manufacturing')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(enable_mfgservice_toggle)
        if visible:
            self.browser.click(enable_mfgservice_toggle)
            sleep(2)

    def enable_account_manager_targets(self):
        """
        Enables Account Manager Targets for Manufacturing Setting in Salesforce Setup
        """
        enable_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("AcctMgrTargetSettings/home")
        sleep(10)
        visible = "visible" in self.browser.get_element_states(enable_toggle)
        if visible:
            self.browser.click(enable_toggle)
            sleep(2)

    def enable_partner_visit_management(self):
        """
        Enables Partner Visit Management for Manufacturing Setting in Salesforce Setup
        """
        enable_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("MfgPartnerVisitMgmtSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Partner Visit Management')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(enable_toggle)
        if visible:
            self.browser.click(enable_toggle)
            sleep(2)

    def enable_partner_performance_management(self):
        """
        Enables Partner Performance Management for Manufacturing Setting in Salesforce Setup
        """
        enable_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("MfgPartnerPerfMgmtSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Partner Performance Management')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(enable_toggle)
        if visible:
            self.browser.click(enable_toggle)
            sleep(2)

    def enable_group_membership(self):
        """
        Enables Group Membership Settings Salesforce Setup
        """
        enable_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("GroupMembershipSettings/home")
        self.browser.wait_for_elements_state("p:text-is('Group Membership')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(enable_toggle)
        if visible:
            self.browser.click(enable_toggle)
            sleep(2)

    def enable_partner_lead_management(self):
        """
        Enables Partner Lead Management Settings Salesforce Setup
        """
        self.shared.go_to_setup_admin_page("MfgPartnerLeadMgmtSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Partner Lead Management')", ElementState.visible, '30s')
        if "checked" not in self.browser.get_element_states("div.slds-card:has(h2:text-is('Partner Lead Management')) >> input[name='mfgPartnerLeadMgmtPref']"):
            self.browser.click("div.slds-card:has(h2:text-is('Partner Lead Management')) >> lightning-input.slds-form-element")
            sleep(2)
            

    def enable_program_based_business(self):
        """
        Enables Program Based Business for Manufacturing Setting in Salesforce Setup
        """
        self.shared.go_to_setup_admin_page("MfgProgramTemplates/home")
        self.browser.wait_for_elements_state("h2:text-is('Program Based Business')", ElementState.visible, '30s')
        if "checked" not in self.browser.get_element_states("div.slds-card:has(h2:text-is('Program Based Business')) >> input[name='mfgProgramPref']"):
            self.browser.click("div.slds-card:has(h2:text-is('Program Based Business')) >> lightning-input.slds-form-element")
            sleep(2)

    def enable_warranty_lifecycle_management(self):
        """
        Enables  Warranty Lifecycle Management for Manufacturing Setting in Salesforce Setup
        """
        self.shared.go_to_setup_admin_page("MfgServiceSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Warranty Lifecycle Management')", ElementState.visible, '30s')
        if "checked" not in self.browser.get_element_states("div.slds-card:has(h2:text-is('Warranty Lifecycle Management')) >> input[name='mfgServicePref']"):
            self.browser.click("div.slds-card:has(h2:text-is('Warranty Lifecycle Management')) >> lightning-input.slds-form-element")
            sleep(2)


    def enable_automotive_cloud_setting(self):
        """
        Enables Automotive Cloud Setting
        """
        self.shared.go_to_setup_admin_page("AutomotiveFoundationSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Automotive')", ElementState.visible, '30s')
        if "checked" not in self.browser.get_element_states("lightning-layout.slds-grid:has(h2:text-is('Automotive')) >> input[name='automotivePref']"):
            self.browser.click("lightning-layout.slds-grid:has(h2:text-is('Automotive')) >> lightning-input.slds-form-element")
            sleep(2)

    def enable_automotive_cloud_service_console_setting(self):
        """
        Enables Automotive Cloud Service Console Setting
        """
        self.shared.go_to_setup_admin_page("AutomotiveServiceExcellenceSettings/home")
        self.browser.wait_for_elements_state("h2:text-is('Service Console for Automotive')", ElementState.visible, '30s')
        if "checked" not in self.browser.get_element_states("div.slds-card:has(h2:text-is('Service Console for Automotive')) >> input[name='automotiveServiceExcellencePref']"):
            self.browser.click("div.slds-card:has(h2:text-is('Service Console for Automotive')) >> lightning-input.slds-form-element")
            sleep(2)