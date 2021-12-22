from lxml import etree as ET
import os
import re

def validate_xml(xml):
    xml = re.sub(r'(encoding=)[\'" ]\S*[\'" ]', '', xml)

    xml_root = ET.fromstring(xml)
    if required_present(xml_root):
        if elements_under_detail(xml_root):
            return True


    return False


def get_value_type(value):
    from dateutil import parser

    try:
        value = int(value)
        value_type = "int"

    except:
        try:
            value = float(value)
            value_type = 'decimal'
        except:
            try:
                value = parser.isoparse(value)
                value_type = 'dateTime'
            except:
                value = str(value)
                value_type = 'string'

    return value_type

def required_present(xml_root):
    ev_attr = dict(xml_root.attrib)
    children = xml_root.getchildren()
    for child in children:
        if child.tag == 'point':
            pt_attr = dict(child.attrib)

    for k, v in ev_attr.items():
        v_t = get_value_type(v)
        ev_attr[k] = [v, v_t]

    for k, v in pt_attr.items():
        v_t = get_value_type(v)
        pt_attr[k] = [v, v_t]
    
    req_ev_attr = {'version':'decimal','type':'string','uid':'string','time':'dateTime','start':'dateTime','stale':'dateTime','how':'string'}
    req_pt_attr = {'lat':'decimal','lon':'decimal','hae':'decimal','ce':'decimal','le':'decimal'}
    
    #Ensure req event attr are present
    if (req_attr in ev_attr for req_attr in req_ev_attr.keys()):
        #Ensure req point attr are present
        if (req_attr in pt_attr for req_attr in req_pt_attr.keys()):
            #Validate data types in event
            for r_k, r_t in req_ev_attr.items():
                for k, v in ev_attr.items():
                    if r_k == k:
                        if v[1] != r_t:
                            return False
            #Validate data types in point
            for r_k, r_t in req_pt_attr.items():
                for k, v in pt_attr.items():
                    if r_k == k:
                        if v[1] != r_t:
                            return False
        else:
            return False
    else:
        return False

    #Need to check a few attr fit specific patterns
    for k, v in ev_attr.items():
        if k == 'version':
            if v[0] != '2.0':
                return False
        if k == 'type':
            if re.match(r'\w+(-\w+)*(;[^;]*)?', v[0]) == None:
                return False
        if k == 'how':
            if re.match(r'\w-\w', v[0]) == None:
                return False
    
    for k, v in pt_attr.items():
        if k == 'lat':
            if 90 <= float(v[0]) <= -90:
                return False
        if k == 'lon':
            if 180 <= float(v[0]) <= -180:
                return False
    
    return True


def elements_under_detail(xml_root):
    #Ensure the only direct subelements of event are point and detail
    event_sub_elements = []
    point_sub_elements = []
    children = xml_root.getchildren()
    for child in children:
        if (child.tag) == 'point':
            try:
                pt_children = child.getChildren()
                return False
            except:
                pass
        event_sub_elements.append(child.tag)

    if event_sub_elements == ['point','detail'] or event_sub_elements == ['detail', 'point']:
        if point_sub_elements == []:
            return True
    else:
        return False

def main():
    complete_files_list = []
    out_folder = "/vipr/CoT-out"
    while True:
        for file in os.listdir(out_folder):
            if file != '.gitkeep':
                if not file in complete_files_list:
                    file_path = os.path.join(out_folder, file)
                    with open(file_path) as f:
                        xml = f.readlines()
                    if validate_xml(xml[0]):
                        print('Validated CoT Message: ', file)
                    else:
                        print('CoT Message Invalid: ', file)
                complete_files_list.append(file)

if __name__ == "__main__":
    main()