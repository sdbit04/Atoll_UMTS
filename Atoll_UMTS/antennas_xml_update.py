import os
import xml.etree.ElementTree as et

def replace_field_name(OrigNew_dict, xml_path_in, xml_path_out):
    with open(xml_path_in, "r") as file:
        serial = file.read()
        for key in OrigNew_dict.keys():
            serial = serial.replace(key, OrigNew_dict.get(key)) # This return a string that need to be stored
    with open(xml_path_out, "w") as file_out:
        file_out.write(serial)


def revert_field_name(NewOrig_dict, xml_path_in, xml_path_out):
    with open(xml_path_in, "r") as file:
        serial = file.read()
        for key in NewOrig_dict.keys():
            serial = serial.replace(key, NewOrig_dict.get(key)) # This return a string that need to be stored
    with open(xml_path_out, "w") as file_out:
        file_out.write(serial)


def beautify_family_attr(origReplacement, replacementOrig, xml_path_in, xml_path_out):
    _xml_path_in = xml_path_in
    _xml_path_out = xml_path_out
    _xml_path_out_tmp = xml_path_out  # TODO: Need to configure this path
    replace_field_name(origReplacement, _xml_path_in, _xml_path_out_tmp)
    xml_tree_object = et.parse(_xml_path_out_tmp)
    data = xml_tree_object.find("rs_data/rs_insert") # Find immediate parent node
    rows = data.findall('z_row') # File all child rows under the data node
    antenna_n_family = {}
    for row in rows:
        family_old = str(row.get("FAMILY"))
        # print(type(family_o))
        # print("family_o = {}".format(family_o))
        family_new = family_old.split("(")[0].replace(" ", "_").replace("/", "_").rstrip("_")
        # print("family_n = {}".format(family_n))
        row.set("FAMILY", family_new)
        antenna_n_family[row.get("NAME")] = row.get("FAMILY") # Adding KV pair into directory
    xml_tree_object.write(_xml_path_out_tmp)  # TODO: Changed path to the temp output antennas.xml
    revert_field_name(replacementOrig, _xml_path_out_tmp, _xml_path_out) # TODO: at this step we create exact output we need
    return antenna_n_family


def create_profile_translator(xml_dir, antenna_n_family_dir, profiletranslator_path):
    antenna_n_family = antenna_n_family_dir
    antenna_k = antenna_n_family.keys()
    utransmitter_file = os.path.realpath(os.path.join(xml_dir, "utransmitters.xml"))
    utransmitter_file_out = os.path.realpath(os.path.join(xml_dir, "utransmitters_tmp.xml"))
    with open(profiletranslator_path, 'w') as profiletranslator:
        print("Name\tMatch", file=profiletranslator)
    utransmitter_fields = {"rs:data": "rsdata", "z:row": "zrow"}
    replace_field_name(utransmitter_fields, utransmitter_file, utransmitter_file_out)
    utransmitter_tree = et.parse(utransmitter_file_out)
    rows = utransmitter_tree.findall("rsdata/zrow")
    uniq_antennas = set()
    for row in rows:
        uniq_antennas.add(row.get("ANTENNA_NAME"))

    with open(profiletranslator_path, 'a') as profiletranslator:
        for antenna in uniq_antennas:
            if antenna in antenna_k:
                print("{}\t{}/{}".format(antenna, antenna_n_family[antenna], antenna), file=profiletranslator)



