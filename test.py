import requests
import sys

def update_script():
    # URL of the Python file on GitHub
    github_url = "https://raw.githubusercontent.com/username/repository/master/script.py"

    try:
        # Fetch the code from GitHub
        response = requests.get(github_url)
        response.raise_for_status()  # Raise an exception for non-successful response codes
        new_code = response.text

        # Overwrite the current script with the code from GitHub
        with open(sys.argv[0], "w") as script_file:
            script_file.write(new_code)

        print("Script updated successfully!")
    except requests.exceptions.RequestException as e:
        print("Failed to update the script:", str(e))
    except IOError as e:
        print("Failed to write to the script file:", str(e))

if __name__ == "__main__":
    update_script()
