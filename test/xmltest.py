import xml.dom.minidom
import xml.dom
import sys
import string
from xml.xpath import Evaluate
from xml.dom.ext.reader import PyExpat
import gnomevfs

class UnicodeStdoutWriter:
    def write(self, data): 
        sys.stdout.write(data.encode('utf-8')) 


class xmlfs:
    doc = None
    common_tools =None
    
    def __init__ (self,base_dir,common_tools):
        self.doc = xml.dom.minidom.parseString("""<file type="directory" name="""+'"'+base_dir+'"'+""" location="" session="0"></file>""")
        self.common_tools = common_tools
        
    def __explore_dir (self,folder,dest_node):
        try:
            total_size = 0
            for file in gnomevfs.open_directory(folder):  
                if file.name == "." or file.name == "..":
                    continue
                
                if file.type == gnomevfs.FILE_TYPE_REGULAR:
                    node = self.__create_file_node (file.name,folder+"/"+file.name,"0","file",str(file.size))
                    dest_node.appendChild(node)
                    total_size += file.size
                
                elif file.type == gnomevfs.FILE_TYPE_DIRECTORY:
                    node = self.__create_file_node (file.name,"","0","directory","0")
                    dest_node.appendChild(node)
                    self.__explore_dir (folder+"/"+file.name,node)
                    total_size += int(node.getAttribute ("size"))
            dest_node.setAttribute("size",str(total_size))
            return
        except gnomevfs.AccessDeniedError,err:
            return
        
        
    def __create_file_node (self,filename,url,session_num,file_type,size):
         node = self.doc.createElement("file")
         node.setAttribute ("type",file_type)
         node.setAttribute ("name",filename)
         node.setAttribute ("location",url)
         node.setAttribute ("session",session_num)
         node.setAttribute ("size",size)
         
         return node
    
    def __get_filenode (self,url):
        exploded_url = url.split("/")
        xpath_query = "/"
        for dir_name in exploded_url:
            xpath_query += "file[@name='"+dir_name+"']/"
        
        print xpath_query
        xpath_query = xpath_query[0:-1]
        des_file_elem = Evaluate(xpath_query,self.doc)
        
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
    
    def get_file_size (self,file):
        node = self.__get_filenode(file)
        file_size = node[0].getAttribute("size")
        return int(file_size)
        
    def cp (self,source_url_in_fs,dest_url):
        file_info = gnomevfs.get_file_info(source_url_in_fs)
        
        dest_dir_elem = self.__get_filenode (dest_url)
        if file_info.type == gnomevfs.FILE_TYPE_DIRECTORY:
            self.__explore_dir (source_url_in_fs,dest_dir_elem[0])
       
        elif file_info.type == gnomevfs.FILE_TYPE_REGULAR:
            source_url_splitted = source_url_in_fs.split("/")
            new_node = self.__create_file_node (source_url_splitted[-1],source_url_in_fs,"0","file",str(file_info.size))
            dest_dir_elem[0].appendChild(new_node)
    
    def mv (self,source_url,dest_url):
        source_node = self.__get_filenode (source_url)
        source_node_daddy = source_node.parentNode
        dest_node = self.__get_filenode (dest_url)
        dest_node.appendChild (source_node)
        source_node_daddy.removeChild(source_node)
            
    def ls(self,dir):
        node_to_list = self.__get_filenode (dir)
        file_list = []
        
        for node in node_to_list[0].childNodes:
            file_list.append ([node.getAttribute("name"),node.getAttribute("location")])
        
        return file_list
    
    def mkdir (self,dirname, location):
        des_dir_elem = self.__get_filenode (location)
        new_dir_elem = self.__create_file_node (dirname,"","0","directory")
        des_dir_elem[0].appendChild(new_dir_elem)
    
    def rm (self,url):
        des_dir_elem = self.__get_filenode (url)
        parent = des_dir_elem[0].parentNode
        parent.removeChild (des_dir_elem[0])
        
        
xmlfs_obj = xmlfs("compilation",None)
xmlfs_obj.cp ("/home/julie","compilation")

print xmlfs_obj.doc.toprettyxml(indent='\t',newl='\n')
files = xmlfs_obj.ls("compilation")
for file in files:
    print file[0]

print xmlfs_obj.get_file_size ("compilation/.java")
#node = nodes[0]
#print node.getAttribute ("location")
#try:
#    while node!= None:
#        node = node.parentNode
#        print node.getAttribute ("location")
#except AttributeError,err:
#    pass