import os
import xml.etree.ElementTree as et
base_path = os.path.dirname(os.path.realpath(__file__))
xml_dir = os.path.realpath(os.path.join(base_path, "..\\Atoll3G"))
xml_path_in = os.path.realpath(os.path.join(xml_dir, "antennas.xml"))
# Please give a new name if you don't want to replace the existing antennas.xml
xml_path_out = os.path.realpath(os.path.join(xml_dir, "antennas_b.xml"))
profiletranslator_path = os.path.realpath(os.path.join(xml_dir, "PROFILESTRANSLATOR04.txt"))
# replacementOrig = {"zrow": "z:row", "rsdata": "rs:data", "rsinsert": "rs:insert"}
origReplacement = {"CUSTOM_NEMS_ANTENNA_NAME": "FAMILY", "z:row":"z_row","rs:data" :"rs_data","rs:insert" : "rs_insert","rs:nullable":"rs_nullable", "rs:fixedlength":"rs_fixedlength", "s:extends":"s_extends", "s:Schema":"s_Schema", "s:ElementType":"s_ElementType","s:AttributeType":"s_AttributeType","s:datatype":"s_datatype", "rs:updatable":"rs_updatable","dt:type":"dt_type","rs:number":"rs_number","rs:write":"rs_write","dt:maxLength":"dt_maxLength", "rs:precision":"rs_precision","rs:maybenull":"rs_maybenull", "rs:long":"rs_long", "xmlns:s":"xmlns_s", "xmlns:dt":"xmlns_dt","xmlns:rs":"xmlns_rs", "xmlns:z":"xmlns_z"}
    # "xmlns:dt":"xmlns_dt","xmlns:rs":"xmlns_rs","xmlns:s":"xmlns_s", "xmlns:z":"xmlns_z"}
                   #, }
replacementOrig = {"z_row":"z:row","rs_data" :"rs:data","rs_insert" : "rs:insert","rs_nullable":"rs:nullable", "rs_fixedlength":"rs:fixedlength", "s_extends":"s:extends", "s_Schema":"s:Schema", "s_ElementType":"s:ElementType","s_AttributeType":"s:AttributeType","s_datatype":"s:datatype", "rs_updatable":"rs:updatable","dt_type":"dt:type","rs_number":"rs:number","rs_write":"rs:write","dt_maxLength":"dt:maxLength", "rs_precision":"rs:precision","rs_maybenull":"rs:maybenull", "rs_long":"rs:long", "xmlns_s":"xmlns:s", "xmlns_dt":"xmlns:dt","xmlns_rs":"xmlns:rs" ,"xmlns_z":"xmlns:z"}
# origReplacement = {"CUSTOM_NEMS_ANTENNA_NAME": "FAMILY", ":":"_"}


def replace_field_name(OrigNew_dict, xml_path_in, xml_path_out):
    with open(xml_path_in, "r") as file:
        serial = file.read()
        for key in OrigNew_dict.keys():
            serial = serial.replace(key, OrigNew_dict.get(key)) # This return a string that need to be stored
    with open(xml_path_out, "w") as file_out:
        file_out.write(serial)


def revert_field_name(NewOrig_dict, xml_path):
    with open(xml_path, "r") as file:
        serial = file.read()
        for key in NewOrig_dict.keys():
            serial = serial.replace(key, NewOrig_dict.get(key)) # This return a string that need to be stored
    with open(xml_path, "w") as file_out:
        file_out.write(serial)


def beautify_family_attr(xml_path_in, xml_path_out):
    _xml_path_in = xml_path_in
    _xml_path_out = xml_path_out
    replace_field_name(origReplacement, _xml_path_in, _xml_path_out)
    xml_tree_object = et.parse(_xml_path_out)
    data = xml_tree_object.find("rs_data/rs_insert")
    rows = data.findall('z_row')
    antenna_n_family = {}
    for row in rows:
        family_o = str(row.get("FAMILY"))
        # print(type(family_o))
        # print("family_o = {}".format(family_o))
        family_n = family_o.split("(")[0].replace(" ", "_").replace("/", "_").rstrip("_")
        # print("family_n = {}".format(family_n))
        row.set("FAMILY", family_n)
        antenna_n_family[row.get("NAME")] = row.get("FAMILY")
    xml_tree_object.write(_xml_path_out)
    revert_field_name(replacementOrig, _xml_path_out)
    return antenna_n_family


def create_profile_translator(antenna_n_family_dir, profiletranslator_path):
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


if __name__ == "__main__":
    antenna_n_family = beautify_family_attr(xml_path_in, xml_path_out)
    create_profile_translator(antenna_n_family, profiletranslator_path)
