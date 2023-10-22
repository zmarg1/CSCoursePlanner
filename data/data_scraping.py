import pandas as pd
import math

# Load the original CSV file (modify the file path as needed)
original_df = pd.read_csv("CSEE_Past_Course_Frequency.csv")

# Create a list of columns representing semester and year
semesters_and_years = original_df.columns[3:]

# Initialize lists to store the data for the new DataFrame
subject_code_list = []
class_number_list = []
term_list = []  # Changed the column name to "term"
year_list = []
frequency_count_list = []

# Iterate through the original DataFrame to transform the data
for _, row in original_df.iterrows():
    subject_code = row[0]  # Assuming subject_code is in the first column
    class_number = row[1]  # Assuming class_number is in the second column
    
    for semester_year, frequency in zip(semesters_and_years, row[3:]):
        if pd.notna(frequency):
            semester, year = semester_year.split()
            year = str(math.floor(float(year)))  # Round down the year to remove decimals
            subject_code_list.append(subject_code)
            class_number_list.append(class_number)
            term_list.append(semester)  # Changed the column name to "term"
            year_list.append(year)
            frequency_count_list.append(frequency)
        else:
            # Append empty values for missing frequencies
            subject_code_list.append(subject_code)
            class_number_list.append(class_number)
            if " " in semester_year:
                semester, year = semester_year.split()
                year = str(math.floor(float(year)))  # Round down the year to remove decimals
                term_list.append(semester)  # Changed the column name to "term"
                year_list.append(year)
            else:
                term_list.append(semester_year)  # Changed the column name to "term"
                year_list.append("")
            frequency_count_list.append("")

# Create a new DataFrame with the transformed data
transformed_df = pd.DataFrame({
    "subject_code": subject_code_list,
    "class_number": class_number_list,
    "term": term_list,  # Changed the column name to "term"
    "year": year_list,
    "frequency_count": frequency_count_list
})

# Write the final transformed data to an Excel file
transformed_df.to_excel("final_transformed_data.xlsx", index=False)