content = open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', encoding='utf-8').read()

# Update color values
content = content.replace('SDPS_DARK_SURFACE = "#111827"', 'SDPS_DARK_SURFACE = "#1E3F66"')
content = content.replace('SDPS_DARK_SURFACE_2 = "#1F2937"', 'SDPS_DARK_SURFACE_2 = "#2A4A75"')

open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', 'w', encoding='utf-8').write(content)
print('Done')