import glob
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt

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
        png_name = namesplit[-1][0:-4] + '.png'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        df.to_csv(os.path.join(output_directory,csv_name), index=False)
        df_new=[]
        df_new.append(df[df['GPU_ID']=='0'])
        df_new.append(df[df['GPU_ID']=='1'])
        df_new.append(df[df['GPU_ID']=='2'])
        plt.figure() 
        for id_gpu, frame in enumerate(df_new):
            frame['GPU_Usage'] = frame['GPU_Usage'].map(lambda x: x.strip('%')).astype('float')
            frame['GPU_Memory_Usage'] = frame['GPU_Memory_Usage'].map(lambda x: x.strip('%')).astype('float')

            frame.apply(pd.to_numeric)
            print(frame.head)
            plt.plot(frame['GPU_Usage'],label=str(id_gpu))
        print(png_name)
        plt.legend()
        plt.savefig(os.path.join(output_directory,png_name))
        print("Plotted")


if __name__=="__main__":
    directory = sys.argv[1]
    output_directory = sys.argv[2]
    file_list  = glob.glob(directory + '/*.out')
    generate_csv(file_list, output_directory)
