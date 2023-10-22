import pandas as pd

def csv_to_excel():
    # Load the original CSV file (modify the file path as needed)
    original_df = pd.read_csv("CSEE_Past_Course_Frequency.csv")

   # Create a list of columns representing semester and year
    semesters_and_years = original_df.columns[3:]

    # Initialize lists to store the data for the new DataFrame
    class_code_list = []
    class_number_list = []
    semester_list = []
    year_list = []
    frequency_count_list = []

    # Iterate through the original DataFrame to transform the data
    for _, row in original_df.iterrows():
        class_code = row[0]  # Assuming class_code is in the first column
        class_number = row[1]  # Assuming class_number is in the second column
        
        for semester_year, frequency in zip(semesters_and_years, row[3:]):
            if pd.notna(frequency):
                semester, year = semester_year.split()
                class_code_list.append(class_code)
                class_number_list.append(class_number)
                semester_list.append(semester)
                year_list.append(year)
                frequency_count_list.append(frequency)
            else:
                # Append empty values for missing frequencies
                class_code_list.append(class_code)
                class_number_list.append(class_number)
                semester_list.append(semester_year)
                year_list.append("")
                frequency_count_list.append("")

    # Create a new DataFrame with the transformed data
    new_df = pd.DataFrame({
        "class_code": class_code_list,
        "class_number": class_number_list,
        "semester": semester_list,
        "year": year_list,
        "frequency_count": frequency_count_list
    })

    # Write the new DataFrame to an Excel file
    new_df.to_excel("transformed_data.xlsx", index=False)
if __name__ == "__main__":
    csv_to_excel()
