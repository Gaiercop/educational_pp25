import json
import os
def get_user_input():
    filename = input("Enter the filename (excluding extension, it will be added): ")
    name = input()
    description = input("Enter the description: ")
    return filename, name, description
def create_json_data(name, description):

    data = {
        "name": name,
        "description": description
    }
    return data


def write_json_file(directory, filename, data):
    directory = "teory"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.json")
    try:
      with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
      print(f"Successfully created: {filepath}")

    except Exception as e:
      print(f"Error creating {filepath}: {e}")
def main():
    filename, name, description = get_user_input()
    json_data = create_json_data(name, description)
    directory = name.replace(" ", "_")
    write_json_file(directory, filename, json_data)


if __name__ == "__main__":
    main()