import matplotlib.pyplot as plt
import glob
import pandas as pd
import os
import sys

def get_train_test_stats(file_list, output_directory):
    for file in file_list:
        data = open(file)
        buffer = []
        test = []
        break_data = []
        for line in data.readlines():
            if line.startswith('Finished training it'):
                elements = line.strip().split(',')
                final_elements = []
                for item in elements:
                    if 'accuracy' in item or 'loss' in item:
                        item = item.split()[1]
                        final_elements.append(item)
                    elif 'ms/it' in item:
                        item = item.split()[0]
                        final_elements.append(item)
                if len(final_elements)>3:
                    continue
                buffer.append(final_elements)
            elif line.startswith('Testing at'):
                testelements = line.strip().split(',')
                testelements = testelements[1:]
                final_test = []
                for item in testelements:
                    if 'accuracy' in item or 'loss' in item or 'best' in item:
                        value = item.split()[1]
                        final_test.append(value)
                if len(final_test)!=3:
                    continue
                test.append(final_test)
            elif line.startswith('DLRM'):
                breakelements = line.strip().split(',')
                final_break = []
                for item in breakelements:
                    value = item.split()[1]
                    final_break.append(value)
                if len(final_break)!=5:
                    continue
                break_data.append(final_break)
        train_df = pd.DataFrame(buffer,columns = ['ms/it', 'Loss', 'Accuracy'])
        test_df = pd.DataFrame(test, columns = ['loss', 'accuracy', 'best'])
        break_df = pd.DataFrame(break_data, columns = ['DLRM_WRAP', 'loss_fn_time', 'Backward_pass_time', 'Average_Grad_time', 'Optimizer_step_time'])
        namesplit = file.split(os.sep)
        csv_name = namesplit[-1][0:-4] + '.csv'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        train_df.to_csv(os.path.join(output_directory,'train_stats_' + csv_name), index=False)
        test_df.to_csv(os.path.join(output_directory,'test_stats_' + csv_name), index=False)
        break_df.to_csv(os.path.join(output_directory,'break_stats_' + csv_name), index=False)
        for col in test_df.columns:
            test_df[col] = test_df[col].astype(float)
        for col in train_df.columns:
            train_df[col] = train_df[col].astype(float)

        if len(test_df)>1:
            plt.figure()
            train_df['Accuracy'].plot.line(title='Accuracy' + namesplit[-1][0:-4], legend=True)
            plt.xlabel('Time')
            plt.ylabel('Train Accuracy')
            train_figure = 'train_figure' + namesplit[-1][0:-4] +'.png'
            plt.savefig(os.path.join(output_directory,train_figure))
            plt.close()
        if len(test_df)>1:
            plt.figure()
            test_df['accuracy'].plot.line(title='Accuracy' + namesplit[-1][0:-4], legend=True)
            plt.xlabel('Time')
            plt.ylabel('Test Accuracy')
            test_figure = 'test_figure' + namesplit[-1][0:-4] +'.png'
            plt.savefig(os.path.join(output_directory,test_figure))
            plt.close()

if __name__=="__main__":
    directory = sys.argv[1]
    output_directory = sys.argv[2]
    file_list  = glob.glob(directory + '/*.out')
    get_train_test_stats(file_list, output_directory)
