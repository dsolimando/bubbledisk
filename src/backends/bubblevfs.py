import xml.dom.minidom
import xml.dom
import sys
import string
from xml.xpath import Evaluate
from xml.dom.ext.reader import PyExpat
from re import match, compile
import gnomevfs
import shutil
import os
import tool_box
import gobject

class bubblevfs:

    def cp (self,source,dest):
        pass

    def mv (self,source,dest):
        pass

    def ls (self,dir):
        pass

    def mkdir (self,dirname,dest):
        pass

    def rm (self,url):
        pass

    def get_file_size (self,file):
        pass

    def get_file_type (self,file):
        pass

    def get_target_file (self,file):
        pass

    def get_url_pattern (self):
        pass


class xmlfs (bubblevfs):
    doc = None
    common_tools =None
    base_dir = ""
    file_sizes = None

    def __init__ (self,common_tools,base_dir):
        self.base_dir = base_dir
        self.doc = xml.dom.minidom.parseString("""<file type="directory" name="""+'"'+base_dir+'"'+""" location="" size="0" session="0"></file>""")
        self.common_tools = common_tools
        self.file_sizes = {}

    def __compute_filetree_size (self,folder,session="0",window=None):
        try:
            total_size = 0
            for file in gnomevfs.open_directory(folder):
                try:
                    if file.name == "." or file.name == "..":
                        continue
                    elif file.type == gnomevfs.FILE_TYPE_REGULAR:
                        total_size += file.size
                        self.file_sizes [folder+"/"+file.name] = file.size

                    elif file.type == gnomevfs.FILE_TYPE_DIRECTORY:
                        children_size = self.__compute_filetree_size (folder+"/"+file.name,session,window)
                        total_size += children_size
                        self.file_sizes [folder+"/"+file.name] = children_size

                except ValueError:
                    pass

            return total_size
        except gnomevfs.AccessDeniedError,err:
            return total_size


    def explore_dir2 (self,folder,session="0",window=None):
        dest_node_list = self.__get_filenode(folder)
        dest_node = dest_node_list[0]


        # If already explored
        if dest_node.hasChildNodes():
            return

        folder = dest_node.getAttribute("location")

        if folder == "":
            # we are at the root of the xml file system and the root has no location on real fs
            return

        try:
            for file in gnomevfs.open_directory(folder):
                try:
                    if file.name == "." or file.name == "..":
                        continue
                    elif file.type == gnomevfs.FILE_TYPE_REGULAR:
                        node = self.__create_file_node (file.name,folder+"/"+file.name,session,"file",str(file.size),oct(file.permissions),"0")
                        dest_node.appendChild(node)

                        if window != None:
                            gobject.idle_add(window.update,[file.name,folder,dest_node.getAttribute("name")])

                    elif file.type == gnomevfs.FILE_TYPE_DIRECTORY:
                        node = self.__create_file_node (file.name,folder+"/"+file.name,session,"directory",str(self.file_sizes[folder+"/"+file.name]),"","0")
                        dest_node.appendChild(node)
                        if window != None:
                            gobject.idle_add(window.update,[file.name,folder,self.get_url (dest_node)])

                except ValueError:
                    pass

            return
        except gnomevfs.AccessDeniedError,err:
            return

    def __create_file_node (self,filename,url,session_num,file_type,size,perm,graftpoint):
         node = self.doc.createElement("file")
         node.setAttribute ("type",file_type)
         node.setAttribute ("name",filename)
         node.setAttribute ("location",url)
         node.setAttribute ("session",session_num)
         node.setAttribute ("size",size)
         node.setAttribute ("permissions",perm)
         node.setAttribute ("graftpoint",graftpoint)

         return node

    def __get_filenode (self,url):
        exploded_url = url.split("/")
        xpath_query = "/"
        for dir_name in exploded_url:
            xpath_query += "file[@name=\""+dir_name+"\"]/"

        xpath_query = xpath_query[0:-1]
        des_file_elem = Evaluate(xpath_query,self.doc)
        #print xpath_query
        return des_file_elem

    def __update_partition_size (self,added_size,node):
        try:
            while node!=None:
                current_size = node.getAttribute("size")
                new_size = added_size + int(current_size)
                node.setAttribute ("size",str (new_size))
                node = node.parrentNode
        except AttributeError,err:
            return

    def get_url (self,node):
        url = ""
        try:
            while node!=None:
                current_uri = node.getAttribute("name")
                url =  current_uri + "/" + url
                node = node.parrentNode
        except AttributeError,err:
            return url

    def get_file_infos (self,file):
        node = self.__get_filenode(file)
        return (int(node[0].getAttribute("size")),
                node[0].getAttribute("permissions"),
                node[0].getAttribute("type"),
                node[0].getAttribute("location"),
                node[0].getAttribute("session"))


    def get_file_size (self,file):
        node = self.__get_filenode(file)
        file_size = node[0].getAttribute("size")
        return int(file_size)/1024

    def get_file_type (self,file):
        node = self.__get_filenode(file)
        file_type = node[0].getAttribute("type")
        return file_type

    def get_target_file (self,file):
        node = self.__get_filenode(file)
        target = node[0].getAttribute("location")
        return target

    def get_file_permissions (self,url):
        node = self.__get_filenode(url)
        permission = node[0].getAttribute("permissions")
        return permission

    def get_url_pattern (self):
        return "(.*/)(.*)"

    def print_xml (self):
        print self.doc.toprettyxml(indent='\t',newl='\n')

    def __compute_filetree_sizetree (self,node,url,graft_points):
        for n in node.childNodes:
            if n.getAttribute("type") == "file":
                graft_points [url+"/"+n.getAttribute("name")] = n.getAttribute("location")
            else:
                self.__compute_filetree_sizetree (n,url+"/"+n.getAttribute("name"),graft_points)
        return graft_points

    def __compute_filetree_sizetree2 (self,node,url,graft_points):
        for n in node.childNodes:
            if n.getAttribute("graftpoint") == "1":
                print "c un graftpoint "+n.getAttribute("graftpoint")
                graft_points [url+"/"+n.getAttribute("name")] = n.getAttribute("location")
            self.__compute_filetree_sizetree2 (n,url+"/"+n.getAttribute("name"),graft_points)
        return graft_points

    def generate_graftpoints (self):
        graft_points = {}
        root_node = self.__get_filenode (self.base_dir)
        graft_points = self.__compute_filetree_sizetree2 (root_node[0],"",graft_points)
        return graft_points

    def set_graftpoint (self,file):
       file_elem = self.__get_filenode (file)
       file_elem[0].setAttribute ("graftpoint","1")

    def unset_graftpoint (self,file):
       file_elem = self.__get_filenode (file)
       file_elem[0].setAttribute ("graftpoint","0")

    def cp (self,source_url_in_fs,dest_url,session="0",graftpoint="1",window=None):
        total_size = 0

        file_info = gnomevfs.get_file_info(source_url_in_fs)
        #source_url_in_fs = string.replace(source_url_in_fs,"'","<appstroph>")
        if window != None:
            gobject.idle_add(window.show_window)

        dest_dir_elem = self.__get_filenode (dest_url)
        source_url_splitted = source_url_in_fs.split("/")

        # Test if file already exists
        exist_file_node = self.__get_filenode (dest_url+"/"+source_url_splitted[-1])

        if len(exist_file_node) != 0:
            # update total files tree size
            current_size = int(dest_dir_elem[0].getAttribute("size"))
            node_todelete_size = int (exist_file_node[0].getAttribute("size"))
            new_size = current_size - node_todelete_size
            dest_dir_elem[0].setAttribute ("size",str(new_size))

            total_size -= node_todelete_size
            # delete the node
            self.rm(dest_url+"/"+source_url_splitted[-1])

        if file_info.type == gnomevfs.FILE_TYPE_DIRECTORY:
            tree_size = self.__compute_filetree_size (source_url_in_fs,session,window)
            print tree_size
            new_node = self.__create_file_node (
                                                source_url_splitted[-1],
                                                source_url_in_fs,
                                                session,
                                                "directory",
                                                str(tree_size),
                                                oct(file_info.permissions),
                                                graftpoint)
            if window != None:
                    gobject.idle_add(window.update,[source_url_splitted[-1],source_url_in_fs,dest_url])
            dest_dir_elem[0].appendChild(new_node)

            self.file_sizes [source_url_in_fs] = tree_size

            # update total tree size
            current_size = int(dest_dir_elem[0].getAttribute ("size"))
            total_size += tree_size
            dest_dir_elem[0].setAttribute ("size", str(total_size+current_size))

        elif file_info.type == gnomevfs.FILE_TYPE_REGULAR:
            source_url_splitted = source_url_in_fs.split("/")
            new_node = self.__create_file_node (source_url_splitted[-1],
                                                source_url_in_fs,
                                                session,
                                                "file",
                                                str(file_info.size),
                                                oct(file_info.permissions),
                                                graftpoint)
            dest_dir_elem[0].appendChild(new_node)

            self.file_sizes [source_url_in_fs] = file_info.size

            # update total tree size
            current_size = int(dest_dir_elem[0].getAttribute ("size"))
            total_size += file_info.size
            dest_dir_elem[0].setAttribute ("size",str(current_size + file_info.size))

        if window != None:
            gobject.idle_add(window.hide_window)


        return total_size

    def mv (self,source_url,dest_url):
        source_node = self.__get_filenode (source_url)
        source_node_daddy = source_node[0].parentNode
        dest_node = self.__get_filenode (dest_url)
        rm_node = source_node_daddy.removeChild(source_node[0])
        dest_node[0].appendChild (rm_node)

    def ls(self,dir):
        node_to_list = self.__get_filenode (dir)
        file_list = []
        for node in node_to_list[0].childNodes:
            #file_list.append ([node.getAttribute("name"),node.getAttribute("location")])
            file_list.append (node.getAttribute("name"))

        return file_list

    def mkdir (self,dirname, location,graftpoint="1"):
        des_dir_elem = self.__get_filenode (location)
        new_dir_elem = self.__create_file_node (dirname,"","0","directory","0","0755",graftpoint)
        des_dir_elem[0].appendChild(new_dir_elem)

    def rm (self,url):
        des_dir_elem = self.__get_filenode (url)

        try:
            del self.file_sizes[des_dir_elem[0].getAttribute("location")]
        except KeyError:
            pass


        # update node sizes
        total_size_removed = int(des_dir_elem[0].getAttribute("size"))
        parent = des_dir_elem[0].parentNode
        current_parent_size = int(parent.getAttribute("size"))
        parent.setAttribute ("size",current_parent_size-total_size_removed)
        parent.removeChild (des_dir_elem[0])
        des_dir_elem[0].unlink()



        return total_size_removed

class slinkfs (bubblevfs):
    common_tools = None

    def __init__ (self,common_tools,base_dir):
        self.common_tools = common_tools
        if not os.path.exists ("/tmp/"+base_dir):
            os.mkdir("/tmp/"+base_dir)

    def get_file_infos (self,file):
        size = self.get_file_size(file)
        location = self.get_target_file(file)
        type = self.get_file_type
        permissions = self.get_file_permissions(file)
        return (size,permissions,type,location)

    def get_file_size (self,file):
#        if os.path.isfile (file) or os.path.isdir (file):
#            regexp_size =  compile("(\d+)\s+")
#            output = self.common_tools.execute("du"," -sL '" + file+"'")
#
#            for value in output:
#                size_match = regexp_size.match(value)
#                if size_match != None:
#                    return_size = int(size_match.group(0))
#                    return return_size
        info = gnomevfs.get_file_info(file)
        if info.type == gnomevfs.FILE_TYPE_SYMBOLIC_LINK:
            target_info = gnomevfs.get_file_info(info.symlink_name)
            return target_info.size
        elif info.type == gnomevfs.FILE_TYPE_DIRECTORY:
            return info.size

    def get_file_type (self,file):
        info = gnomevfs.get_file_info(file)
        if info.type == gnomevfs.FILE_TYPE_SYMBOLIC_LINK:
            target_info = gnomevfs.get_file_info(info.symlink_name)
            if target_info.type == gnomevfs.FILE_TYPE_REGULAR:
                return "file"
        elif info.type == gnomevfs.FILE_TYPE_DIRECTORY:
            return "directory"

    def get_target_file (self,file):
        info = gnomevfs.get_file_info(file)
        try:
            target = info.symlink_name
        except ValueError:
            target = ""
        return target

    def get_file_permissions (self,url):
        try:
            info = gnomevfs.get_file_info(url)
            info.symlink_name
            target_info = gnomevfs.get_file_info(info.symlink_name)
            return oct(target_info.permissions)
        except ValueError:
            return ""

    def get_url_pattern (self):
        return "(/.*/)(.*)"

    def cp (self,source_url_in_fs,dest_url,window=None):
        if (os.path.isfile (source_url_in_fs) or os.path.isdir (source_url_in_fs)) and (os.path.isfile(dest_url) or os.path.isdir(dest_url)):
            output = self.common_tools.execute("cp"," -rfsv '" + source_url_in_fs + "' '"+ dest_url + "' ",window)
            return 1
        else:
            return 0

    def mv(self,source,dest):
        self.common_tools.execute ("mv", "'"+source+"' " +"'"+dest+"'")
        return

    def ls (self,dir):
        return os.listdir(dir)

    def mkdir (self,dirname, location):
        os.mkdir (os.path.join (location,dirname))

    def rm (self,url):
        if os.path.isfile (url):
            os.remove (url)
            return 1
        elif os.path.isdir (url):
            shutil.rmtree(url)
            return 1
        else:
            return 0

