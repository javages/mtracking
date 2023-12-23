import os
from jinja2 import Template

# Directory where the log files are located
log_dir = 'machine_logs'  # Replace with the actual path to your log files directory

# Scan the directory for log files
log_files = [f for f in os.listdir(log_dir) if f.startswith('machine_resources') and f.endswith('.log')]

# Function to extract the number from the log file name, with a default for non-conforming names
def extract_number(file_name):
    parts = file_name.split('machine_resources')
    if len(parts) > 1 and parts[1].split('.log')[0].isdigit():
        return int(parts[1].split('.log')[0])
    return 0  # Default number for 'machine_resources.log' or other non-conforming names

# Sort log files by number
log_files.sort(key=extract_number)

def format_vnstat_data(log_content):
    if "vnStat Data:" in log_content:
        lines = log_content.split('\n')
        table_content = "<table>"
        header_flag = False

        for line in lines:
            if line.strip().lower() in ['monthly', 'daily']:
                # This is a header line
                table_content += f"<tr><th colspan='0'>{line.strip()}</th></tr>"
                header_flag = True
            elif '----' in line or not line.strip():
                # Skip divider lines or empty lines
                continue
            else:
                # Data line
                cells = line.split('\t')
                if header_flag:  # The first data line after a header is another header
                    table_content += "<tr>" + "".join(f"<th>{cell.strip()}</th>" for cell in cells if cell.strip()) + "</tr>"
                    header_flag = False
                else:
                    table_content += "<tr>" + "".join(f"<td>{cell.strip()}</td>" for cell in cells if cell.strip()) + "</tr>"
        
        table_content += "</table>"
        return table_content
    else:
        return f"<pre>{log_content}</pre>"

# Read the content of each log file
log_data = {}
for file_name in log_files:
    with open(os.path.join(log_dir, file_name), 'r') as file:
        log_content = file.read()
        formatted_content = format_vnstat_data(log_content)
        log_data[file_name] = formatted_content

# HTML template with Jinja2 placeholders
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Machine Resources</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: black;
            color: white;
            margin: 0;
            padding: 0;
        }
        .content-container {
            max-width: 800px; /* Maximum width of the content */
            margin: 0 auto; /* Centering */
            padding: 20px; /* Padding around the content */
        }
        .log-container {
            margin-bottom: 20px;
            text-align: left;
        }
        .log-title {
            color: white;
        }
        .log-content table {
            width: 100%;
            table-layout: fixed;
        }
        .log-content th, .log-content td {
            text-align: left;
            padding: 8px;
            border: 1px solid white;
        }
        .log-content th:nth-child(1), .log-content td:nth-child(1) {
            width: 100%;
        }
        .log-content th {
            background-color: #333;
        }
        .log-content td {
            background-color: #555;
        }
    </style>
</head>
<body>
    <div class="content-container">
        {% for name, content in log_data.items() %}
        <div class="log-container">
            <h2 class="log-title">{{ name }}</h2>
            <div class="log-content">{{ content }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>


"""

# Create a Jinja2 template and render it with the log data
template = Template(html_template)
html_content = template.render(log_data=log_data)

# Path for the output HTML file
output_html_path = '/home/josh/jina/mtracking.html'  # Replace with your desired output path

# Write the HTML content to the file
with open(output_html_path, 'w') as file:
    file.write(html_content)

print(f"HTML file generated at: {output_html_path}")

