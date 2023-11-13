import pandas as pd
import math

# Load the original CSV file (modify the file path as needed)
original_df = pd.read_csv("CSEE_Past_Course_Frequency_2.csv")

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
    "course_num": class_number_list,
    "term": term_list,  # Changed the column name to "term"
    "year": year_list,
    "frequency_count": frequency_count_list
})

# Extract the CMSC courses only
transformed_df = transformed_df[transformed_df['subject_code'] == 'CMSC']

# Define the course, subject, and term dataframes as lookup tables
course_df = pd.read_excel("database_tables.xlsx", sheet_name="course")
subject_df = pd.read_excel("database_tables.xlsx", sheet_name="subject")
semester_df = pd.read_excel("database_tables.xlsx", sheet_name="semester")

# Convert "course_num" to string data type
transformed_df["course_num"] = transformed_df["course_num"].astype(str)

# Merge to replace subject_code with subject_id
transformed_df = transformed_df.merge(subject_df, on="subject_code", how="left")

# Drop the subject_code column
transformed_df = transformed_df.drop("subject_code", axis=1)

# Clean the 'course_num' column by stripping white spaces
transformed_df['course_num'] = transformed_df['course_num'].str.strip()

# Convert the 'year' column in the transformed data to int64
transformed_df['year'] = transformed_df['year'].astype('int64')

# Convert the 'year' column in the transformed data to int64
transformed_df['year'] = transformed_df['year'].astype('int64')

# Map terms to numerical values
term_mapping = {'Winter': 1, 'Spring': 2, 'Summer': 3, 'Fall': 4}
transformed_df['term'] = transformed_df['term'].map(term_mapping)

# Remove rows before Fall 2020
fall_2020_index = transformed_df[(transformed_df['year'] > 2020) | ((transformed_df['year'] == 2020) & (transformed_df['term'] >= term_mapping['Fall']))].index
transformed_df = transformed_df.loc[fall_2020_index]

# Reverse map numerical terms back to strings
transformed_df['term'] = transformed_df['term'].map({v: k for k, v in term_mapping.items()})

#transformed_df.to_excel("final_transformed_data.xlsx", index=False)

# Replace "term" and "year" with "semester_id" from the term table
transformed_df = transformed_df.merge(semester_df, left_on=["term", "year"], right_on=["term", "year"], how="left")
transformed_df.drop(columns=["term", "year"], inplace=True)

# Step 3: Ensure data types and merge with the course table
course_df['course_num'] = course_df['course_num'].astype(str)
transformed_df['subject_id'] = transformed_df['subject_id'].astype(int)
course_df['subject_id'] = course_df['subject_id'].astype(int)
course_df['course_id'] = course_df['course_id'].astype(int)

# Merge with the course table on both 'subject_id' and 'course_num'
transformed_df = transformed_df.merge(course_df, on=['subject_id', 'course_num'], how='left')

# Add an "offered_id" column
transformed_df['offered_id'] = range(1, len(transformed_df) + 1)

# Rename the "frequency_count" column to "frequency"
transformed_df.rename(columns={"frequency_count": "frequency"}, inplace=True)

# Reorder the columns
transformed_df = transformed_df[['offered_id', 'course_id', 'semester_id', 'frequency']]

# Write the final transformed data to an Excel file
transformed_df.to_excel("final_transformed_data.xlsx", index=False)