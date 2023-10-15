import subprocess
import os

def main():
    subprocess.run(['python3', 'csvDownload.py'])
    subprocess.run(['python3', 'pydantic_LPF.py'])
    #print("Skipping python scripts")

    data_output_size = os.path.getsize('data_output.csv') / (1024 * 1024)  # size in MB
    linked_places_output_size = os.path.getsize('linked_places_output.json') / (1024 * 1024)  # size in MB
    total_size = (linked_places_output_size)
    print()
    print(f'{data_output_size:.2f} MB turned into {total_size:.2f}')
    print(f'data_output.csv size:       {data_output_size:.2f} MB')
    print(f'linked_places_output.json size:     {linked_places_output_size:.2f} MB')

if __name__ == "__main__":
    main()
