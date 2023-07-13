from abc import ABC, abstractmethod
from cumulusci.tasks.command import Command
from cumulusci.core.keychain import BaseProjectKeychain

class QbrixBaseSalesforceDXTask(Command, ABC):

    """Run a command against the Salesforce CLI"""

    task_options = {
        "org": {
            "description": "Org Alias",
            "required": False
        },
        "command": {
            "description": "Command to execute against the Salesforce CLI",
            "required": True,
        },
        "cli": {
            "description": "The CLI to use, defaults to 'sf'",
            "required": True,
        },
        "extra": {"description": "Append additional options to the command"},
    }

    keychain_class = BaseProjectKeychain

    def _init_options(self, kwargs):
        super(QbrixBaseSalesforceDXTask, self)._init_options(kwargs)
        self.env = self._get_env()

    @property
    def keychain_cls(self):
        klass = self.get_keychain_class()
        return klass or self.keychain_class

    @abstractmethod
    def get_keychain_class(self):
        return None

    @property
    def keychain_key(self):
        return self.get_keychain_key()

    @abstractmethod
    def get_keychain_key(self):
        return None
    
    def _load_keychain(self):
        if self.keychain is not None:
            return

        keychain_key = self.keychain_key if self.keychain_cls.encrypted else None

        if self.project_config is None:
            self.keychain = self.keychain_cls(self.universal_config, keychain_key)
        else:
            self.keychain = self.keychain_cls(self.project_config, keychain_key)
            self.project_config.keychain = self.keychain

    def _prepruntime(self):

        if ("org" in self.options and not self.options["org"] is None) and self.keychain is None:
            self._load_keychain()
            self.logger.info("Org passed in but no keychain found in runtime")

        if not self.org_config.access_token is None:
            self.accesstoken = self.org_config.access_token

        if not self.org_config.instance_url is None:
            self.instanceurl = self.org_config.instance_url

    def _get_command(self):

        cli = self.options['cli'] if "cli" in self.options else "sf"

        command = "{sf_cli} {command}".format(
            command=self.options["command"], sf_cli=cli
        )
        if self.options.get("extra"):
            command += " {}".format(self.options["extra"])
        
        return command