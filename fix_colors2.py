content = open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', encoding='utf-8').read()

# Update the main app background to light blue
content = content.replace(
    'background: linear-gradient(180deg, #ffffff 0%, #fbf8f4 100%);',
    'background: linear-gradient(180deg, #E6F3FF 0%, #B8D9FF 100%);'
)
content = content.replace(
    'color: #000000;',
    'color: #1a2935;'
)

open(r'C:\Users\hp\Desktop\FinalYearProject\dropout_app\app.py', 'w', encoding='utf-8').write(content)
print('Done')