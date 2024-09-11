import subprocess
import threading
import os
import glob


def fill_template(template_file, resume_sections, new_file):
    with open(template_file, 'r') as file:
        template_content = file.read()

    index_exp = 1
    index_project = 1
    index_pub = 1
    for resume in resume_sections:
        print(resume.type, resume.company, resume.role, resume.description, resume.date)
        if resume.type == 'Experience':
            template_content = template_content.replace('ReplaceExperienceDate' + str(index_exp), resume.date)
            template_content = template_content.replace('ReplaceExperienceRole' + str(index_exp), resume.role)
            template_content = template_content.replace('ReplaceExperienceCompany' + str(index_exp), resume.company)
            template_content = template_content.replace('ReplaceExperienceLocation' + str(index_exp), '')
            template_content = template_content.replace('ReplaceExperienceItems' + str(index_exp), resume.description)
            index_exp += 1
        if resume.type == 'Projects':
            template_content = template_content.replace('ReplaceProjectRole' + str(index_project), resume.role)
            template_content = template_content.replace('ReplaceProjectItems' + str(index_project), resume.description)
            index_project += 1

        if resume.type == 'Publications':
            template_content = template_content.replace('ReplacePublicationRole' + str(index_pub), resume.role)
            template_content = template_content.replace('ReplacePublicationItems' + str(index_pub), resume.description)
            index_pub += 1

    # Write the final content to a new .tex file
    with open(new_file, 'w') as file:
        file.write(template_content)
    print("LaTeX file generated successfully!")

    run_pdftex(new_file, new_file.split('.')[0], 'Rigved_Manoj_Resume')
    print("pdf file generated successfully!")


def rename_file(current_name, new_name):
    try:
        os.rename(current_name, new_name)
    except FileNotFoundError:
        print(f"The file {current_name} does not exist.")
    except PermissionError:
        print(f"Permission denied: cannot rename {current_name}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def send_input_every_second(process):
    try:
        while process.poll() is None:  # Check if the process is still running
            process.stdin.write('\n')
            process.stdin.flush()
    except Exception as e:
        print(f"An error occurred in the input thread: {e}")


def run_pdftex(tex_file, old_file_name, file_name):
    # Open a subprocess to run pdftex
    process = subprocess.Popen(
        ['pdflatex', tex_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Start a thread to send input every second
    input_thread = threading.Thread(target=send_input_every_second, args=(process,))
    input_thread.start()

    try:
        # Read and print the process output
        while True:
            output = process.stdout.read(1)
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output, end='')

        # Wait for the input thread to finish
        input_thread.join()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if os.path.exists(file_name + '.pdf'):
            os.remove(file_name + '.pdf')
        if os.path.exists(file_name + '.tex'):
            os.remove(file_name + '.tex')
        rename_file(old_file_name + '.pdf', file_name + '.pdf')
        rename_file(old_file_name + '.tex', file_name + '.tex')
        pattern = os.path.join('', old_file_name + '*')
        files = glob.glob(pattern)
        for file in files:
            os.remove(file)

