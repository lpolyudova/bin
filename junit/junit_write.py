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
allowed_commands = { "create", "delete", "move", "copy", "rename", "done"}


def capitalize(string):
    return string[0].upper()+string[1:].lower()


def generate_stub(target, create_flag):
    Name = target.name
    Type = target.o_type.capitalize()
    prologue=""
    args=""
    options=""
    for attr in target.attributes.keys():
        value = target.attributes[attr]
        value_obj = test_object_map[value];
        options = "o"+Name+".set"+attr+"("+value_obj.ID+");\n"
    create_stub=prologue+\
    "Object o"+Name+" = getGeneric"+Type+"("+args+");\n"+\
    options+\
    "long l"+Name+"ID = m_oPersistenceSession.createObject(o"+Name+");\n"+\
    "try\n {"
    delete_stub="}\n finally\n {"+\
    "m_oPersistenceSession.deleteObjectByID("+Type.lower()+", l"+Name+"ID);\n"+\
    "}"
    if create_flag=="create":
        return create_stub
    elif create_flag=="delete":
        return delete_stub

test_object_map = {}
class test_object(object):
    def __init__(self,args):
        print args
        self.attributes = list()
        [o_type, quant] = args[0].split('=')
        args = args[1:]
        self.name = o_type.capitalize()+quant
        self.o_type=o_type.lower()
        self.ID = "l"+self.name+"ID";
        for arg in args:
            [attr, value] = arg.split('=')
            self.attributes[attr] = value
        test_object_map[self.name]=self

    
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
    target.attribtues['ParentID'] = new_location.ID
    print "m_oPersistenceSession.moveObjectByID(\""+target.o_type+\
    "\", "+target.ID+", "+new_location.ID+");\n"

def copy_cmd(args):
    target = test_object_map[args[0]]
    new_location = test_object_map[args[1]]
    new_name = test_object([args[2]])
    new_name.attributes = target.attributes;
    new_name.attributes['ParentID'] = new_location.ID
    create_stack.append(new_name);
    print "long "+new_name.ID+" = m_oPersistenceSession.copyObjectByID(\""+target.o_type+\
    "\", "+target.ID+", "+new_location.ID+", \""+target.name+"Copy\");\n"+\
    "try\n{"
    
def delete_cmd(args):
    target = test_object_map[ags[0]]
    print "m_oPersistenceSession.deleteObjectByID(\""+target.o_type+\
        "\", "+target.ID+");\n"

with open('command_file') as f:
    for line in f:
        line = line.rstrip()
        command(line.split(' '))
        

    
    
    
