import cot_validator
import argparse
import os
import sys

def match_provided_files(xml, xml_file, files_path):
    for file in os.listdir(files_path):
        if xml_file != file:
            file_path = os.path.join(files_path, file)
            try:
                with open(file_path, 'r') as f:
                    contents = f.read()
                if contents == xml:
                    return file
            except:
                break
           
    return 'None'


def main(args):
    project_path = args.project_path
    files_path = os.path.join(project_path, 'vipr/outputs/')
    results_list = []
    for file in os.listdir(files_path):
        if file[0:5] == 'vipr-':
            file_path = os.path.join(project_path, 'vipr/outputs/', file)
            with open(file_path) as f:
                xml = f.readlines()[0]
                results_list.append([file, cot_validator.validate_xml(xml), xml, match_provided_files(xml, file, files_path)])
                

    results_path = os.path.join(project_path, 'vipr/outputs/', 'File_Validation_Results.txt')
    with open(results_path, 'w') as f:
        for result in results_list:
            f.write('File: ' + result[0] + '\n')
            f.write('Valid CoT: ' + str(result[1]) + '\n')
            f.write('XML: ' + result[2] + '\n')
            f.write('Matched File: ', result[3])
            f.write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_path", help="Path to project in container")
    try:
        args = parser.parse_args()
    except:
        sys.exit(2)
    main(args)