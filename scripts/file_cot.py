import cot_validator
import argparse
import os

def main(args):
    project_path = args.project_path
    files_path = os.path.join(project_path, '/vipr/outputs/')
    for file in os.listdir(files_path):
        if file[0:4] == 'vipr-':
            

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_path", help="Path to project in container")
    try:
        args = parser.parse_args()
    except:
        sys.exit(2)
    main(args)