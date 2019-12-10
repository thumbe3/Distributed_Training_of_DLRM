import glob
import pandas as pd
import os
import sys

def generate_csv(file_list, output_directory):
    for file in file_list:
        data = open(file)
        buffer = []
        for line in data.readlines():
            if line.startswith('|') and not 'ID' in line:
                elements = line.strip().split('|')
                final_elements = [x.strip() for x in elements if len(x)>=1]
                if len(final_elements)>3:
                    continue
                buffer.append(final_elements)
        df = pd.DataFrame(buffer,columns = ['GPU_ID', 'GPU_Usage', 'GPU_Memory_Usage'])
        namesplit = file.split(os.sep)
        csv_name = namesplit[-1][0:-4] + '.csv'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        df.to_csv(os.path.join(output_directory,csv_name), index=False)

if __name__=="__main__":
    directory = sys.argv[1]
    output_directory = sys.argv[2]
    file_list  = glob.glob(directory + '/*.out')
    generate_csv(file_list, output_directory)
