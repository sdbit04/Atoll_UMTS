import os
import xml.etree.ElementTree as et
import inspect
import logging
import datetime


def create_custom_logger(log_level):
    my_logger = logging.getLogger(inspect.stack()[1][3])
    my_logger.setLevel(logging.INFO)

    log_path = os.path.dirname(os.path.abspath(__file__))
    log_file = "atoll_xml_converter{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d"))
    file_handler = logging.FileHandler(os.path.join(log_path, log_file))
    file_handler.setLevel(log_level)

    log_format = logging.Formatter('%(asctime)-15s %(name)s %(message)s')
    file_handler.setFormatter(log_format)

    my_logger.addHandler(file_handler)

    return my_logger


class AtollXmlConverter(object):
    logger_name = create_custom_logger(logging.DEBUG)

    @classmethod
    def replace_field_name(cls, OrigNew_dict, xml_path_in, xml_path_out):
        cls.logger_name.info("Start replacing fields")
        #cls represent this class
        with open(xml_path_in, "r") as file:
            serial = file.read()
            for key in OrigNew_dict.keys():
                serial = serial.replace(key, OrigNew_dict.get(key)) # This return a string that need to be stored
        with open(xml_path_out, "w") as file_out:
            file_out.write(serial)

    @classmethod
    def revert_field_name(cls, NewOrig_dict, xml_path_in, xml_path_out):
        logger_name = create_custom_logger(logging.DEBUG)
        logger_name.info("Start revert fields")
        with open(xml_path_in, "r") as file:
            serial = file.read()
            for key in NewOrig_dict.keys():
                serial = serial.replace(key, NewOrig_dict.get(key)) # This return a string that need to be stored
        with open(xml_path_out, "w") as file_out:
            file_out.write(serial)

    @classmethod
    def derive_family_from_name(cls, name=" "):
        cls.logger_name.info("Deriving Family for each profile {}".format(name))
        name_split = name.split("_")
        new_family = ""
        if name_split[-1] == "GSM":
            if len(str(name_split[-2])) == 2:
                new_family = name[0:-7]
            else:
                new_family = name
        elif len(str(name_split[-1])) == 2:
            if name_split[-1].isnumeric():
                new_family = name[0:-3]
            elif str(name_split[-1])[-2] == "-":
                new_family = name[0:-3]
        elif len(str(name_split[-1])) == 3:
            if str(name_split[-1])[-1] == "T":
                new_family = name[0:-4]
            elif str(name_split[-1])[-3] == "-":
                new_family = name[0:-4]
            else:
                new_family = name
        else:
            new_family = name
        return new_family

    @classmethod
    def beautify_family_attr(cls, origReplacement, replacementOrig, xml_dir_in, xml_dir_out):
        cls.logger_name.info("Enhancing the Family value")
        _xml_dir_in = xml_dir_in
        _xml_dir_out = xml_dir_out
        _xml_path_in = os.path.realpath(os.path.join(_xml_dir_in, "antennas.xml"))
        _xml_path_out = os.path.realpath(os.path.join(_xml_dir_out, "antennas.xml"))
        _xml_path_out_tmp = os.path.realpath(os.path.join(_xml_dir_out, "antennas_tmp.xml"))

        cls.replace_field_name(origReplacement, _xml_path_in, _xml_path_out_tmp)
        xml_tree_object = et.parse(_xml_path_out_tmp)
        data = xml_tree_object.find("rs_data/rs_insert")    # Find immediate parent node
        rows = data.findall('z_row')    # File all child rows under the data node
        antenna_n_family = {}

        for row in rows:
            name = str(row.get("NAME"))
            family_new = cls.derive_family_from_name(name)
            row.set("FAMILY", family_new)
            antenna_n_family[row.get("NAME")] = row.get("FAMILY") # Adding KV pair into directory
        xml_tree_object.write(_xml_path_out_tmp)  # TODO: Changed path to the temp output antennas.xml
        cls.revert_field_name(replacementOrig, _xml_path_out_tmp, _xml_path_out) # TODO: at this step we create exact output we need
        return antenna_n_family

    @classmethod
    def create_profile_translator(cls, xml_dir_in, xml_dir_out, antenna_n_family_dir):
        cls.logger_name.info("Creating profile translator")
        _xml_dir_in = xml_dir_in
        _xml_dir_out = xml_dir_out
        profiletranslator_path_out = os.path.realpath(os.path.join(_xml_dir_out, "PROFILESTRANSLATOR03.txt"))
        antenna_n_family = antenna_n_family_dir
        antenna_k = antenna_n_family.keys()
        utransmitter_file = os.path.realpath(os.path.join(_xml_dir_in, "utransmitters.xml"))
        utransmitter_file_out = os.path.realpath(os.path.join(_xml_dir_out, "utransmitters_tmp.xml"))
        with open(profiletranslator_path_out, 'w') as profiletranslator:
            print("Name\tMatch", file=profiletranslator)
        utransmitter_fields = {"rs:data": "rsdata", "z:row": "zrow"}
        cls.replace_field_name(utransmitter_fields, utransmitter_file, utransmitter_file_out)
        utransmitter_tree = et.parse(utransmitter_file_out)
        rows = utransmitter_tree.findall("rsdata/zrow")
        uniq_antennas = set()
        for row in rows:
            uniq_antennas.add(row.get("ANTENNA_NAME"))

        with open(profiletranslator_path_out, 'a') as profiletranslator:
            for antenna in uniq_antennas:
                if antenna in antenna_k:
                    print("{}\t{}/{}".format(antenna, antenna_n_family[antenna], antenna), file=profiletranslator)

    @classmethod
    def copy_required_files(cls, in_dir, out_dir=""):
        cls.logger_name.info("Coping files")
        excluded_files = os.path.join(out_dir, "excluded_list.tmp")
        with open(excluded_files, 'w') as excluded:
            excluded.write("antennas.xml\nPROFILESTRANSLATOR03.txt")
        # Created the excluded list above, used the file at below
        os.system("xcopy {}\*.* {} /y /d /exclude:{}".format(in_dir, out_dir, excluded_files))
        os.system("del {0}\*.tmp, {0}\*_tmp.xml".format(out_dir))

