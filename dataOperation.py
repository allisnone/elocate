# -*- coding:utf-8 -*-
import datetime,time,os
import pandas as pd
import fileOperation as fo
import sendMail as sm
"""
ROOT_DIR="/Xperia Z2/内部存储设备/BarScannerExcels/"
FILE_PROFIX="BarScan"
FILE_TPY=".xls"
ROOT_DIR="C:/BarScannerExcels/"
"""

#ROOT_DIR="/storage/emulated/0/BarScannerExcels/"
def get_all_scan_file(given_dir="C:/BarScannerExcels/data/",key_word='BarScan',file_type='.xls'):
    """
        获取特定目录的最新扫描文件名
    """
    """
    :param given_dir: str type, given DIR
    :return: str type, all file name in the given DIR
    """
    all_file_names=[]
    #print(given_dir)
    #print(os.walk(given_dir))
    for root,dirs,allfiles in os.walk(given_dir):
        if root==given_dir:
            for file in allfiles:
                if key_word in file and file_type in file:
                    all_file_names.append(given_dir+file)
    all_file_names=sorted(all_file_names,reverse=True)
    return all_file_names


def get_scan_data(column,given_file_name=None,given_dir="C:/BarScannerExcels/",key_word='BarScan',file_type='.xls'):
    """
        获取需要的更新数据
    """
    """
    :param given_file_name: str type, given file name
    :param given_dir: str type, given DIR
    :return: dataframe type, scanned data
    """
    bar_data_df=pd.DataFrame(data={},columns=column)
    allfiles=get_all_scan_file()
    file_name=''
    if given_file_name:
        file_name=given_file_name
        if '.xls' in file_name:
            file_type='.xls'
        elif '.csv' in file_name:
            file_type = '.csv'
        else:
            pass
    else:
        allfiles=get_all_scan_file(given_dir,key_word,file_type)
        if allfiles:
            file_name=allfiles[0]
        else:
            pass
    if file_name and file_type=='.xls':
        try: 
            raw_bar_data_df=pd.read_excel(file_name,header=0,encoding='gb2312')
            #df_0=pd.read_csv(file_name,names=column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
            #print(file_name)
            bar_data_df=raw_bar_data_df[column]
            #print(bar_data_df)
            bar_data_df=bar_data_df.set_index(' NTAsset')
        except:
            print('file: %s does not exist...' % file_name)
            pass
    elif file_name and file_type=='.csv':
        try: 
            raw_bar_data_df=pd.read_csv(file_name,names=column,header=1,encoding='gb2312')
            #df_0=pd.read_csv(file_name,names=column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
            #print(file_name)
            bar_data_df=raw_bar_data_df[column]
            #bar_data_df=bar_data_df.set_index(' NTAsset')
        except:
            print('file: %s does not exist...' % file_name)
            #pass
    else:
        print('Please put your scanned data to ROOT_DIR: C:/BarScannerExcels/')
    return bar_data_df


def compare_scan_data(new_scan_data,history_bar_data):
    """
    将更新的扫描数据和数据源比较，更新数据源并发送email给asset prime
    """
    """
    :param new_scan_data: dataframe type, scanned data
    :param history_bar_data: dataframe type, rwa data
    :return:  
    """
    update_column_list=[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']
    update_data=pd.DataFrame(data={},columns=update_column_list)
    updated_history_bar_data=update_data
    if new_scan_data.empty or history_bar_data.empty:
        pass
    else:
        #update_barms=new_scan_data[' NTAsset'].values.tolist()
        update_barms=new_scan_data.index.values.tolist()
        #print(history_bar_data.columns.tolist())
        #hist_barms=history_bar_data[' NTAsset'].values.tolist()
        hist_barms=history_bar_data.index.values.tolist()
        update_existing_barms=list(set(update_barms).intersection(set(hist_barms)))
        new_insert_barms=list(set(update_barms).difference(set(update_existing_barms)))
        #history_bar_data=history_bar_data.set_index(' NTAsset')
        #print(history_bar_data)
        #new_scan_data=new_scan_data.set_index(' NTAsset')
        update_data=new_scan_data[new_scan_data.index.isin(update_existing_barms)]
        new_insert_data=new_scan_data[new_scan_data.index.isin(new_insert_barms)]
        if update_existing_barms:
            #update_column_list=['FrameRackPosition']
            update_data=new_scan_data.fillna(-1)
            for bams in update_existing_barms:
                for col in update_column_list:
                    if update_data.at[bams,col] != -1 and history_bar_data.at[bams,col]!=update_data.at[bams,col]:
                        history_bar_data.at[bams,col]=update_data.at[bams,col]
            #history_bar_data=history_bar_data.drop(update_existing_barms)
        #print('history_bar_data: \n',history_bar_data)
        #print('new_insert_data: \n',new_insert_data)
        updated_history_bar_data=pd.concat([history_bar_data,new_insert_data],ignore_index=False)
        #print('updated_history_bar_data \n',updated_history_bar_data)
        updated_history_bar_data=updated_history_bar_data.sort_index()[update_column_list]
        update_data=updated_history_bar_data[updated_history_bar_data.index.isin(update_barms)][update_column_list]
        #print(update_data[[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']])
        #print('Final result:')
        #print(updated_history_bar_data)
        #print('Final affected data:')
        #print(update_data)
    return update_data,updated_history_bar_data

def clear_hist_scan_files(data_dir,temp_dir,max_temp_file=20):
    new_files=get_all_scan_file(given_dir=data_dir)
    all_temp_files=get_all_scan_file(given_dir=temp_dir)
    new_move_files=list(set(new_files).difference(set(all_temp_files)))
    print('Backup scan files to temp dir: ')
    fo.copyFiles(sourceDir=data_dir, targetDir=temp_dir)
    fo.removeFileInFirstDir(targetDir=data_dir)
    new_temp_files=all_temp_files+new_move_files
    new_temp_files=sorted(new_temp_files,reverse=True)
    print('Clear and delete files to temp files.')
    for file in new_temp_files[20:]:
        if os.path.isfile(file): 
            os.remove(file)
    return new_temp_files[:20]

def consolidate_scan_data(scan_dir):
    ROOT_DIR="C:/BarScannerExcels/"
    all_files=get_all_scan_file()
    column_list=[' NTAsset',' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']
    consolidate_bar_data_df=pd.DataFrame(data={},columns=column_list)
    latest_file_name=''
    if all_files:
        latest_file_name=all_files[0]
        print('Lastest scan file name: %s' % all_files[0])
        print('Start to conolidate scan data...')
        if len(all_files)==1:
            consolidate_bar_data_df=get_scan_data(column=column_list,given_file_name=all_files[0])
        else:
            indx=len(all_files)-1
            consolidate_bar_data_df=get_scan_data(column=column_list,given_file_name=all_files[indx])
            while indx>0:
                indx=indx-1
                new_scan_data=get_scan_data(column=column_list,given_file_name=all_files[indx])
                #print(all_files[indx])
                #print(new_scan_data)
                update_data,consolidate_bar_data_df = compare_scan_data(new_scan_data, consolidate_bar_data_df)
        clear_hist_scan_files(data_dir=ROOT_DIR+'data/', temp_dir=ROOT_DIR+'temp/')
    else:
        pass
    return consolidate_bar_data_df

def get_eqm_data():
    eqm_column_list=['Region','Test Organization','Site','Cabinet Position','Owner',
                     'Ericsson SN','BAMS ID','Asset ID','Product No','R-state',
                     'Functional Designation','Manufacturing Day','Position','Comments',
                     'Destination','Borrower','Transferred To','Category',
                     'Free Text Description','Update Date','Update User']
    eqm_data=pd.DataFrame(data={},columns=eqm_column_list)
    eqm_key_work = 'Guangzhou_EQM'
    eqm_file_type = '.csv'
    eqm_file_dir ='C:/BarScannerExcels/eqm/'
    latest_eqm_files = get_all_scan_file(given_dir=eqm_file_dir, key_word=eqm_key_work, file_type=eqm_file_type)
    latest_eqm_file=''
    if latest_eqm_files:
        latest_eqm_file = latest_eqm_files[0]
        eqm_data = get_scan_data(column=eqm_column_list,given_file_name=latest_eqm_file)
    else:
        print('There no EQM data in DIR: %s' % eqm_file_dir)
    #print(eqm_data)
    #print(latest_eqm_file)
    return eqm_data

def update_position_eqm_data(scan_data,raw_eqm_data):
    """
    将更新的扫描数据和数据源比较，更新数据源并发送email给asset prime
    """
    """
    :param new_scan_data: dataframe type, scanned data
    :param history_bar_data: dataframe type, rwa data
    :return:  
    """
    raw_eqm_data_columns = ['Region', 'Test Organization', 'Site', 'Cabinet Position', 'Owner',
                            'Ericsson SN', 'BAMS ID', 'Asset ID', 'Product No', 'R-state',
                            'Functional Designation', 'Manufacturing Day', 'Position', 'Comments',
                            'Destination', 'Borrower', 'Transferred To', 'Category',
                            'Free Text Description', 'Update Date', 'Update User']
    
    update_column_list=[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']
    update_data=pd.DataFrame(data={},columns=update_column_list)
    updated_history_bar_data=update_data
    if scan_data.empty or raw_eqm_data.empty:
        pass
    else:
        #update_barms=new_scan_data[' NTAsset'].values.tolist()
        update_barms=scan_data.index.values.tolist()
        #print(history_bar_data.columns.tolist())
        #hist_barms=history_bar_data[' NTAsset'].values.tolist()
        #raw_eqm_data = raw_eqm_data0
        #hist_barms=raw_eqm_data.index.values.tolist()
        hist_barms=raw_eqm_data['BAMS ID'].values.tolist()
        update_existing_barms=list(set(update_barms).intersection(set(hist_barms)))
        new_insert_barms=list(set(update_barms).difference(set(update_existing_barms)))
        #history_bar_data=history_bar_data.set_index(' NTAsset')
        #print(history_bar_data)
        #new_scan_data=new_scan_data.set_index(' NTAsset')
        update_data=scan_data[scan_data.index.isin(update_existing_barms)]
        new_insert_data=scan_data[scan_data.index.isin(new_insert_barms)]
        raw_eqm_data_temp = raw_eqm_data.set_index('BAMS ID')
        if update_existing_barms:
            #update_column_list=['FrameRackPosition']
            update_data=scan_data.fillna(-1)
            for bams in update_existing_barms:
                #for col in update_column_list:
                if update_data.at[bams,'FrameRackPosition'] != -1 and raw_eqm_data_temp.at[bams,'Cabinet Position']!=update_data.at[bams,'FrameRackPosition']:
                    raw_eqm_data_temp.at[bams,'Cabinet Position']=update_data.at[bams,'FrameRackPosition']
            #history_bar_data=history_bar_data.drop(update_existing_barms)
        print('history_bar_data: \n',raw_eqm_data)
        print('new_insert_data: \n',new_insert_data)
        updated_history_bar_data=pd.concat([raw_eqm_data,new_insert_data],ignore_index=False)
        print('updated_history_bar_data \n',updated_history_bar_data)
        updated_history_bar_data=updated_history_bar_data.sort_index()[update_column_list]
        update_data=updated_history_bar_data[updated_history_bar_data.index.isin(update_barms)][update_column_list]
        #print(update_data[[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']])
        #print('Final result:')
        #print(updated_history_bar_data)
        #print('Final affected data:')
        #print(update_data)
    return update_data,updated_history_bar_data
    

def get_gims_data():
    csv_file_name="C:/BarScannerExcels/GIMs_data.xls"
    raw_bar_data_df=pd.read_excel(csv_file_name,header=0,encoding='gb2312')
    need_columns = ['LABEL_ID', 'PEC', 'SN','NTASSET', 'USERGROUP']
    #print(raw_bar_data_df[need_columns].tail(20))
    #print(raw_bar_data_df.columns.values.tolist())
    return raw_bar_data_df[need_columns]

def update_eqm_sn_from_gims():
    return

if __name__ == "__main__":
    history_bar_data=pd.DataFrame({' NTAsset': ['BAMS-1001068584','BAMS-1001068511','BAMS-1001068512','BAMS-1001068513'],
                                   ' GDNTAsset': ['CO12034450','CO12034451','CO12034452','CO12034453'],
                                   ' SN': ['NNTM000078J0','NNTM000078J1','NNTM000078J2','NNTM000078J3'], 
                                   ' PEC': ['RNC','PP15K','ATCA','SUN T4'],
                                   'FrameRackPosition': ['/CNGN18/Lab/CP00/33','/CNGN18/Lab/CN01/33','/CNGN18/Lab/CN02/33','/CNGN18/Lab/CN04/33'],
                                   ' SiteLocation':['IU','IU','IU','IU']})
    history_bar_data = history_bar_data.set_index(' NTAsset')
    #print('Raw DB data:')
    #raw_db_file_name="C:/BarScannerExcels/hist/CGC_asset.xls"
    #history_bar_data.to_excel(raw_db_file_name)
    eqm_data=get_eqm_data()
    #print(eqm_data.tail(5))
    update_column_list=[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']
    eqm_data['site code'] = '/CNGN18'
    eqm_data[' GDNTAsset'] = eqm_data['BAMS ID']
    eqm_data[' SN'] = eqm_data['Ericsson SN']
    eqm_data[' PEC'] =eqm_data['Product No']
    eqm_data['FrameRackPosition'] = eqm_data['site code'] + eqm_data['Cabinet Position']
    eqm_data[' SiteLocation'] = 'NA'
    #print(eqm_data.columns.values.tolist())
    eqm_data_temp = eqm_data[[' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation']]
    eqm_data_temp = eqm_data_temp.set_index(' GDNTAsset')
    print(eqm_data_temp)
    ROOT_DIR="C:/BarScannerExcels/"
    bar_data_df = consolidate_scan_data(ROOT_DIR+'data/')
    print('Scanning data:')  
    print(bar_data_df)
    update_data,updated_history_bar_data = compare_scan_data(bar_data_df,eqm_data_temp)
    print('Compare new scan data with DB raw data')
    
    #print('updated history data: \n', updated_history_bar_data)
    update_data_file_name = 'C:/BarScannerExcels/temp/updated_scan_data.xls'
    final_db_data_file_name = 'C:/BarScannerExcels/temp/db_data.xls'
    """
    #update_data['site code'] = '/CNGN18'
    update_data['BAMS ID'] = update_data[' GDNTAsset']
    update_data['Ericsson SN'] = update_data[' SN']
    update_data['Product No'] = update_data[' PEC']
    update_data['Cabinet Position'] = update_data['FrameRackPosition']#= eqm_data['site code'] 
    for  column in [' SN', ' PEC','FrameRackPosition',' SiteLocation']:
        del update_data[column]
    """
    update_data = update_data.rename(index=str,columns={' SN':'Ericsson SN', ' PEC': 'Product No','FrameRackPosition': 'Cabinet Position',' SiteLocation':' SiteLocation'})#{' GDNTAsset',' SN', ' PEC','FrameRackPosition',' SiteLocation'})
    
    del update_data[' GDNTAsset']
    del update_data[' SiteLocation']
    update_data['BAMS ID'] = update_data.index
    update_data = update_data.set_index('BAMS ID')
    #print(update_data)
    print('Final data need to update: ')
    print(update_data )
    
    #asset_prime = 'anna.chen@ericsson.com'
    #asset_prime = 'tony.cao@ericsson.com'
    asset_prime = 'jason.g.zhang@ericsson.com'
    #copy_addr='PDLEENGSDG@pdl.internal.ericsson.com'
    #copy_addr = ['jason.g.zhang@ericsson.com','tony.cao@ericsson.com']
    copy_addr = 'jason.g.zhang@ericsson.com'
    bcopy_addr = 'jason.g.zhang@ericsson.com'
    if update_data.empty:
        print("no data need to update")
        pass
    else:
        update_data.to_excel(update_data_file_name)
        print('Scan data write as:  %s' % update_data_file_name)
        updated_history_bar_data.to_excel(final_db_data_file_name)
        print('Final DB data write as:  %s' % final_db_data_file_name)
        """
        sm.send_mail(from_addr='jason.g.zhang@ericsson.com', to_addr='jason.g.zhang@ericsson.com',cc_addr='jason.g.zhang@ericsson.com',
           subjest_content='E-location update', mail_content='Please see the asset update in the attachment', 
           attachment=update_data_file_name)
        """
        sm.send_mail(from_addr='jason.g.zhang@ericsson.com', to_addr=asset_prime,
           subjest_content='E-location update', mail_content='Please see the asset update in the attachment', 
           cc_addr=copy_addr,bcc_addr=bcopy_addr,
           attachment=update_data_file_name)
        #updated_history_bar_data.to_excel()
        print('Send the new scan data to asset prime completed.')


#test()
#consolidate_scan_data()
