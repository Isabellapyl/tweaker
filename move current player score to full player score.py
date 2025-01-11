import pandas as pd

# Define the file paths
file1_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\player_balance.csv"
file2_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\all_players.csv"
output_path = r"C:\Users\Isabella.Pijl\learn\Casino Summative\all_players.csv"

try:
    # Read the contents of file1 and file2
    df1 = pd.read_csv(file1_path, header=None)  # Load file1 exactly as is, without assigning headers
    df2 = pd.read_csv(file2_path, header=None)  # Load file2 exactly as is, without assigning headers

    # Combine both DataFrames
    updated_df = pd.concat([df2, df1], ignore_index=True)

    # Save the updated content back to the file2 path
    updated_df.to_csv(output_path, index=False, header=False)

    # Display the updated DataFrame for verification
    print(updated_df)

except FileNotFoundError as e:
    print(f"Error: {e}. Please check the file path.")
except Exception as e:
    print(f"An unexpected error occurred: {e}.")
