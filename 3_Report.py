import streamlit as st 
import pandas as pd
from Home import face_rec
st.set_page_config(page_title='Reporting',layout='wide')
st.subheader('Reporting')


name = 'attendance:logs'
def load_logs(name,end=-1):
    logs_list = face_rec.r.lrange(name,start=0,end=end) 
    return logs_list


tab1,tab2,tab3 =st.tabs(['Registered Users','Logs','Attendance Report']);

with tab1:
    if st.button('Refresh Data'):
        with st.spinner("Retriving data from Database"):
            redis_face_db = face_rec.retrive_data(name='academy:register')
            st.dataframe(redis_face_db[['Name','Role']])


with tab2:
    if st.button('Refresh Logs'):
        st.write(load_logs(name=name))


with tab3:
    st.subheader('Attendance Report')
    logs_list = load_logs(name=name)
    

    covert_byte_to_string = lambda x: x.decode('utf-8')
    logs_list_string = list(map(covert_byte_to_string,logs_list))

    split_string = lambda x: x.split('@')
    logs_nested_list = list(map(split_string,logs_list_string))

    logs_df = pd.DataFrame(logs_nested_list,columns=['Name','Role','Time'])
    
    logs_df['Time'] = pd.to_datetime(logs_df['Time'])
    logs_df['Date']= logs_df['Time'].dt.date


    report_df = logs_df.groupby(by=['Date','Name','Role']).agg(
        In_Time = pd.NamedAgg('Time','min'),
         Out_Time = pd.NamedAgg('Time','max')
    ).reset_index()


    report_df['In_Time'] = pd.to_datetime(report_df['In_Time'])
    report_df['Out_Time'] = pd.to_datetime(report_df['Out_Time'])
    report_df['Duration']=  report_df['Out_Time']-report_df['In_Time'] 

  

    all_dates = report_df['Date'].unique()
    name_role = report_df[['Name','Role']].drop_duplicates().values.tolist()

    date_name_role_zip = []
    for dt in all_dates:
        for name,role in name_role:
            date_name_role_zip.append([dt,name,role])

    date_name_role_zip_df = pd.DataFrame(date_name_role_zip,columns=['Date','Name','Role'])

    
    date_name_role_zip_df = pd.merge(date_name_role_zip_df,report_df,how='left',on=['Date','Name','Role'])

    
  

    date_name_role_zip_df['Duration_seconds'] = date_name_role_zip_df['Duration'].dt.seconds

    date_name_role_zip_df['Duration_hours'] = date_name_role_zip_df['Duration_seconds']/(60*60)


    def status_marker(x):

        if pd.Series(x).isnull().all():
            return 'Absent'
        elif x >= 0 and x < 1:
             return 'Absent'
        else:
            return 'Present'

    date_name_role_zip_df['Status'] =date_name_role_zip_df['Duration_hours'].apply(status_marker)

    st.dataframe(date_name_role_zip_df)

