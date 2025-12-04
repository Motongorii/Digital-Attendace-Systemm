#!/usr/bin/env python
"""Patch session_detail.html template to add semester/lec label and attendance percentage column"""

template_file = r'c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\templates\attendance\session_detail.html'

# Read the current file
with open(template_file, 'r') as f:
    content = f.read()

# Patch 1: Update unit code display to show semester and lec number
old_unit_display = '''                    <div class="unit-code">{{ session.unit.code }}</div>
                    <div class="unit-name">{{ session.unit.name }}</div>'''

new_unit_display = '''                    <div class="unit-code">{{ session.unit.code }}{% if session.session_number %} - S{{ session.semester }} Lec {{ session.session_number }}{% endif %}</div>
                    <div class="unit-name">{{ session.unit.name }}</div>'''

if old_unit_display in content:
    content = content.replace(old_unit_display, new_unit_display)
    print("✓ Patch 1: Unit code display updated")
else:
    print("⚠ Patch 1: Could not find unit display to update")

# Patch 2: Add attendance percentage column header
old_thead = '''                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Student Name</th>
                            <th>Admission No.</th>
                            <th>Time Marked</th>
                        </tr>
                    </thead>'''

new_thead = '''                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Student Name</th>
                            <th>Admission No.</th>
                            <th>Time Marked</th>
                            <th>Attendance %</th>
                        </tr>
                    </thead>'''

if old_thead in content:
    content = content.replace(old_thead, new_thead)
    print("✓ Patch 2: Table header updated with Attendance % column")
else:
    print("⚠ Patch 2: Could not find table header to update")

# Patch 3: Add attendance percentage cell in table body
old_tbody = '''                    <tbody>
                        {% for record in attendance_records %}
                        <tr>
                            <td>{{ forloop.counter }}</td>
                            <td>{{ record.student_name }}</td>
                            <td>{{ record.admission_number }}</td>
                            <td>{{ record.timestamp|slice:":19" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>'''

new_tbody = '''                    <tbody>
                        {% for record in attendance_records %}
                        <tr>
                            <td>{{ forloop.counter }}</td>
                            <td>{{ record.student_name }}</td>
                            <td>{{ record.admission_number }}</td>
                            <td>{{ record.timestamp|slice:":19" }}</td>
                            <td><strong>{{ record.attendance_percentage|floatformat:1 }}%</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>'''

if old_tbody in content:
    content = content.replace(old_tbody, new_tbody)
    print("✓ Patch 3: Table body updated with attendance percentage cell")
else:
    print("⚠ Patch 3: Could not find table body to update")

# Write the patched content
with open(template_file, 'w') as f:
    f.write(content)

print("\n✓ All template patches applied successfully!")
