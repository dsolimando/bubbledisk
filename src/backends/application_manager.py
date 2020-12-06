import os
import string
import gnome.vfs
import tool_box
from re import match, compile

class application:

    name = ""
    exec_url = ""
    version = ""

    def __init__(self,name,exec_url,version):
        self.name = name
        self.exec_url = exec_url
        self.version = version

    def get_name (self):
        return self.name

    def get_execurl (self):
        return self.exec_url

    def get_version (self):
        return self.version

class application_manager:

    applications_needed = ["cdrecord",
                           "cdrdao",
                           "sox",
                           "mkisofs",
                           "mpg123",
                           "ogg123",
                           "eject",
                           "readcd"]

    applications_installed = []

    path = []

    comline_tools = None
    config_handler = None

    def __init__ (self,config_handler):
        self.config_handler = config_handler

        path = self.config_handler.get("apps/path")
        if path == "":
            config_handler.set("apps/path",os.environ['PATH'])
            path = self.config_handler.get("apps/path")

        self.path = path.split (os.pathsep)
        self.comline_tools = tool_box.Common_tools()
        self.search_applications()

    def get_version (self,app):
        if app == "cdrdao":
            version_regexp = compile(".*Cdrdao\ version\ (\d+)\.(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app," ")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2)
                            +"."
                            +version_match.group(3))

        elif app == "cdrecord":
            version_regexp = compile(".*Cdrecord(.+)\ (\d+)\.(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app,"-version")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(2)
                            +"."
                            +version_match.group(3)
                            +"."
                            +version_match.group(4))
        elif app == "sox":
            version_regexp = compile(".*sox:\s+Version\s(\d+)\.(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app,"-help")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2)
                            +"."
                            +version_match.group(3))

        elif app == "mkisofs":
            version_regexp = compile(".*mkisofs\s+(\d+)\.(\d.+)\ .*")
            output = self.comline_tools.execute (app,"-version")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2))

        elif app == "mpg123":
            version_regexp = compile(".*Version\s+(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app,"-help")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2))

        elif app == "ogg123":
            version_regexp = compile(".*vorbis-tools\s+(\d+)\.(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app,"-help")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2)
                            +"."
                            +version_match.group(3))

        elif app == "eject":
            version_regexp = compile(".*eject version\s+(\d+)\.(\d+)\.(\d+).*")
            output = self.comline_tools.execute (app,"-V")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2)
                            +"."
                            +version_match.group(3))

        elif app == "readcd":
            version_regexp = compile("readcd (\d).(\d\d)")
            output = self.comline_tools.execute (app,"-version")
            for res in output:
                version_match = version_regexp.match(res)
                if version_match != None:
                    return (version_match.group(1)
                            +"."
                            +version_match.group(2))

    def search_applications (self):
        self.applications_installed = []
        for dir in self.path:
            files = gnome.vfs.open_directory (dir)
            for file in files:
                if file.name in self.applications_needed:
                    if not file.name in self.get_apps_installed_names():
                        version = self.get_version(file.name)
                        app = application(file.name,
                                          dir+os.sep+file.name,
                                          version)

                        self.applications_installed.append (app)
    def get_apps_installed_names (self):
        appnames = []
        for app in self.applications_installed:
             appnames.append (app.get_name())
        return appnames

    def get_application_infos (self, app):
        for val in self.applications_installed:
             if val.get_name() == app:
                 return (val.get_name(),val.get_execurl(), val.get_version())
        return None

#app = application_manager()
#app.search_applications ()
#print app.get_application_infos("mpg123")
