from datetime import datetime
from typing import Optional, Dict, Any
from nicegui import ui
from core.ui import UserInterfaceElements
from core.db import BaseDB
import os
import json
import inspect


class TemplateModule:
    def __init__(self, api: Dict[str, Any]):
        # Maintain a reference to the database
        #print("Api:", api)
        self.db: BaseDB = api.get("db", None)

        # Declare uielems helper class
        self.uielems = UserInterfaceElements()


        # Get the module properties from the properties.json file
        cls_file = inspect.getfile(self.__class__)
        cls_dir = os.path.dirname(os.path.abspath(cls_file))

        # 2. Look for properties.json right next to it
        prop_path = os.path.join(cls_dir, "properties.json")
        if not os.path.isfile(prop_path):
            raise FileNotFoundError(f"No properties.json found in {cls_dir!r}")

        # 3. Load and store
        with open(prop_path, "r", encoding="utf-8") as fp:
            self.properties = json.load(fp)

        # Register self routes
        self.register_routes()

        # TODO: check if properties.json has all the required fields
        self.moduleID = self.properties.get("moduleID", None)
        self.module_name = self.properties.get("moduleName", None)
        self.module_description = self.properties.get("cardDescription", None).get("description", None)
        self.table_name = self.properties.get("database", {}).get("tableName", None)

        self.permissions = None

    def register_routes(self):
        """
        Register the routes for the module
        """
        route_root = "/" + self.properties.get("moduleID")

        # Register the main page
        @ui.page(route_root)
        def main_page():
            self.uielems.draw_header(
                page_title=self.module_name
            )
            self.draw_main_page()

        # Register the configuration page
        @ui.page(route_root + "/config")
        def config_page():
            self.uielems.draw_header(
                page_title= self.module_name,
                sub_page="Configuration"
            )
            self.draw_config_page()

        # Register the settings page
        @ui.page(route_root + "/settings")
        def settings_page():
            self.uielems.draw_header(
                page_title=self.module_name,
                sub_page="Settings"
            )
            self.draw_settings_page()

        # Register the help page
        @ui.page(route_root + "/help")
        def help_page():
            self.uielems.draw_header(
                page_title=self.module_name,
                sub_page="Help"
            )
            self.draw_help_page()

    def user_permitted(self, roleids: str) -> bool:
        """
        Check if the user is permitted to access this module.
        :param userid: The user ID to check.
        :return: True if the user is permitted, False otherwise.
        """
        if(roleids == None):
            # If the user has no roles, they are not permitted
            return False
        for role_id in roleids:
            role = self.db.find("roles", {"_id": role_id})
            if not role:
                # If the role is not found, skip it
                continue

            role = role[0]  # Get the first role
            permissions = role.get("permissions", [])
            #print("Permissions:", permissions)
            if permissions =="admin":
                # If the role has admin permissions, it is a superuser
                return True
            
            for permission in permissions:
                perm_module = permission.get("moduleID")
                print("Module ID:", perm_module, "Module Name:", self.moduleID)
                if permission.get("moduleID") == self.moduleID or permission.get("moduleID") == "all" or permission.get("moduleID") == self.module_name:
                    # If the module ID matches, the user is permitted
                    return True
                

        return False

    def draw_card(self):
        """
        Draws the card for the module
        Expected format in properties.json:
        "cardDescription": {
            "title": "Template Module",
            "description": "This is a template module for CliniKit.",
            "icon": "tab_unselected",
            "iconColor": "text-blue-500"
        }

        Parent has to provide the grid for the cards.
        Default endpoint when clicking on card is from the module_name
        """

        with ui.card().classes("w-full transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer") as card:
            # Add the icon
            cardDescription = self.properties.get("cardDescription", {})
            #print("Card Description:", cardDescription)
            with ui.row().classes("relative"):
                if "icon" in cardDescription:
                    ui.icon(cardDescription["icon"]).classes(
                        "text-4xl " + cardDescription["iconColor"]
                    )

                # Add the title
                if "title" in cardDescription:
                    ui.label(cardDescription["title"]).classes("text-h6 cursor-pointer transition-colors duration-200 hover:text-blue-500").on(
                        "click", lambda: ui.navigate.to(self.moduleID)
                    )

            with ui.dropdown_button().classes("ml-auto absolute right-2 top-2").props("outline flat rounded no-icon-animation dropdown-icon='more_vert'"):
                ui.item("Settings", on_click=lambda: ui.navigate.to(self.moduleID+"/settings"))
                ui.item("Configure", on_click=lambda: ui.navigate.to(self.moduleID+"/config"))
                ui.item("Help", on_click=lambda: ui.navigate.to(self.moduleID+"/help"))

            # Add the description
            if "description" in cardDescription:
                ui.label(cardDescription["description"]).classes("text-body1")
            
    
    def get_properties(self) -> Dict[str, Any]:
        """
        Returns a dictionary with the module information
        :return: A dictionary with the module information
        """
        return self.properties


    def draw_config_page(self):
        """
        Draws the configuration page for the module
        """
        with ui.card().classes("w-full"):
            ui.label("Configuration Page").classes("text-h6")
            ui.label("This is the configuration page for the module.").classes(
                "text-body1"
            )

    def draw_settings_page(self):
        """
        Draws the settings page for the module
        """
        with ui.card().classes("w-full"):
            ui.label("Settings Page").classes("text-h6")
            ui.label("This is the settings page for the module.").classes("text-body1")

    def draw_help_page(self):
        """
        Draws the help page for the module
        Pretty prints all the properties of the module
        """
        with ui.card().classes("w-full"):
            ui.label("Help Page").classes("text-h6")
            ui.label("This is the help page for the module.").classes("text-body1")

            # Pretty print the properties
            ui.label("Module Properties:").classes("text-body1")
            for key, value in self.properties.items():
                ui.label(f"{key}: {value}").classes("text-body2")

    def draw_main_page(self):
        """
        Draws the main page for the module
        """
        with ui.card().classes("w-full"):
            ui.label("Main Page").classes("text-h6")
            ui.label("This is the main page for the module.").classes("text-body1")
