#=======================================================================
## 0. Importing libraries and setting up streamlit web app

#Importing the necessary packages
import streamlit as st
import openpyxl
import pygwalker as pyg
import pandas as pd
import sys  # Make sure to import sys for sys.exit() to work properly

#Setting up web app page
st.set_page_config(page_title='EDA in Streamlit', page_icon=None, layout="wide")


#=======================================================================
## 1. File upload

#Creating section in sidebar
st.sidebar.write("****A) File upload****")

#User prompt to select file type
ft = st.sidebar.selectbox("*What is the file type?*",["Excel", "CSV"])

# Initialize default values for sh (sheet name) and h (header row) 
sh = None
h = 0  # Default header row for CSV; will be overridden for Excel files if needed

#Creating dynamic file upload option in sidebar
uploaded_file = st.sidebar.file_uploader("*Please upload your file here*")

if uploaded_file is not None:
    file_path = uploaded_file

    if ft == 'Excel':
        try:
            #User prompt to select sheet name in uploaded Excel
            sh = st.sidebar.selectbox("*Which sheet name in the file should be read?*", pd.ExcelFile(file_path).sheet_names)
            #User prompt to define row with column names if they aren't in the header row in the uploaded Excel
            h = st.sidebar.number_input("*Which row contains the column names?*", 0, 100, value=0)
        except Exception as e:
            st.info("File is not recognised as an Excel file")
            sys.exit()
    
    elif ft == 'CSV':
        # For CSV files, sh and h remain as their default values (None and 0 respectively)
        pass

    #Caching function to load data
    @st.cache(allow_output_mutation=True)
    def load_data(file_path, file_type, sheet_name, header_row):
        
        if file_type == 'Excel':
            try:
                #Reading the excel file
                return pd.read_excel(file_path, header=header_row, sheet_name=sheet_name, engine='openpyxl')
            except Exception as e:
                st.info("File is not recognised as an Excel file.")
                sys.exit()
    
        elif file_type == 'CSV':
            try:
                #Reading the csv file
                return pd.read_csv(file_path)
            except Exception as e:
                st.info("File is not recognised as a CSV file.")
                sys.exit()
        
        return None  # Add return statement for clarity

    data = load_data(file_path, ft, sh, h)


#=====================================================================================================
## 2. Overview of the data
    st.write( '### 1. Dataset Preview ')

    if data is not None:  # Check if data is loaded properly
        try:
            #View the dataframe in streamlit
            st.dataframe(data, use_container_width=True)

        except Exception as e:
            st.info("The file wasn't read properly. Please ensure that the input parameters are correctly defined.")
            st.write(e)  # Output the actual error for better debugging
            sys.exit()


#=====================================================================================================
## 3. Understanding the data
    st.write( '### 2. High-Level Overview ')

    #Creating radio button and sidebar simultaneously
    selected = st.sidebar.radio("**B) What would you like to know about the data?**", 
                                ["Data Dimensions",
                                 "Field Descriptions",
                                "Summary Statistics", 
                                "Value Counts of Fields"])

    #Showing field types
    if selected == 'Field Descriptions':
        fd = data.dtypes.reset_index().rename(columns={'index': 'Field Name', 0: 'Field Type'}).sort_values(by='Field Type', ascending=False).reset_index(drop=True)
        st.dataframe(fd, use_container_width=True)

    #Showing summary statistics
    elif selected == 'Summary Statistics':
        ss = pd.DataFrame(data.describe(include='all').round(2).fillna(''))
        st.dataframe(ss, use_container_width=True)

    #Showing value counts of object fields
    elif selected == 'Value Counts of Fields':
        # Creating radio button and sidebar simultaneously if this main selection is made
        sub_selected = st.sidebar.radio("*Which field should be investigated?*", data.select_dtypes(include=['object']).columns.tolist())
        vc = data[sub_selected].value_counts().reset_index().rename(columns={'index': 'Value', sub_selected: 'Count'}).reset_index(drop=True)
        st.dataframe(vc, use_container_width=True)

    #Showing the shape of the dataframe
    else:
        st.write('###### The data has the dimensions :', data.shape)


#=====================================================================================================
## 4. Visualisation

    #Selecting whether visualisation is required
    vis_select = st.sidebar.checkbox("**C) Is visualisation required for this dataset?**")

    if vis_select:

        st.write( '### 3. Visual Insights ')

        #Creating a PyGWalker Dashboard
        walker = pyg.walk(data, return_html=True)
        st.components.v1.html(walker, width=1100, height=800)  #Adjust width and height as needed
