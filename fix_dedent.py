content = open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', encoding='utf-8').read()

# Find and fix the render_ui_css function
lines = content.split('\n')
output = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check if this is the def line
    if line.strip() == 'def render_ui_css(dark_mode: bool = True):':
        # Add the function definition with proper indentation
        output.append(line)
        i += 1
        # Now add the fixed body with proper 4-space indentation
        output.append('    if dark_mode:')
        output.append('        css_vars = f"""')
        output.append('        :root {{')
        output.append('            --sdps-bg: #0a1e35;')
        output.append('            --sdps-bg-2: #112440;')
        output.append('            --sdps-surface: {SDPS_DARK_SURFACE};')
        output.append('            --sdps-surface-2: {SDPS_DARK_SURFACE_2};')
        output.append('            --sdps-text: {SDPS_DARK_TEXT};')
        output.append('            --sdps-muted: {SDPS_DARK_MUTED};')
        output.append('            --sdps-border: {SDPS_DARK_BORDER};')
        output.append('            --sdps-input: #112440;')
        output.append('            --sdps-primary: {SDPS_PRIMARY};')
        output.append('            --sdps-secondary: {SDPS_SECONDARY};')
        output.append('            --sdps-accent: {SDPS_ACCENT};')
        output.append('            --sdps-danger: #ef4444;')
        output.append('            --sdps-warning: #f59e0b;')
        output.append('            --sdps-success: #10b981;')
        output.append('            --sdps-card-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);')
        output.append('        }}')
        output.append('        """')
        output.append('    else:')
        i += 1  # Skip the corrupted line
        while i < len(lines):
            next_line = lines[i]
            # Continue until we find the st.markdown line
            if 'st.markdown(f"""' in next_line or '.markdown(f\"\"\"' in next_line:
                output.append('        ' + next_line.lstrip())
                i += 1
                break
            i += 1
    else:
        output.append(line)
    i += 1

# Write back
open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', 'w', encoding='utf-8').write('\n'.join(output))
print('Done')