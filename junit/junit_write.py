#!/bin/python

from string import Template

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
                     "vcscheckout", "vcsadd", "vcsrevert", "vcscommit",\
                     "get",\
                     "checkmodifiedflag"}
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
    create_stub=Template('''$prologue   
    Object o$Name = getGenenric$Type($args);
    $options
    long $ID = m_oPersisitenceSession.createObject(o$Name);
    try
    \{'''.format(prologue=prologue, Name=Name, Type=Type, args=args, ID=target.ID, options=options)
    delete_stub='''
    \}
    finally
    \{
    m_oPersistenceSession.deleteObjectByID("{type}", {ID});
    \}
    '''.format(type=Type.lower(), ID=target.ID)
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
        self.action=globals()[self.cmd_type+"_cmd"](args[1:])
    #@indent    
    def __call__(self):
        print self.action
    def print_command(self):
        pass

def create_cmd(args):
    target  = test_object(args)
    create_stack.append(target)
    return  generate_stub(target, "create")

        
def done_cmd(args):
    while not len(create_stack)==0:
        cmd = create_stack.pop()
        return generate_stub(cmd, "delete")
        
def move_cmd(args):
    target = test_object_map[args[0]]
    new_location = test_object_map[args[1]]
    target.attributes['ParentID'] = new_location.ID
    return  "m_oPersistenceSession.moveObjectByID(\""+target.o_type.lower()+\
    "\", "+target.ID+", "+new_location.ID+");"

def copy_cmd(args):
    target = test_object_map[args[0]]
    new_location = test_object_map[args[1]]
    new_name = test_object([args[2]])
    new_name.attributes = target.attributes;
    new_name.attributes['ParentID'] = new_location.ID
    create_stack.append(new_name);
    return "long "+new_name.ID+" = m_oPersistenceSession.copyObjectByID(\""+target.o_type.lower()+\
    "\", "+target.ID+", "+new_location.ID+", \""+target.name+"Copy\");"+\
    "try\n{"
    
def delete_cmd(args):
    target = test_object_map[ags[0]]
    return "m_oPersistenceSession.deleteObjectByID(\""+target.o_type.lower()+\
        "\", "+target.ID+");"

def vcscheckout_cmd(args):
    folder = test_object_map[args[0]]
    vcsrepo = test_object_map[args[1]]
    test_object(['Composition=1', 'ParentID='+folder.ID, 'jName="SoastaComp"'])
    test_object(["Target=1", "ParentID="+folder.ID, 'jName="soasta"'])
    test_object(["MessageClip=1", "ParentID="+folder.ID, 'jName="Clip for Soasta"'])
    return " m_oPersistenceSession.vcsCheckOut("+folder.ID +\
        ", "+ vcsrepo.ID+", null);"

    
def vcsadd_cmd(args):
    Id_array = "new long[] {"+(", ").join([test_object_map[item].ID for item in args])+"}"
    return "m_oPersistenceSession.vcsAdd("+Id_array+");"
    

def vcsrevert_cmd(args):
    Id_array = "new long[] {"+(", ").join([test_object_map[item].ID for item in args])+"}"
    return "m_oPersistenceSession.vcsRevert("+Id_array+");"

def vcscommit_cmd(args):
    Id_array = "new long[] {"+(", ").join([test_object_map[item].ID for item in args])+"}"
    return "m_oPersistenceSession.vcsCommit("+Id_array+",\"commit message\");"

    
def get_cmd(args):
    options_begin=""
    options_end=""
    [target, new_name] = args[0].split('=')
    target = test_object_map[target]
    [find_flag, identifier] = args[1].split('=')
    [opt, value] = args[2].split('=')
    if opt.lower()=='listid' and value.lower()=='true':
        options_end = options_end +\
                      "long "+target.ID+" = o"+target.name+".getId();"
    if new_name=="":
        isNew = ""
    else:
        test_object_map[new_name]=target
        isNew="Object "

    if find_flag.lower()=="id":
        method="getObjectByID("
        args="\""+target.o_type.lower()+"\", "+target.ID+");"
    elif find_flag.lower()=="path":
        path="str"+identifier+"Path"
        options_begin= "String "+path+" = Folders.mergePathAndBaseName(o"+identifier+".getPath(), o"+identifier+".getName());"
        method="getObjectByName("
        args="\""+target.o_type.lower()+"\", "+path+", "+target.attributes['jName']+");"
    return options_begin + isNew+"o"+target.name+" = m_oPersistenceSession."+method+args  + options_end

def checkmodifiedflag_cmd(args):
    target=test_object_map[args[0]]
    action = 'checkModifiedFlag("{type}", ID);'.format(type=target.o_type, ID=target.ID)
    return action;

    
# main routine is here
with open('command_file') as f:
    for line in f:
        line = line.rstrip()
        if not line[0]=="#":
            cmd=command(line.split(' '))
            cmd()

    
    
    
