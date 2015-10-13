#!/bin/python

"""
names are of format type+quantifier

Syntax for commands:
create <type> <quantifier> 
delete <name>

move <name_target> <name_new_parent>
copy <name_copy_target> <name_clone> <name_new_parent>



general flow:
<cmd> <name> <other args>
read line -> g
"""


create_stack = list()
allowed_commands = { "create", "delete", "move", "copy", "rename", "done",\
                     "vcscheckout", "vcsadd", "vcsrevert",\
                     "get"}
ID_to_obj = {}

def get_prologue(type):
    prologue = ""
    if type=="vcsrepository":
        prologue="String oGitFolderPath = getGitRepoPath();\n"
    return prologue

def get_args(test_object_a):
    args=""
    if test_object_a.o_type.lower()=="vcsrepository":
        args = "oGitFolderPath";
    return args

def capitalize(string):
    return string[0].upper()+string[1:].lower()


def generate_stub(target, create_flag):
    Name = target.name
    Type = target.o_type
    prologue=get_prologue(Type.lower())
    args=get_args(target)
    options=""
    for attr in target.attributes.keys():
        value = target.attributes[attr]
        value_obj = ID_to_obj[value];
        options = "o"+Name+".set"+attr+"("+value_obj.ID+");\n"
    create_stub=prologue+\
    "Object o"+Name+" = getGeneric"+Type+"("+args+");\n"+\
    options+\
    "long l"+Name+"ID = m_oPersistenceSession.createObject(o"+Name+");\n"+\
    "try\n {"
    delete_stub="}\n finally\n {"+\
    "m_oPersistenceSession.deleteObjectByID(\""+Type.lower()+"\", l"+Name+"ID);\n"+\
    "}"
    if create_flag=="create":
        return create_stub
    elif create_flag=="delete":
        return delete_stub

test_object_map = {}
class test_object(object):
    def __init__(self,args):
        self.attributes = {}
        [o_type, quant] = args[0].split('=')
        args = args[1:]
        self.name = o_type+quant
        self.o_type=o_type
        self.ID = "l"+self.name+"ID";
        for arg in args:
            [attr, value] = arg.split('=')
            self.attributes[attr] = value
        test_object_map[self.name]=self
        ID_to_obj[self.ID]=self
    
class command(object):
    def __init__(self,args):
        self.cmd_type = args[0]
        if not self.cmd_type in allowed_commands:
            print "command not recognized!"
            return 
        globals()[self.cmd_type+"_cmd"](args[1:])
    def print_command(self):
        pass

def create_cmd(args):
    target  = test_object(args)
    create_stack.append(target)
    print generate_stub(target, "create")

        
def done_cmd(args):
    while not len(create_stack)==0:
        cmd = create_stack.pop()
        print generate_stub(cmd, "delete")
        
def move_cmd(args):
    target = test_object_map[args[0]]
    new_location = test_object_map[args[1]]
    target.attributes['ParentID'] = new_location.ID
    print "m_oPersistenceSession.moveObjectByID(\""+target.o_type.lower()+\
    "\", "+target.ID+", "+new_location.ID+");\n"

def copy_cmd(args):
    target = test_object_map[args[0]]
    new_location = test_object_map[args[1]]
    new_name = test_object([args[2]])
    new_name.attributes = target.attributes;
    new_name.attributes['ParentID'] = new_location.ID
    create_stack.append(new_name);
    print "long "+new_name.ID+" = m_oPersistenceSession.copyObjectByID(\""+target.o_type.lower()+\
    "\", "+target.ID+", "+new_location.ID+", \""+target.name+"Copy\");\n"+\
    "try\n{"
    
def delete_cmd(args):
    target = test_object_map[ags[0]]
    print "m_oPersistenceSession.deleteObjectByID(\""+target.o_type.lower()+\
        "\", "+target.ID+");\n"

def vcscheckout_cmd(args):
    folder = test_object_map[args[0]]
    vcsrepo = test_object_map[args[1]]
    print " m_oPersistenceSession.vcsCheckOut("+folder.ID +\
        ", "+ vcsrepo.ID+");\n"
    test_object(['Composition=1', 'ParentID='+folder.ID, 'jName="SoastaComp"'])
    test_object(["Target=1", "ParentID="+folder.ID, 'jName="soasta"'])
    test_object(["MessageClip=1", "ParentID="+folder.ID, 'jName="Clip for Soasta"'])

def vcsadd_cmd(args):
    Id_array = "new long[] {"+(", ").join([test_object_map[item].ID for item in args])+"}"
    print "m_oPersistenceSession.vcsAdd("+Id_array+");\n"
    

def vcsrevert_cmd(args):
    Id_array = "new long[] {"+(", ").join([test_object_map[item].ID for item in args])+"}"
    "m_oPersistenceSession.vcsRevert("+Id_array+");\n"

def get_cmd(args):
    [target, new_name] = args[0].split('=')
    target = test_object_map[target]
    [find_flag, identifier] = args[1].split('=')
    if new_name=="":
        isNew = ""
    else:
        test_object_map[new_name]=target
        isNew="Object "

    if find_flag.lower()=="id":
        method="getObjectByID("
        args="\""+target.o_type.lower()+"\", "+target.ID+");\n"
    elif find_flag.lower()=="path":
        path="str"+identifier+"Path"
        print "String "+path+" = Folders.mergePathAndBaseName(o"+identifier+".getPath(), o"+identifier+".getName());"
        method="getObjectByName("
        args="\""+target.o_type.lower()+"\", "+path+", "+target.attributes['jName']+");\n"
    print isNew+"o"+target.name+" = m_oPersistenceSession."+method+args;
    
# main routine is here
with open('command_file') as f:
    for line in f:
        line = line.rstrip()
        if not line[0]=="#":
            command(line.split(' '))
        

    
    
    
